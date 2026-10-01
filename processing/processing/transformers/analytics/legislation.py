from sqlalchemy import select, Integer, and_

from processing.models.tables.legislation import Legislation, LegislationStage, LegislationVoting
from processing.models.tables.voting import Voting
from processing.models.tags import TermTag


class LegislationAnalyticsTransformer:

    @staticmethod
    def legislation_query(term_tag: TermTag):
        return (
            select(Legislation)
            .where(
                Legislation.chamber_name == term_tag.chamber_name,
                Legislation.term_id == term_tag.term_id,
            )
            .order_by(Legislation.legislation_number)
        )

    @staticmethod
    def legislation_stages_query(term_tag: TermTag):
        return (
            select(LegislationStage)
            .where(
                LegislationStage.chamber_name == term_tag.chamber_name,
                LegislationStage.term_id == term_tag.term_id,
            )
            .order_by(
                LegislationStage.legislation_number,
                LegislationStage.stage_index.cast(Integer),
            )
        )

    @staticmethod
    def legislation_votings_query(term_tag: TermTag):
        # Join each stage->vote link to the existing votings table so the web can
        # show the vote's date and title in context. Outer join: keep the link
        # even if the referenced voting has not been processed yet.
        return (
            select(
                LegislationVoting.legislation_number,
                LegislationVoting.stage_index,
                LegislationVoting.session_id,
                LegislationVoting.voting_id,
                Voting.datetime,
                Voting.description_01,
                Voting.description_02,
            )
            .join(
                Voting,
                and_(
                    LegislationVoting.chamber_name == Voting.chamber_name,
                    LegislationVoting.term_id == Voting.term_id,
                    LegislationVoting.session_id == Voting.session_id,
                    LegislationVoting.voting_id == Voting.voting_id,
                ),
                isouter=True,
            )
            .where(
                LegislationVoting.chamber_name == term_tag.chamber_name,
                LegislationVoting.term_id == term_tag.term_id,
            )
            .order_by(
                LegislationVoting.legislation_number,
                LegislationVoting.stage_index.cast(Integer),
            )
        )
