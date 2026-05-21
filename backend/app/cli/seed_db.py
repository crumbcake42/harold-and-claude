"""seed_db -- load redacted CSVs into the database through the Command pipeline.

Dev tooling, parallel to bootstrap_admin (and distinct from M8's production
spreadsheet import). It pairs with redact_csv.py: real data -> redacted CSV
-> seed folder -> seed_db.

Design (settled at the M1.2 Case 2 sizing + Step 2.2a):

  - **Through the pipeline.** Each CSV row is dispatched as a `create_*`
    Command, not INSERTed directly -- so seeded data is real: invariants
    run, audit-log rows are written, the every-state-change-is-a-Command
    rule keeps its single exception (login). A Caller exists post-bootstrap;
    seed_db runs as the superadmin bootstrap_admin created.

  - **CSV -> Payload.** One CSV per entity, header columns named for the
    command Payload's fields. A JSONB-collection column cannot sit in a
    flat CSV, so it gets a sidecar: Contract's code_flat_fee_schedule is
    `contract_code_fees.csv` (contract_number, code_type, fee), joined by
    contract_number before dispatch.

  - **Idempotency.** Skip-existing, keyed on the entity's natural key
    (contract_number). A row whose key is already present is skipped; a
    clean slate is "drop the DB + migrate", not a wipe-and-reload through
    the Command surface (which would pile audit-log rows up every run).

  - **Folder.** Default `app/cli/seeds/` (colocated -- the script resolves
    `./seeds` relative to itself), gitignored CSVs, committed README.
    Override with --seed-dir.

  - **Ordering.** SEED_ORDER is a hand-maintained topological list; later
    entity-adding sub-steps (2.2b, M1.3, ...) append to it.

argparse, not Click -- per ADR-0061's deferral (Click waits for a unified
app.cli subcommand group).

Usage:
    uv run python -m app.cli.seed_db [--seed-dir PATH]
"""

import argparse
import csv
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path

from pydantic import BaseModel
from sqlalchemy.orm import Session, sessionmaker

from app.adapters.db import SessionFactory
from app.domain.auth import User, UserRole
from app.domain.commands.contract import CodeFlatFee, CreateContract
from app.domain.contract import Contract
from app.framework.caller import Caller, Role
from app.framework.command import Command
from app.framework.dispatcher import Dispatcher
from app.framework.runtime import build_dispatcher

DEFAULT_SEED_DIR = Path(__file__).resolve().parent / "seeds"


# ---- CSV helpers ----


def _read_csv(path: Path) -> list[dict[str, str]]:
    """Read a CSV into a list of header-keyed row dicts. Empty file or
    missing file -> empty list (a missing CSV means 'nothing to seed')."""
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _blank_to_none(value: str | None) -> str | None:
    """An empty CSV cell is the absence of an optional value."""
    return value if value else None


def _optional_date(value: str | None) -> date | None:
    text = _blank_to_none(value)
    return date.fromisoformat(text) if text is not None else None


# ---- Per-entity payload loaders ----


def _load_contract_payloads(seed_dir: Path) -> list[BaseModel]:
    """Build CreateContract payloads from contract.csv, joining the
    code_flat_fee_schedule sidecar by contract_number."""
    fees_by_number: dict[str, list[CodeFlatFee]] = {}
    for row in _read_csv(seed_dir / "contract_code_fees.csv"):
        fees_by_number.setdefault(row["contract_number"], []).append(
            CodeFlatFee(code_type=row["code_type"], fee=Decimal(row["fee"]))
        )

    payloads: list[BaseModel] = []
    for row in _read_csv(seed_dir / "contract.csv"):
        number = row["contract_number"]
        payloads.append(
            CreateContract.Payload(
                contract_number=number,
                name=_blank_to_none(row.get("name")),
                start_date=date.fromisoformat(row["start_date"]),
                end_date=_optional_date(row.get("end_date")),
                code_flat_fee_schedule=fees_by_number.get(number, []),
            )
        )
    return payloads


# ---- Seed registry ----


@dataclass(frozen=True)
class SeedSpec:
    """One entity's seed wiring. `natural_key` names the field on both the
    Payload and the entity used for skip-existing."""

    name: str
    command: type[Command]
    entity_model: type
    natural_key: str
    load_payloads: Callable[[Path], list[BaseModel]]


# Dependency order: independent entities first. 2.2b appends Employee /
# School / Contractor / User; M1.3+ appends further entities.
SEED_ORDER: list[SeedSpec] = [
    SeedSpec(
        name="Contract",
        command=CreateContract,
        entity_model=Contract,
        natural_key="contract_number",
        load_payloads=_load_contract_payloads,
    ),
]


@dataclass
class SeedResult:
    created: int
    skipped: int


# ---- Seeding ----


def _seed_one(
    spec: SeedSpec,
    dispatcher: Dispatcher,
    session_factory: sessionmaker[Session],
    caller: Caller,
    seed_dir: Path,
) -> SeedResult:
    payloads = spec.load_payloads(seed_dir)
    with session_factory() as session:
        existing = {
            key
            for (key,) in session.query(
                getattr(spec.entity_model, spec.natural_key)
            ).all()
        }
    result = SeedResult(created=0, skipped=0)
    for payload in payloads:
        if getattr(payload, spec.natural_key) in existing:
            result.skipped += 1
            continue
        dispatcher.dispatch(spec.command, payload, caller)
        result.created += 1
    return result


def run_seed(
    *,
    dispatcher: Dispatcher,
    session_factory: sessionmaker[Session],
    caller: Caller,
    seed_dir: Path,
) -> dict[str, SeedResult]:
    """Seed every entity in SEED_ORDER. The testable core -- main() wires
    the production dispatcher + caller and calls this."""
    return {
        spec.name: _seed_one(spec, dispatcher, session_factory, caller, seed_dir)
        for spec in SEED_ORDER
    }


def _resolve_seed_caller() -> Caller | None:
    """Build a Caller from the bootstrap superadmin. seed_db dispatches
    create_* commands, which need role >= admin; the superadmin
    bootstrap_admin created satisfies that."""
    with SessionFactory() as session:
        grant = (
            session.query(UserRole)
            .filter(UserRole.role == Role.SUPERADMIN.value)
            .first()
        )
        if grant is None:
            return None
        user = session.get(User, grant.user_id)
        if user is None:
            return None
        role_rows = (
            session.query(UserRole).filter(UserRole.user_id == user.id).all()
        )
        return Caller(
            id=user.id,
            username=user.username,
            roles=frozenset(Role(row.role) for row in role_rows),
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed the database from CSVs.")
    parser.add_argument(
        "--seed-dir",
        type=Path,
        default=DEFAULT_SEED_DIR,
        help=f"Directory holding the seed CSVs (default: {DEFAULT_SEED_DIR}).",
    )
    args = parser.parse_args()

    caller = _resolve_seed_caller()
    if caller is None:
        print(
            "no superadmin found -- run `uv run python -m app.cli.bootstrap_admin` first",
            file=sys.stderr,
        )
        return 1

    results = run_seed(
        dispatcher=build_dispatcher(),
        session_factory=SessionFactory,
        caller=caller,
        seed_dir=args.seed_dir,
    )
    for name, result in results.items():
        print(f"{name}: {result.created} created, {result.skipped} skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
