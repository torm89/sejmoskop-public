from unittest.mock import Mock, patch, MagicMock, PropertyMock

import pandas as pd

from tests.models.data.init.conftest import MockData


def test_rename_columns():
    fake_df = pd.DataFrame({"old_name": [1, 2, 3, 4, 5]})
    fake_column_renaming_dict = {"old_name": "new_name"}

    renamed_df = MockData.rename_columns(fake_df, fake_column_renaming_dict)

    pd.testing.assert_frame_equal(renamed_df, pd.DataFrame({"new_name": [1, 2, 3, 4, 5]}))
    pd.testing.assert_frame_equal(fake_df, pd.DataFrame({"old_name": [1, 2, 3, 4, 5]}))


def test_filter_columns():
    fake_df = pd.DataFrame({"column01": [1, 2, 3, 4, 5], "column02": [11, 22, 33, 44, 55]})
    fake_columns = ["column02"]

    filtered_df = MockData.filter_columns(fake_df, fake_columns)

    pd.testing.assert_frame_equal(filtered_df, pd.DataFrame({"column02": [11, 22, 33, 44, 55]}))
    pd.testing.assert_frame_equal(
        fake_df, pd.DataFrame({"column01": [1, 2, 3, 4, 5], "column02": [11, 22, 33, 44, 55]}))


def test_unify_column_types():
    fake_df = pd.DataFrame({"column01": [1, 2, 3, 4, 5], "column02": [11, 22, 33, 44, 55]})
    fake_columns_types = {"column01": str}

    unified_df = MockData.unify_column_types(fake_df, fake_columns_types)

    pd.testing.assert_frame_equal(
        unified_df, pd.DataFrame({"column01": ['1', '2', '3', '4', '5'], "column02": [11, 22, 33, 44, 55]}))
    pd.testing.assert_frame_equal(
        fake_df, pd.DataFrame({"column01": [1, 2, 3, 4, 5], "column02": [11, 22, 33, 44, 55]}))


def test_normalize_df():
    mock_data = MockData(tag=Mock(), df=pd.DataFrame())
    mock_data.df = "01"

    # TODO: Get rid of those "with" statements
    with patch('tests.models.data.init.conftest.MockData.column_renaming_dict',
               new_callable=PropertyMock) as column_renaming_dict:
        with patch('tests.models.data.init.conftest.MockData.columns', new_callable=PropertyMock) as columns:
            with patch('tests.models.data.init.conftest.MockData.columns_types',
                       new_callable=PropertyMock) as columns_types:
                column_renaming_dict.return_value = "fake_column_renaming_dict"
                columns.return_value = "fake_columns"
                columns_types.return_value = 'fake_columns_types'

                mock_data.rename_columns = Mock(return_value='02')
                mock_data.filter_columns = Mock(return_value='03')
                mock_data.unify_column_types = Mock(return_value='04')

                mock_data.normalize_df()

                mock_data.rename_columns.assert_called_once_with('01', 'fake_column_renaming_dict')
                mock_data.filter_columns.assert_called_once_with('02', 'fake_columns')
                mock_data.unify_column_types.assert_called_once_with('03', 'fake_columns_types')


def test_normalize_df_empty_columns_types():
    mock_data = MockData(tag=Mock(), df=pd.DataFrame())
    mock_data.df = "01"

    # TODO: Get rid of those "with" statements
    with patch('tests.models.data.init.conftest.MockData.column_renaming_dict',
               new_callable=PropertyMock) as column_renaming_dict:
        with patch('tests.models.data.init.conftest.MockData.columns', new_callable=PropertyMock) as columns:
            with patch('tests.models.data.init.conftest.MockData.columns_types',
                       new_callable=PropertyMock) as columns_types:
                column_renaming_dict.return_value = "fake_column_renaming_dict"
                columns.return_value = "fake_columns"
                columns_types.return_value = {}

                mock_data.rename_columns = Mock(return_value='02')
                mock_data.filter_columns = Mock(return_value='03')
                mock_data.unify_column_types = Mock(return_value='04')

                mock_data.normalize_df()

                mock_data.rename_columns.assert_called_once_with('01', 'fake_column_renaming_dict')
                mock_data.filter_columns.assert_called_once_with('02', 'fake_columns')
                mock_data.unify_column_types.assert_not_called()


@patch.object(pd.DataFrame, "copy")
@patch.object(MockData, "normalize_df")
def test_innit(mock_normalize_df, mock_df_copy):
    MockData(tag=Mock(), df=pd.DataFrame())

    mock_df_copy.assert_called_once()
    mock_normalize_df.assert_called_once()


def test_from_dict():
    # TODO: write that one
    assert True


@patch.object(MockData, "from_dict", return_value="fake_data")
def test_from_json(mock_data_from_dict_mock):
    MockData.from_json('fake_tag', "{\"fake key\": \"fake value\"}")

    mock_data_from_dict_mock.assert_called_once_with(tag='fake_tag', data={"fake key": "fake value"})


def test_df_csv():
    # TODO: write that one
    assert True


def test_to_file():
    # TODO: write that one
    assert True


def test_df_csv():
    # TODO: write that one
    assert True
