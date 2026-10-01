from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel, Field, Extra, model_validator


class VotingType(str, Enum):
    NORMAL = "normal"
    LIST = "list"
    TRADITIONAL = "traditional"
    DIFFERENT = "different"
    QUORUM = "quorum"
    UNKNOWN = "unknown"


class VotingOutcomeCall(str, Enum):
    yea = "yea"
    nay = "nay"
    abstain = "abstain"
    no_voted = "no_voted"


class TermTag(BaseModel, extra=Extra.ignore):
    chamber_name: str = Field(alias='chamberName')
    term_id: str = Field(alias='termId')

    class Config:
        frozen = True


class SessionTag(TermTag):
    session_id: str = Field(alias='sessionId')


class VotingTag(SessionTag):
    voting_id: str = Field(alias='votingId')
    voting_type: Optional[str] = Field(alias='votingType', default=None)

    date: Optional[str] = Field(alias='date', default=None)

    def __hash__(self):
        return hash((self.chamber_name, self.term_id, self.session_id, self.voting_id))

    def __eq__(self, other):
        return self.chamber_name == other.chamber_name and self.term_id == other.term_id and \
            self.session_id == other.session_id and self.voting_id == other.voting_id


class VotingOutcomeTag(VotingTag):
    voting_id: str = Field(alias='votingId')

    class Config:
        use_enum_values = True

    def __gt__(self, other):
        return ((self.chamber_name, self.term_id, self.session_id, self.voting_id) >
                (other.chamber_name, other.term_id, other.session_id, other.voting_id))

    def __lt__(self, other):
        return ((self.chamber_name, self.term_id, self.session_id, self.voting_id) <
                (other.chamber_name, other.term_id, other.session_id, other.voting_id))

    def __ge__(self, other):
        return ((self.chamber_name, self.term_id, self.session_id, self.voting_id) >=
                (other.chamber_name, other.term_id, other.session_id, other.voting_id))

    def __le__(self, other):
        return ((self.chamber_name, self.term_id, self.session_id, self.voting_id) <=
                (other.chamber_name, other.term_id, other.session_id, other.voting_id))


class LegislationTag(TermTag):
    legislation_number: str = Field(alias='legislationNumber')

    def __hash__(self):
        return hash((self.chamber_name, self.term_id, self.legislation_number))

    def __eq__(self, other):
        return self.chamber_name == other.chamber_name and self.term_id == other.term_id and \
            self.legislation_number == other.legislation_number


class MemberTag(TermTag):
    member_id: str = Field(alias='memberId')
    member_type: Optional[str] = Field(alias='memberType', default=None)


class GroupTag(TermTag):
    name: str = Field(alias='name', default='')
    id: Optional[str] = Field(alias='id', default=None)

    def __hash__(self):
        return hash((self.chamber_name, self.term_id, self.name, self.id))

    def __eq__(self, other):
        return self.chamber_name == other.chamber_name and self.term_id == other.term_id and self.name == other.name and self.id == other.id


class SessionDayTag(SessionTag):
    date_id: str = Field(alias='dateId')


class StatementTag(SessionDayTag):
    statement_id: Optional[str] = Field(alias='statementId', default='')
    statement_id_new: Optional[int] = Field(alias='statementIdNew', default=-1)

    @model_validator(mode='before')
    @classmethod
    def check_statement_id(cls, data: Any) -> Any:
        if not (data.get('statementId') or (int(data.get('statementIdNew', '-1')) + 1)):
            raise ValueError('statementId or statementIdNew is required')
        return data


class MemberType(str, Enum):
    ACTIVE = "active"
    FORMER = "former"


class GroupType(str, Enum):
    KLUB = "klub"
    KOLO = "kolo"


class FakeTag(BaseModel, extra=Extra.ignore):
    a: str = Field(alias='a')


class ScrapeMode(str, Enum):
    ALL = "all"
    NEW = "new"
