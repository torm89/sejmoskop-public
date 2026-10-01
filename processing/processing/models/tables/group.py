from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from processing.models.tables import Base


class Group(Base):
    __tablename__ = "groups"

    name: Mapped[str]
    name_short: Mapped[str] = mapped_column(primary_key=True)
    group_type: Mapped[str] = mapped_column()

    chamber_name: Mapped[str] = mapped_column(primary_key=True)
    term_id: Mapped[str] = mapped_column(primary_key=True)

    votings_outcomes = relationship("VotingOutcome", back_populates="group", viewonly=True)

    __table_args__ = (
        PrimaryKeyConstraint("chamber_name", "term_id", "name_short"),
    )

    def __repr__(self) -> str:
        return f"Group(chamber_name={self.chamber_name!r}, term_id={self.term_id!r}, name_short={self.name_short!r}, name={self.name!r}, group_type={self.group_type!r})"
