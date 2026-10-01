from processing.models.tags import StatementTag
from processing.steps.processing.statement import StatementProcessingStep
from processing.transformers.processing.european.parliament.statement import \
    StatementProcessingTransformerEuropeanParliament


class StatementProcessingStepEuropeanParliament(StatementProcessingStep):

    @classmethod
    def run(cls, payload, *args, **kwargs):
        tag, data = payload['statement_tag'], payload['statement_data']

        statement = {}
        statement.update(StatementProcessingTransformerEuropeanParliament.extract_timeline(tag, data))
        statement.update(StatementProcessingTransformerEuropeanParliament.extract_tag(tag, data))
        statement.update(StatementProcessingTransformerEuropeanParliament.extract_speaker(tag, data))
        statement.update(StatementProcessingTransformerEuropeanParliament.extract_language(tag, data))
        statement.update(StatementProcessingTransformerEuropeanParliament.extract_chairman(tag, data))
        statement.update(StatementProcessingTransformerEuropeanParliament.extract_written(tag, data))
        # Same document shape as sejm/senat; EP interventions carry no details.
        statement.update({"details": {}})

        tag_dict = tag.model_dump(by_alias=True)
        tag_dict["statementIdNew"] = StatementProcessingTransformerEuropeanParliament.encode_statement_id(
            tag_dict['statementId'])
        statement_tag = StatementTag(**tag_dict)

        payload.update({
            "statement_tag": statement_tag,
            "statement_data": statement
        })

        return payload


class StatementInterpretationStepEuropeanParliament(StatementProcessingStep):

    @classmethod
    def run(cls, payload, *args, **kwargs):
        tag, data = payload['statement_tag'], payload['statement_data']

        morf = cls._morf_client()
        concraft = cls._concraft_client()

        statement = StatementProcessingTransformerEuropeanParliament.add_text_interpretation(data, morf, concraft)

        payload.update({
            "statement_data": statement
        })

        return payload
