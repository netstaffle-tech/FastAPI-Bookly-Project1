from sqlalchemy.orm import Mapped, mapped_column
from src.db.main import Base
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime, date
import uuid

class Book(Base):
    __tablename__ = "books"

    uid: Mapped[uuid.UUID] = mapped_column(
        pg.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    title: Mapped[str] = mapped_column(nullable=False)
    author: Mapped[str] = mapped_column(nullable=False)
    publisher: Mapped[str] = mapped_column(nullable=False)
    published_date: Mapped[date] = mapped_column(nullable=False)
    page_count: Mapped[int] = mapped_column(nullable=False)
    language: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        pg.TIMESTAMP(timezone=True),
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        pg.TIMESTAMP(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<Book {self.title}>"

