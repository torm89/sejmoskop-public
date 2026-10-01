from processing.models.data.preprocessing.legislation import LegislationData, LegislationStageData, \
    LegislationVotingData
from processing.steps.step import Step
from processing.transformers.processing.sejm.legislation import LegislationProcessingTransformerSejm


class LegislationProcessingStepSejm(Step):

    @classmethod
    def run(cls, payload, *args, **kwargs):
        tag, data = payload['legislation_tag'], payload['legislation_data']

        legislation = LegislationProcessingTransformerSejm.extract_legislation(tag=tag, data=data)
        stages = LegislationProcessingTransformerSejm.extract_stages(tag=tag, data=data)
        votings = LegislationProcessingTransformerSejm.extract_votings(tag=tag, data=data)

        payload.update({
            "legislation_data": LegislationData.from_dict(tag=tag, data=legislation),
            "legislation_stage_data": LegislationStageData.from_dict(tag=tag, data=stages) if stages else None,
            "legislation_voting_data": LegislationVotingData.from_dict(tag=tag, data=votings) if votings else None,
        })

        return payload
