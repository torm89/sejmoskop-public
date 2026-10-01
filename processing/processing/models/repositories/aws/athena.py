import shutil
import tempfile
from pathlib import Path

from processing.providers.aws import AwsProvider


class AthenaRepository:
    def __init__(self):
        self.provider = AwsProvider()

        self._result_reuse_max_age = 3

        directory = tempfile.mkdtemp()
        self.directory_path = Path(directory)

    def __del__(self):
        shutil.rmtree(str(self.directory_path))

    @property
    def result_reuse_max_age(self):
        return self._result_reuse_max_age

    @result_reuse_max_age.setter
    def result_reuse_max_age(self, value):
        self._result_reuse_max_age = value

    def run_query(self, query: str, max_age: int = None) -> Path:
        result_reuse_max_age = self.result_reuse_max_age if max_age is None else max_age

        return self.provider.athena_run_query(
            directory_path=self.directory_path,
            QueryString=str(query),
            QueryExecutionContext={
                'Database': self.provider.athena_database_name,
                'Catalog': "AwsDataCatalog"
            },
            WorkGroup=self.provider.athena_workgroup_name,
            ResultReuseConfiguration={
                'ResultReuseByAgeConfiguration': {
                    'Enabled': bool(result_reuse_max_age),
                    'MaxAgeInMinutes': result_reuse_max_age
                }
            }
        )
