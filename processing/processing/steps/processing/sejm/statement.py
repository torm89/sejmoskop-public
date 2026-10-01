from processing.steps.processing.statement import StatementProcessingStep
from processing.transformers.processing.sejm.statement import StatementProcessingTransformerSejm


class StatementProcessingStepSejm(StatementProcessingStep):

    @classmethod
    def run(cls, payload, *args, **kwargs):
        tag, proceedings, dao = payload['statement_tag'], payload['statement_proceedings'], payload['statement_dao']

        morf = cls._morf_client()
        concraft = cls._concraft_client()

        statements = StatementProcessingTransformerSejm.extract_statements(
            tag=tag, proceedings=proceedings, hot_dao=dao)
        statements = StatementProcessingTransformerSejm.enrich_statements(statements, dao, morf=morf, concraft=concraft)

        payload.update({
            "statements_data_list": cls._prepare_statements_data_list(statements),
        })

        return payload

