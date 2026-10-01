from processing.models.data.preprocessing.group import GroupData
from processing.steps.step import Step
from processing.transformers.processing.senat.group import GroupProcessingTransformerSenat


class GroupProcessingStepSenat(Step):

    @classmethod
    def run(cls, payload, *args, **kwargs):
        tag, data = payload['group_tag'], payload['group_data']

        data = GroupProcessingTransformerSenat.add_group_name_short_field(tag=tag, data=data)
        data = GroupProcessingTransformerSenat.fix_group_type_field(tag=tag, data=data)

        payload.update({
            "group_data": GroupData.from_dict(tag=tag, data=data),
        })

        return payload
