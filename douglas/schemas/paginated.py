from douglas.schemas import BaseModel


class Paginated[T](BaseModel):
    page: int
    page_size: int
    total_pages: int
    items: list[T]
