"""Tests for the seed_db framework -- run_seed loading Contract CSVs
through the Command pipeline, with skip-existing idempotency."""

import csv
from collections.abc import Sequence
from pathlib import Path
from uuid import uuid4

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.adapters.db import Base
from app.cli.seed_db import run_seed
from app.domain.contract import Contract
from app.framework.caller import Caller, Role
from app.framework.runtime import build_dispatcher

SEEDER = Caller(id=uuid4(), username="seed", roles=frozenset({Role.SUPERADMIN}))


def _write_csv(path: Path, header: list[str], rows: Sequence[Sequence[str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def _write_contract_csvs(seed_dir: Path) -> None:
    _write_csv(
        seed_dir / "contract.csv",
        ["contract_number", "name", "start_date", "end_date"],
        [
            ["SCA-1", "First Contract", "2026-01-01", "2026-12-31"],
            ["SCA-2", "", "2026-02-01", ""],
        ],
    )
    _write_csv(
        seed_dir / "contract_code_fees.csv",
        ["contract_number", "code_type", "fee"],
        [
            ["SCA-1", "ACP7", "1200.00"],
            ["SCA-1", "ACP8", "900"],
        ],
    )


def test_run_seed_creates_contracts(
    tmp_path: Path,
    sqlite_engine: Engine,
    sqlite_session_factory: sessionmaker[Session],
) -> None:
    Base.metadata.create_all(sqlite_engine)
    _write_contract_csvs(tmp_path)

    results = run_seed(
        dispatcher=build_dispatcher(sqlite_session_factory),
        session_factory=sqlite_session_factory,
        caller=SEEDER,
        seed_dir=tmp_path,
    )

    assert results["Contract"].created == 2
    assert results["Contract"].skipped == 0

    with sqlite_session_factory() as session:
        rows = session.query(Contract).order_by(Contract.contract_number).all()
        assert [r.contract_number for r in rows] == ["SCA-1", "SCA-2"]
        # sidecar joined onto SCA-1
        assert rows[0].code_flat_fee_schedule == [
            {"code_type": "ACP7", "fee": "1200.00"},
            {"code_type": "ACP8", "fee": "900"},
        ]
        # empty CSV cells -> None / open-ended; no sidecar rows -> empty schedule
        assert rows[1].name is None
        assert rows[1].end_date is None
        assert rows[1].code_flat_fee_schedule == []


def test_run_seed_is_idempotent(
    tmp_path: Path,
    sqlite_engine: Engine,
    sqlite_session_factory: sessionmaker[Session],
) -> None:
    Base.metadata.create_all(sqlite_engine)
    _write_contract_csvs(tmp_path)
    dispatcher = build_dispatcher(sqlite_session_factory)

    run_seed(
        dispatcher=dispatcher,
        session_factory=sqlite_session_factory,
        caller=SEEDER,
        seed_dir=tmp_path,
    )
    second = run_seed(
        dispatcher=dispatcher,
        session_factory=sqlite_session_factory,
        caller=SEEDER,
        seed_dir=tmp_path,
    )

    assert second["Contract"].created == 0
    assert second["Contract"].skipped == 2
    with sqlite_session_factory() as session:
        assert session.query(Contract).count() == 2  # no duplicates


def test_run_seed_missing_csv_is_a_noop(
    tmp_path: Path,
    sqlite_engine: Engine,
    sqlite_session_factory: sessionmaker[Session],
) -> None:
    Base.metadata.create_all(sqlite_engine)
    # tmp_path has no CSVs -- nothing to seed.
    results = run_seed(
        dispatcher=build_dispatcher(sqlite_session_factory),
        session_factory=sqlite_session_factory,
        caller=SEEDER,
        seed_dir=tmp_path,
    )
    assert results["Contract"].created == 0
    assert results["Contract"].skipped == 0
