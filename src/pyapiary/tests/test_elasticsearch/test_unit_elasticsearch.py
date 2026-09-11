import unittest
from unittest.mock import patch, MagicMock
from elasticsearch import NotFoundError
from pyapiary.dbms_connectors.elasticsearch import ElasticsearchConnector


def _not_found():
    return NotFoundError("index_not_found_exception", MagicMock(status=404), {})


class TestElasticsearchConnector(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock()
        self.connector = ElasticsearchConnector(
            hosts=["http://localhost:9200"],
            username="user",
            password="pass",
            logger=self.mock_logger
        )

    @patch("pyapiary.dbms_connectors.elasticsearch.Elasticsearch")
    def test_initialization(self, mock_es):
        ElasticsearchConnector(
            hosts=["http://localhost:9200"],
            username="user",
            password="pass",
            logger=self.mock_logger
        )
        mock_es.assert_called_with(["http://localhost:9200"], basic_auth=("user", "pass"))

    @patch("pyapiary.dbms_connectors.elasticsearch.Elasticsearch")
    def test_initialization_without_credentials_omits_basic_auth(self, mock_es):
        ElasticsearchConnector(hosts=["http://localhost:9200"], logger=self.mock_logger)
        mock_es.assert_called_with(["http://localhost:9200"])

    @patch("pyapiary.dbms_connectors.elasticsearch.Elasticsearch")
    def test_initialization_with_api_key(self, mock_es):
        ElasticsearchConnector(
            hosts=["http://localhost:9200"], api_key="abc123", logger=self.mock_logger
        )
        mock_es.assert_called_with(["http://localhost:9200"], api_key="abc123")

    @patch("pyapiary.dbms_connectors.elasticsearch.Elasticsearch")
    def test_initialization_rejects_partial_basic_auth(self, mock_es):
        with self.assertRaises(ValueError):
            ElasticsearchConnector(hosts=["http://localhost:9200"], username="user")

    @patch("pyapiary.dbms_connectors.elasticsearch.Elasticsearch")
    def test_initialization_rejects_mixed_auth(self, mock_es):
        with self.assertRaises(ValueError):
            ElasticsearchConnector(
                hosts=["http://localhost:9200"],
                username="user",
                password="pass",
                api_key="abc123",
            )

    def test_build_search_body_lucene_string(self):
        body = ElasticsearchConnector._build_search_body("status:500 AND host:web*")
        self.assertEqual(
            body, {"query": {"query_string": {"query": "status:500 AND host:web*"}}}
        )

    def test_build_search_body_full_body_passthrough(self):
        source = {"query": {"match_all": {}}, "sort": [{"@timestamp": "desc"}]}
        self.assertEqual(ElasticsearchConnector._build_search_body(source), source)

    def test_build_search_body_wraps_bare_clause(self):
        body = ElasticsearchConnector._build_search_body({"match": {"host": "web1"}})
        self.assertEqual(body, {"query": {"match": {"host": "web1"}}})

    def test_build_search_body_empty_dict_matches_all(self):
        self.assertEqual(
            ElasticsearchConnector._build_search_body({}), {"query": {"match_all": {}}}
        )

    def test_build_search_body_rejects_bad_type(self):
        with self.assertRaises(TypeError):
            ElasticsearchConnector._build_search_body(["match_all"])

    @patch("pyapiary.dbms_connectors.elasticsearch.Elasticsearch")
    def test_query_scroll(self, mock_es):
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "_scroll_id": "abc123",
            "hits": {"hits": [{"_id": 1}, {"_id": 2}]}
        }
        mock_client.scroll.side_effect = [
            {"_scroll_id": "abc123", "hits": {"hits": [{"_id": 3}]}},
            {"_scroll_id": "abc123", "hits": {"hits": []}},
        ]
        mock_es.return_value = mock_client
        connector = ElasticsearchConnector(
            hosts=["http://localhost:9200"],
            username="user",
            password="pass",
            logger=self.mock_logger
        )
        results = list(connector.query(index="test", query={"match_all": {}}))
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["_id"], 1)
        mock_client.options.return_value.clear_scroll.assert_called_once_with(
            scroll_id="abc123"
        )

    @patch("pyapiary.dbms_connectors.elasticsearch.Elasticsearch")
    def test_query_sends_size_in_body_only(self, mock_es):
        mock_client = MagicMock()
        mock_client.search.return_value = {"_scroll_id": "s", "hits": {"hits": []}}
        mock_es.return_value = mock_client
        connector = ElasticsearchConnector(hosts=["http://localhost:9200"])
        list(connector.query(index="test", query={"match_all": {}}, size=25))

        _, kwargs = mock_client.search.call_args
        self.assertEqual(kwargs["body"]["size"], 25)
        self.assertNotIn("size", {k: v for k, v in kwargs.items() if k != "body"})

    @patch("pyapiary.dbms_connectors.elasticsearch.Elasticsearch")
    def test_query_respects_size_in_dsl_body(self, mock_es):
        mock_client = MagicMock()
        mock_client.search.return_value = {"_scroll_id": "s", "hits": {"hits": []}}
        mock_es.return_value = mock_client
        connector = ElasticsearchConnector(hosts=["http://localhost:9200"])
        list(connector.query(
            index="test", query={"query": {"match_all": {}}, "size": 10}, size=1000
        ))

        _, kwargs = mock_client.search.call_args
        self.assertEqual(kwargs["body"]["size"], 10)

    @patch("pyapiary.dbms_connectors.elasticsearch.Elasticsearch")
    def test_query_clears_scroll_when_generator_abandoned(self, mock_es):
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "_scroll_id": "abc123",
            "hits": {"hits": [{"_id": 1}, {"_id": 2}]}
        }
        mock_client.scroll.return_value = {
            "_scroll_id": "abc123", "hits": {"hits": [{"_id": 3}]}
        }
        mock_es.return_value = mock_client
        connector = ElasticsearchConnector(hosts=["http://localhost:9200"])

        gen = connector.query(index="test", query={"match_all": {}})
        next(gen)
        gen.close()

        mock_client.options.return_value.clear_scroll.assert_called_once_with(
            scroll_id="abc123"
        )

    @patch("pyapiary.dbms_connectors.elasticsearch.Elasticsearch")
    def test_query_missing_index_logs_and_raises(self, mock_es):
        mock_client = MagicMock()
        mock_client.search.side_effect = _not_found()
        mock_es.return_value = mock_client
        connector = ElasticsearchConnector(
            hosts=["http://localhost:9200"], logger=self.mock_logger
        )

        with self.assertRaises(NotFoundError):
            list(connector.query(index="missing", query={"match_all": {}}))
        self.assertIn("was not found", self.mock_logger.error.call_args[0][0])

    @patch("pyapiary.dbms_connectors.elasticsearch.Elasticsearch")
    def test_query_expired_scroll_logs_and_raises(self, mock_es):
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "_scroll_id": "abc123", "hits": {"hits": [{"_id": 1}]}
        }
        mock_client.scroll.side_effect = _not_found()
        mock_es.return_value = mock_client
        connector = ElasticsearchConnector(
            hosts=["http://localhost:9200"], logger=self.mock_logger
        )

        with self.assertRaises(NotFoundError):
            list(connector.query(index="test", query={"match_all": {}}))
        self.assertIn("Scroll context expired", self.mock_logger.error.call_args[0][0])

    @patch("pyapiary.dbms_connectors.elasticsearch.Elasticsearch")
    def test_query_without_scroll_id_yields_first_page(self, mock_es):
        mock_client = MagicMock()
        mock_client.search.return_value = {"hits": {"hits": [{"_id": 1}]}}
        mock_es.return_value = mock_client
        connector = ElasticsearchConnector(
            hosts=["http://localhost:9200"], logger=self.mock_logger
        )

        results = list(connector.query(index="test", query={"match_all": {}}))
        self.assertEqual(len(results), 1)
        mock_client.scroll.assert_not_called()

    @patch("pyapiary.dbms_connectors.elasticsearch.helpers.bulk")
    def test_bulk_insert(self, mock_bulk):
        mock_bulk.return_value = (3, [])
        data = [{"_id": "1", "name": "Alice"}, {"_id": "2", "name": "Bob"}, {"_id": "3", "name": "Charlie"}]
        success, errors = self.connector.bulk_insert(index="test-index", data=data)
        self.assertEqual(success, 3)
        self.assertEqual(errors, [])
        self.mock_logger.info.assert_called_with("Bulk insert completed successfully")

        actions = mock_bulk.call_args[0][1]
        self.assertEqual(actions[0]["_id"], "1")
        self.assertFalse(mock_bulk.call_args[1]["raise_on_error"])

    @patch("pyapiary.dbms_connectors.elasticsearch.helpers.bulk")
    def test_bulk_insert_omits_missing_id(self, mock_bulk):
        mock_bulk.return_value = (2, [])
        self.connector.bulk_insert(index="test-index", data=[{"test": 1}, {"test": 2}])

        actions = mock_bulk.call_args[0][1]
        self.assertNotIn("_id", actions[0])
        self.assertEqual(actions[0]["_source"], {"test": 1})

    @patch("pyapiary.dbms_connectors.elasticsearch.helpers.bulk")
    def test_bulk_insert_with_errors(self, mock_bulk):
        mock_bulk.return_value = (2, [{"error": "failed to insert"}])
        data = [{"_id": "1", "name": "Alice"}, {"_id": "2", "name": "Bob"}]
        success, errors = self.connector.bulk_insert(index="test-index", data=data)
        self.assertEqual(success, 2)
        self.assertTrue(errors)
        self.mock_logger.error.assert_called()


if __name__ == "__main__":
    unittest.main()
