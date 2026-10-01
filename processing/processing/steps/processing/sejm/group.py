from processing.models.data.preprocessing.group import GroupData, GroupImageData
from processing.steps.step import Step
from processing.transformers.processing.sejm.group import GroupProcessingTransformerSejm


class GroupProcessingStepSejm(Step):

    @classmethod
    def run(cls, payload, *args, **kwargs):
        tag, data = payload['group_tag'], payload['group_data']

        data = GroupProcessingTransformerSejm.fix_group_name_short_field(tag=tag, data=data)
        data = GroupProcessingTransformerSejm.fix_group_type_field(tag=tag, data=data)

        image = GroupProcessingTransformerSejm.extract_group_image(tag=tag, data=data)

        payload.update({
            "group_data": GroupData.from_dict(tag=tag, data=data),
            "group_image": GroupImageData.from_dict(tag=tag, data=image)
        })

        return payload
