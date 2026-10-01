from abc import abstractmethod, ABC
from typing import TypeVar, Generic, List

from processing.models.data.analytics.groups import Groups, GroupsMembersRotation
from processing.models.data.analytics.members import Members, MembersVotingsOutcomesStats, \
    MembersVotingsOutcomesConsistencyChamber, MembersVotingsOutcomesConsistencyGroups, \
    MembersVotingsOutcomesAbstainRanking, MembersVotingsOutcomesNoVotedRanking
from processing.models.data.analytics.statements import StatementsDetails, StatementsSessionDayDetails
from processing.models.data.analytics.legislation import LegislationAnalytics, LegislationStagesAnalytics, \
    LegislationVotingsAnalytics
from processing.models.data.preprocessing.group import GroupImageData, GroupData
from processing.models.data.preprocessing.member import MemberData, MemberImageData
from processing.models.data.preprocessing.statement import StatementData
from processing.models.data.preprocessing.voting import VotingData, VotingOutcomeData
from processing.models.data.preprocessing.legislation import LegislationData, LegislationStageData, \
    LegislationVotingData
from processing.models.tags import TermTag, MemberTag, VotingTag, GroupTag, StatementTag, LegislationTag

T = TypeVar('T', MemberTag, VotingTag, GroupTag, StatementTag, LegislationTag)
D = TypeVar(
    'D',
    MemberData,
    MemberImageData,

    GroupData,
    GroupImageData,

    VotingData,
    VotingOutcomeData,

    StatementData,

    LegislationData,
    LegislationStageData,
    LegislationVotingData,

    Members,
    MembersVotingsOutcomesStats,
    MembersVotingsOutcomesConsistencyChamber,
    MembersVotingsOutcomesConsistencyGroups,
    MembersVotingsOutcomesAbstainRanking,
    MembersVotingsOutcomesNoVotedRanking,

    Groups,
    GroupsMembersRotation,

    StatementsDetails,
    StatementsSessionDayDetails,

    LegislationAnalytics,
    LegislationStagesAnalytics,
    LegislationVotingsAnalytics
)


class Dao(Generic[T, D], ABC):

    @abstractmethod
    def list(self, term_tag: TermTag) -> List[D]:
        pass

    @abstractmethod
    def get(self, tag: T) -> D:
        pass

    @abstractmethod
    def save(self, data: D) -> None:
        pass
