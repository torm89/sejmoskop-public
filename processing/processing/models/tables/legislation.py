from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from processing.models.tables import Base
from processing.models.tables.voting import Voting


class Legislation(Base):
    __tablename__ = "legislation"

    chamber_name: Mapped[str] = mapped_column()
    term_id: Mapped[str] = mapped_column()

    legislation_number: Mapped[str] = mapped_column()

    title: Mapped[str] = mapped_column()
    document_type: Mapped[str] = mapped_column()
    passed: Mapped[str] = mapped_column()
    process_start_date: Mapped[str] = mapped_column()
    change_date: Mapped[str] = mapped_column()
    closure_date: Mapped[str] = mapped_column()

    __table_args__ = (
        PrimaryKeyConstraint("chamber_name", "term_id", "legislation_number"),
    )

    def __repr__(self) -> str:
        return f"Legislation(chamber_name={self.chamber_name!r}, term_id={self.term_id!r}, legislation_number={self.legislation_number!r}, document_type={self.document_type!r})"


class LegislationStage(Base):
    __tablename__ = "legislation-stages"

    chamber_name: Mapped[str] = mapped_column()
    term_id: Mapped[str] = mapped_column()
    legislation_number: Mapped[str] = mapped_column()

    stage_index: Mapped[str] = mapped_column()

    stage_name: Mapped[str] = mapped_column()
    stage_type: Mapped[str] = mapped_column()
    date: Mapped[str] = mapped_column()
    decision: Mapped[str] = mapped_column()
    print_numbers: Mapped[str] = mapped_column()

    __table_args__ = (
        PrimaryKeyConstraint("chamber_name", "term_id", "legislation_number", "stage_index"),
        ForeignKeyConstraint(
            [chamber_name, term_id, legislation_number],
            [Legislation.chamber_name, Legislation.term_id, Legislation.legislation_number],
        ),
    )

    def __repr__(self) -> str:
        return f"LegislationStage(chamber_name={self.chamber_name!r}, term_id={self.term_id!r}, legislation_number={self.legislation_number!r}, stage_index={self.stage_index!r}, stage_type={self.stage_type!r})"


class LegislationVoting(Base):
    __tablename__ = "legislation-votings"

    chamber_name: Mapped[str] = mapped_column()
    term_id: Mapped[str] = mapped_column()
    legislation_number: Mapped[str] = mapped_column()
    stage_index: Mapped[str] = mapped_column()

    session_id: Mapped[str] = mapped_column()
    voting_id: Mapped[str] = mapped_column()

    __table_args__ = (
        PrimaryKeyConstraint(
            "chamber_name", "term_id", "legislation_number", "stage_index", "session_id", "voting_id"
        ),
        ForeignKeyConstraint(
            [chamber_name, term_id, legislation_number],
            [Legislation.chamber_name, Legislation.term_id, Legislation.legislation_number],
        ),
        ForeignKeyConstraint(
            [chamber_name, term_id, session_id, voting_id],
            [Voting.chamber_name, Voting.term_id, Voting.session_id, Voting.voting_id],
        ),
    )

    def __repr__(self) -> str:
        return f"LegislationVoting(chamber_name={self.chamber_name!r}, term_id={self.term_id!r}, legislation_number={self.legislation_number!r}, stage_index={self.stage_index!r}, session_id={self.session_id!r}, voting_id={self.voting_id!r})"
