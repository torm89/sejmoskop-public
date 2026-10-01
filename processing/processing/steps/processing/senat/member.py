from processing.models.data.preprocessing.member import MemberData, MemberImageData
from processing.steps.step import Step
from processing.transformers.processing.senat.member import MemberProcessingTransformerSenat


class MemberProcessingStepSenat(Step):

    @classmethod
    def run(cls, payload, *args, **kwargs):
        tag, data = payload['member_tag'], payload['member_data']

        current_image_data = payload['member_current_image']

        data = MemberProcessingTransformerSenat.extract_name_fields(tag=tag, data=data)
        data = MemberProcessingTransformerSenat.add_member_voting_name_field(tag=tag, data=data)
        data = MemberProcessingTransformerSenat.add_former_details_field(tag=tag, data=data)
        data = MemberProcessingTransformerSenat.add_birth_date_field(tag=tag, data=data)
        data = MemberProcessingTransformerSenat.add_member_country_field(tag=tag, data=data)

        data = MemberProcessingTransformerSenat.fix_member_type_field(tag=tag, data=data)

        image = MemberProcessingTransformerSenat.extract_member_image(current_image_data=current_image_data, data=data)

        payload.update({
            "member_data": MemberData.from_dict(tag=tag, data=data),
            "member_image": MemberImageData.from_dict(tag=tag, data=image)
        })

        return payload
