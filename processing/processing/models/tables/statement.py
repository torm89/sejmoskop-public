from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from processing.models.tables import Base


class Statement(Base):
    __tablename__ = "statements"

    date: Mapped[str] = mapped_column()
    description_01: Mapped[str] = mapped_column()
    description_02: Mapped[str] = mapped_column()
    title_01: Mapped[str] = mapped_column()
    title_02: Mapped[str] = mapped_column()
    session_id: Mapped[str] = mapped_column()
    date_id: Mapped[str] = mapped_column()
    statement_id: Mapped[str] = mapped_column()
    statement_id_new: Mapped[str] = mapped_column()
    video_url: Mapped[str] = mapped_column()

    chamber_name: Mapped[str] = mapped_column()
    term_id: Mapped[str] = mapped_column()

    __table_args__ = (
        PrimaryKeyConstraint("chamber_name", "term_id", "statement_id"),
    )

    def __repr__(self) -> str:
        return f"Statement(chamber_name={self.chamber_name!r}, term_id={self.term_id!r}, session_id={self.session_id!r}, statement_id={self.statement_id!r}, statement_id_new={self.statement_id_new!r})"

