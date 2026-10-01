from processing.models.data.preprocessing.voting import VotingData, VotingOutcomeData
from processing.steps.step import Step
from processing.transformers.processing.senat.voting import VotingProcessingTransformerSenat


class VotingProcessingStepSenat(Step):

    @classmethod
    def run(cls, payload, *args, **kwargs):
        tag, data = payload['voting_tag'], payload['voting_data']

        data = VotingProcessingTransformerSenat.add_datetime_field(tag=tag, data=data)
        data = VotingProcessingTransformerSenat.add_description_03_field(tag=tag, data=data)
        data = VotingProcessingTransformerSenat.fix_voting_type_field(tag=tag, data=data)

        outcome_data, outcome_tag = VotingProcessingTransformerSenat.extract_outcome(tag=tag, data=data)

        payload.update({
            "voting_data": VotingData.from_dict(tag=tag, data=data),
            "voting_outcome_data":
                VotingOutcomeData.from_dict(tag=outcome_tag, data=outcome_data) if outcome_data else None
        })

        return payload
