"""Pagination contract unit tests (ADR-0078).

`PaginationParams`' page->offset conversion. The wire-bound validation
(`page >= 1`, `page_size` in `[1, 200]`) is FastAPI-enforced via `Query()`
and is exercised through the per-entity route tests; `paginate()`'s
slicing + total count is likewise exercised end-to-end there.
"""

from app.engine.pagination import (
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    Page,
    PaginationParams,
)


def test_defaults_are_page_one_default_size() -> None:
    params = PaginationParams()
    assert params.page == 1
    assert params.page_size == DEFAULT_PAGE_SIZE
    assert params.limit == DEFAULT_PAGE_SIZE
    assert params.offset == 0


def test_offset_is_zero_based_from_page() -> None:
    assert PaginationParams(page=1, page_size=20).offset == 0
    assert PaginationParams(page=2, page_size=20).offset == 20
    assert PaginationParams(page=5, page_size=50).offset == 200


def test_limit_is_page_size() -> None:
    assert PaginationParams(page=3, page_size=25).limit == 25
    assert PaginationParams(page=2, page_size=MAX_PAGE_SIZE).limit == MAX_PAGE_SIZE


def test_page_envelope_shape() -> None:
    page: Page[int] = Page(items=[1, 2, 3], total=10, page=2, page_size=3)
    assert page.model_dump() == {
        "items": [1, 2, 3],
        "total": 10,
        "page": 2,
        "page_size": 3,
    }
