"""Read-API pagination contract (ADR-0078).

Roster read routes paginate with a uniform contract. The **wire** idiom is
page-based -- `page` / `page_size` query params and a `Page[T]` response
envelope echoing them -- which is what the generated frontend client and
the DataTable consume. The **internal** idiom is `limit` / `offset`, which
maps 1:1 to SQL. `PaginationParams` is the single seam converting the
page-based wire input to offset-based slicing; nothing downstream of it
sees `page`. This mirrors the route-DTO-vs-command-`Payload` separation
ADR-0070 already draws -- the wire speaks the frontend-friendly idiom, the
internals speak the standard one.

Transport-layer and domain-agnostic: it lives in `app/http/` (cross-cutting
FastAPI code, ADR-0079) -- `PaginationParams` reads `fastapi.Query`, and a
`Page[T]` envelope is a read-API wire shape, neither of which belongs in the
write-side command engine. Every feature slice's read routes import `Page`,
`PaginationParams`, and `paginate` from here. Contract's
`GET /contracts` is a deliberate exemption -- it holds a handful of rows
growing ~1 every few years, so it is left on its bare-array shape
(ADR-0078).
"""

from typing import Annotated

from fastapi import Query
from pydantic import BaseModel
from sqlalchemy.orm import Query as DbQuery

# Wire defaults / bounds. page_size is capped to keep an unbounded scan off
# the table; an over-cap page_size or a page < 1 is a 422 (FastAPI-enforced
# via Query() below), not a silent clamp.
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200


class Page[T](BaseModel):
    """The wrapped read-response envelope. `total` is the unpaginated row
    count; `page` / `page_size` echo the request so the client renders a
    pager without a second round-trip.
    """

    items: list[T]
    total: int
    page: int
    page_size: int


class PaginationParams:
    """FastAPI dependency: reads the page-based wire params and exposes the
    offset-based `limit` / `offset` the query layer consumes. The page->offset
    conversion is the wire/internal seam -- nothing past this object sees
    `page`.
    """

    def __init__(
        self,
        page: Annotated[int, Query(ge=1)] = 1,
        page_size: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    ) -> None:
        self.page = page
        self.page_size = page_size

    @property
    def limit(self) -> int:
        return self.page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def paginate[T](query: DbQuery[T], params: PaginationParams) -> tuple[list[T], int]:
    """Run `query` paginated: return the page's rows plus the total
    unpaginated count. The total is a second query -- cheap at roster scale;
    revisit if a high-cardinality table ever consumes this.
    """
    total = query.count()
    rows = query.limit(params.limit).offset(params.offset).all()
    return rows, total
