from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from processing.models.tables import Base


class Member(Base):
    __tablename__ = "members"

    member_id: Mapped[str] = mapped_column()
    first_name: Mapped[str] = mapped_column()
    second_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    member_type: Mapped[str] = mapped_column()
    voting_name: Mapped[str] = mapped_column()
    birth_date: Mapped[str] = mapped_column()
    former_details: Mapped[str] = mapped_column()
    country: Mapped[str] = mapped_column()

    chamber_name: Mapped[str] = mapped_column()
    term_id: Mapped[str] = mapped_column()

    votings_outcomes = relationship("VotingOutcome", back_populates="member", viewonly=True)

    __table_args__ = (
        PrimaryKeyConstraint("chamber_name", "term_id", "member_id"),
    )

    def __repr__(self) -> str:
        return f"Member(chamber_name={self.chamber_name!r}, term_id={self.term_id!r}, id={self.member_id!r}, first_name={self.first_name!r}, fullname={self.second_name!r}, last_name={self.last_name!r})"
