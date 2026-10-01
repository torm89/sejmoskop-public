from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from processing.models.tables import Base
from processing.models.tables.group import Group
from processing.models.tables.member import Member
from processing.models.tags import VotingType


class Voting(Base):
    __tablename__ = "votings"

    chamber_name: Mapped[str] = mapped_column()
    term_id: Mapped[str] = mapped_column()

    session_id: Mapped[str] = mapped_column()
    voting_id: Mapped[str] = mapped_column()

    voting_type: Mapped[str] = mapped_column()  # TODO: Use Enum

    datetime: Mapped[str] = mapped_column()

    description_01: Mapped[str] = mapped_column()
    description_02: Mapped[str] = mapped_column()

    outcomes = relationship("VotingOutcome", back_populates="voting", viewonly=True)

    __mapper_args__ = {
        "polymorphic_identity": "voting",
        "polymorphic_on": "voting_type",
    }

    __table_args__ = (
        PrimaryKeyConstraint("chamber_name", "term_id", "session_id", "voting_id"),
    )

    def __repr__(self) -> str:
        return f"Voting(chamber_name={self.chamber_name!r}, term_id={self.term_id!r}, session_id={self.session_id!r}, voting_id={self.voting_id!r}, voting_type={self.voting_type!r})"


class VotingNormal(Voting):
    outcomes = relationship("VotingOutcomeNormal", back_populates="voting", viewonly=True)

    __mapper_args__ = {
        "polymorphic_identity": VotingType.NORMAL.value
    }

    def __repr__(self) -> str:
        return f"VotingNormal(chamber_name={self.chamber_name!r}, term_id={self.term_id!r}, session_id={self.session_id!r}, voting_id={self.voting_id!r})"


class VotingList(Voting):
    outcomes = relationship("VotingOutcomeList", back_populates="voting", viewonly=True)

    __mapper_args__ = {
        "polymorphic_identity": VotingType.LIST.value
    }

    def __repr__(self) -> str:
        return f"VotingNormal(chamber_name={self.chamber_name!r}, term_id={self.term_id!r}, session_id={self.session_id!r}, voting_id={self.voting_id!r})"


class VotingOutcome(Base):
    __tablename__ = "votings-outcomes"

    chamber_name: Mapped[str] = mapped_column()
    term_id: Mapped[str] = mapped_column()

    session_id: Mapped[str] = mapped_column()
    voting_id: Mapped[str] = mapped_column()
    voting_type: Mapped[str] = mapped_column()  # TODO: Use Enum

    member_name: Mapped[str] = mapped_column()
    member_id: Mapped[str] = mapped_column()
    group_name_short: Mapped[str] = mapped_column()

    call: Mapped[str] = mapped_column()

    member = relationship(
        "Member", back_populates="votings_outcomes", foreign_keys=[chamber_name, term_id, member_name], viewonly=True)
    voting = relationship(
        "Voting", back_populates="outcomes", foreign_keys=[chamber_name, term_id, session_id, voting_id],
        viewonly=True
    )
    group = relationship(
        "Group", back_populates="votings_outcomes", foreign_keys=[chamber_name, term_id, group_name_short],
        viewonly=True
    )

    __mapper_args__ = {
        "polymorphic_identity": "voting_outcome",
        "polymorphic_on": "voting_type",
    }

    __table_args__ = (
        PrimaryKeyConstraint("chamber_name", "term_id", "session_id", "voting_id", "member_name"),
        ForeignKeyConstraint(
            [chamber_name, term_id, member_name],
            [Member.chamber_name, Member.term_id, Member.voting_name]
        ),
        ForeignKeyConstraint(
            [chamber_name, term_id, session_id, voting_id],
            [Voting.chamber_name, Voting.term_id, Voting.session_id, Voting.voting_id],
        ),
        ForeignKeyConstraint(
            [chamber_name, term_id, group_name_short],
            [Group.chamber_name, Group.term_id, Group.name_short],
        ),
    )


class VotingOutcomeNormal(VotingOutcome):
    voting = relationship(
        "VotingNormal",
        back_populates="outcomes",
        foreign_keys=[
            VotingOutcome.chamber_name, VotingOutcome.term_id, VotingOutcome.session_id, VotingOutcome.voting_id
        ],
        viewonly=True
    )

    __mapper_args__ = {
        "polymorphic_identity": VotingType.NORMAL.value,
    }

    def __repr__(self) -> str:
        return f"VotingOutcomeNormal(chamber_name={self.chamber_name!r}, term_id={self.term_id!r}, session_id={self.session_id!r}, voting_id={self.voting_id!r}, member_name={self.member_name!r}, group_name_short={self.group_name_short!r})"


class VotingOutcomeList(VotingOutcome):
    voting = relationship(
        "VotingList",
        back_populates="outcomes",
        foreign_keys=[
            VotingOutcome.chamber_name, VotingOutcome.term_id, VotingOutcome.session_id, VotingOutcome.voting_id
        ],
        viewonly=True
    )

    __mapper_args__ = {
        "polymorphic_identity": VotingType.LIST.value,
    }

    def __repr__(self) -> str:
        return f"VotingOutcomeList(chamber_name={self.chamber_name!r}, term_id={self.term_id!r}, session_id={self.session_id!r}, voting_id={self.voting_id!r}, member_name={self.member_name!r}), group_name_short={self.group_name_short!r})"
