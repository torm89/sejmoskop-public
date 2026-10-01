import csv
import json
import pathlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from io import BytesIO
from typing import TypeVar, Generic, Dict, List, Any, Type, Union

import pandas as pd

from processing.models.tags import MemberTag, VotingTag, TermTag, LegislationTag

T = TypeVar('T', MemberTag, VotingTag, TermTag, LegislationTag)


@dataclass
class DataHot(Generic[T], ABC):
    tag: T
    data: Dict

    @classmethod
    def from_json(cls, tag: T, data: str):
        return cls(tag=tag, data=json.loads(data))


@dataclass
class Data(Generic[T], ABC):
    tag: T
    df: pd.DataFrame

    @property
    @abstractmethod
    def columns(self) -> List[str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def columns_types(self) -> Dict[str, Type]:
        raise NotImplementedError

    @property
    def column_renaming_dict(self) -> Dict[str, str]:
        return {
            'chamberName': 'chamber_name', 'termId': 'term_id',

            'memberId': 'member_id', 'firstName': 'first_name', 'secondName': 'second_name', 'lastName': 'last_name',
            'memberType': 'member_type', 'votingName': 'voting_name', 'birthDate': "birth_date",

            'sessionId': 'session_id', 'votingId': 'voting_id', 'votingType': 'voting_type',
            'description01': 'description_01', 'description02': 'description_02', 'description03': 'description_03',

            'memberName': 'member_name', 'groupNameShort': 'group_name_short',

            'nameShort': 'name_short', 'groupType': 'group_type'
        }

    @staticmethod
    def rename_columns(df: pd.DataFrame, column_renaming_dict: Dict[str, str]):
        return df.rename(columns=column_renaming_dict, errors='ignore')

    @staticmethod
    def filter_columns(df: pd.DataFrame, columns: List[str]):
        return df[[c for c in columns]]

    @staticmethod
    def unify_column_types(df: pd.DataFrame, columns_types: Dict[str, Any]):
        return df.astype({k: v for k, v in columns_types.items() if k in df.columns}, errors='ignore')

    def normalize_df(self):
        self.df = self.rename_columns(self.df, self.column_renaming_dict)
        self.df = self.filter_columns(self.df, self.columns)
        self.df = self.unify_column_types(self.df, self.columns_types) if self.columns_types else self.df

    def __init__(self, tag: T, df: pd.DataFrame):
        self.tag = tag
        self.df = df.copy()

        self.normalize_df()

    @classmethod
    def from_dict(cls, tag: T, data):
        df = pd.DataFrame(data if type(data) is list else [data])

        return cls(tag=tag, df=df)

    @classmethod
    def from_json(cls, tag: T, data: str):
        return cls.from_dict(tag=tag, data=json.loads(data))

    @classmethod
    def from_csv(cls, tag: T, data: any, header=None):
        df = pd.read_csv(BytesIO(data), quoting=csv.QUOTE_NONNUMERIC, quotechar="'", header=header,
                         names=cls.columns2(), dtype=cls.columns_types2())
        return cls(tag=tag, df=df)

    @classmethod
    def from_query(cls, tag: TermTag, query: Any, session):
        return cls(tag=tag, df=pd.read_sql_query(sql=query, con=session.connection()))

    @classmethod
    def from_query_repository_athena(cls, tag: TermTag, query: Any, repository_athena):
        query_compiled = query.compile(compile_kwargs={"literal_binds": True})
        filepath = repository_athena.run_query(query_compiled)

        return cls(tag=tag, df=pd.read_csv(str(filepath), header=0, dtype=str))

    def df_csv(self, header=True) -> str:
        return self.df.to_csv(index=False, quoting=csv.QUOTE_NONNUMERIC, quotechar="'", header=header)

    @staticmethod
    def df_to_json(df, **kwargs) -> str:
        return df.to_json(orient='records', **kwargs)

    def df_json(self, **kwargs) -> str:
        return self.df_to_json(df=self.df, **kwargs)

    def df_dict(self):
        return self.df.to_dict(orient='records')

    def to_json(self, path: pathlib.Path):
        tag_dict = self.tag if isinstance(self.tag, dict) else self.tag.model_dump()
        json.dump({'tag': tag_dict, 'data': self.df_dict()}, path.open('w+'), indent=4)


class DataNoSql(Generic[T], ABC):
    def __init__(self, tag: T, data: Union[List[Dict], Dict]):
        self.tag = tag
        self.data = data.copy()

    @classmethod
    def from_dict(cls, tag: T, data: Union[List[Dict], Dict]):
        return cls(tag=tag, data=data)

    @classmethod
    def from_json(cls, tag: T, data: str):
        return cls.from_dict(tag=tag, data=json.loads(data))

    @staticmethod
    def data_to_json(data, **kwargs) -> str:
        return json.dumps(data, indent=2)

    def data_json(self, **kwargs) -> str:
        return self.data_to_json(data=self.data, **kwargs)
