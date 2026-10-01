from processing.models.data.preprocessing.member import MemberImageData
from processing.transformers.processing.sejm.member import MemberProcessingTransformerSejm


def test_extract_member_image(fake_member_tag, fake_member_data, fake_member_image):
    fake_current_image_data = MemberImageData(tag=fake_member_tag, data=None)

    image = MemberProcessingTransformerSejm.extract_member_image(fake_current_image_data, fake_member_data)
    assert image == fake_member_image
