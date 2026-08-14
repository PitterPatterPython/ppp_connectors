from unittest.mock import MagicMock, patch

import pytest

import pyapiary.dbms_connectors.odbc as odbc_module
from pyapiary.dbms_connectors.odbc import ODBCConnector


@pytest.fixture
def mock_pyodbc():
    with patch("pyapiary.dbms_connectors.odbc._get_pyodbc") as mock_loader:
        pyodbc_mock = MagicMock()
        mock_loader.return_value = pyodbc_mock
        yield pyodbc_mock


def test_odbcconnector_init(mock_pyodbc):
    mock_logger = MagicMock()
    connector = ODBCConnector("DSN=testdb", logger=mock_logger)
    mock_pyodbc.connect.assert_called_once_with("DSN=testdb", autocommit=False)
    assert connector.logger == mock_logger


def test_odbcconnector_init_autocommit_defaults_to_false(mock_pyodbc):
    """pyodbc defaults to autocommit=False; the connector must not change that."""
    ODBCConnector("DSN=testdb")

    mock_pyodbc.connect.assert_called_once_with("DSN=testdb", autocommit=False)


def test_odbcconnector_init_autocommit_true(mock_pyodbc):
    """Drivers without transaction support (e.g. BigQuery) require autocommit=True."""
    ODBCConnector("DSN=testdb", autocommit=True)

    mock_pyodbc.connect.assert_called_once_with("DSN=testdb", autocommit=True)


def test_odbcconnector_query_returns_rows(mock_pyodbc):
    """Test that query returns rows as dictionaries."""
    mock_cursor = MagicMock()
    mock_cursor.description = [("id",), ("name",)]
    mock_cursor.fetchall.return_value = [(1, "Alice"), (2, "Bob")]
    mock_pyodbc.connect.return_value.cursor.return_value = mock_cursor
    connector = ODBCConnector("DSN=testdb")

    results = list(connector.query("SELECT * FROM users"))

    assert results == [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]


def test_odbcconnector_bulk_insert(mock_pyodbc):
    mock_cursor = MagicMock()
    mock_pyodbc.connect.return_value.cursor.return_value = mock_cursor
    connector = ODBCConnector("DSN=testdb")

    data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    connector.bulk_insert("users", data)

    assert mock_cursor.executemany.called
    assert mock_pyodbc.connect.return_value.commit.called


def test_odbcconnector_bulk_insert_empty_data(mock_pyodbc):
    mock_cursor = MagicMock()
    mock_pyodbc.connect.return_value.cursor.return_value = mock_cursor
    connector = ODBCConnector("DSN=testdb")

    connector.bulk_insert("users", [])

    mock_cursor.executemany.assert_not_called()


def test_odbcconnector_context_manager_closes_connection(mock_pyodbc):
    """Test that the context manager closes the connection."""
    mock_conn = MagicMock()
    mock_pyodbc.connect.return_value = mock_conn

    with ODBCConnector("DSN=testdb") as connector:
        assert isinstance(connector, ODBCConnector)

    mock_conn.close.assert_called_once()


def test_odbcconnector_raises_helpful_error_when_pyodbc_missing(monkeypatch):
    """Ensure that using the connector without the extra raises a clear error."""
    monkeypatch.setattr(odbc_module, "_PYODBC_MODULE", None)
    monkeypatch.setattr(
        odbc_module,
        "import_module",
        MagicMock(side_effect=ImportError("pyodbc missing")),
    )

    with pytest.raises(ImportError) as excinfo:
        ODBCConnector("DSN=testdb")

    assert "pyodbc is not installed" in str(excinfo.value)
