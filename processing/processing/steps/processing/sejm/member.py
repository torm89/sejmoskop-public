from processing.models.data.preprocessing.member import MemberData, MemberImageData
from processing.steps.step import Step
from processing.transformers.processing.sejm.member import MemberProcessingTransformerSejm


class MemberProcessingStepSejm(Step):

    @classmethod
    def run(cls, payload, *args, **kwargs):
        tag, data = payload['member_tag'], payload['member_data']

        current_image_data = payload['member_current_image']

        data = MemberProcessingTransformerSejm.add_member_second_name_field(tag=tag, data=data)
        data = MemberProcessingTransformerSejm.add_member_voting_name_field(tag=tag, data=data)
        data = MemberProcessingTransformerSejm.add_former_details_field(tag=tag, data=data)
        data = MemberProcessingTransformerSejm.add_member_country_field(tag=tag, data=data)

        data = MemberProcessingTransformerSejm.fix_member_type_field(tag=tag, data=data)

        image = MemberProcessingTransformerSejm.extract_member_image(current_image_data=current_image_data, data=data)

        payload.update({
            "member_data": MemberData.from_dict(tag=tag, data=data),
            "member_image": MemberImageData.from_dict(tag=tag, data=image)
        })

        return payload
