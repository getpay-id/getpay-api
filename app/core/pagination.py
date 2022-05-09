from typing import Any, Optional, Sequence

from motor.core import AgnosticCollection

from app.core.models import Page
from app.core.utils import serialize_data


async def paginate(
    collection: AgnosticCollection,
    page: int,
    size: int,
    *,
    query_filter: Optional[dict] = None,
    sort_field: Optional[Sequence] = [],
    **kwargs: Any,
) -> Page:
    offset = (page - 1) * size
    query_filter = query_filter or {}
    total = await collection.count_documents(query_filter)
    cursor = collection.find(query_filter, skip=offset, limit=size, **kwargs).sort(
        *sort_field
    )
    items = [i async for i in cursor]
    data = serialize_data(items)
    return Page(total=total, data=data)
