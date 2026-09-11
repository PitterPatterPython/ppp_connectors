from pyapiary.dbms_connectors.elasticsearch import ElasticsearchConnector
from pyapiary.helpers import combine_env_configs, setup_logger
from typing import Dict, Any
import json


env_config: Dict[str, Any] = combine_env_configs()

# Initialize logger
logger = setup_logger(name="es_test", level="INFO")

index = env_config["ES_INDEX"]

# Credentials are optional; omit them for an unsecured cluster
client = ElasticsearchConnector(
    hosts=[env_config["ES_HOST"]],
    username=env_config.get("ES_USER"),
    password=env_config.get("ES_PASS"),
    logger=logger
)

logger.info("Inserting two docs without an _id (cluster should generate them)...")
success, errors = client.bulk_insert(
    index=index,
    data=[{"test": 1}, {"test": 2}]
)
logger.info(f"bulk_insert -> success={success} errors={errors}")

logger.info("Inserting two docs with an explicit _id...")
success, errors = client.bulk_insert(
    index=index,
    data=[{"_id": "dev-1", "test": 3}, {"_id": "dev-2", "test": 4}]
)
logger.info(f"bulk_insert -> success={success} errors={errors}")

client.client.indices.refresh(index=index)

logger.info("Form 1: Lucene query string")
for hit in client.query(index=index, query="test:1 OR test:3", size=10):
    print(json.dumps(hit["_source"], indent=2))

logger.info("Form 2: full DSL search body, with size set inside the body")
full_body = {
    "query": {"match_all": {}},
    "size": 5,
    "sort": [{"_doc": "asc"}]
}
for hit in client.query(index=index, query=full_body):
    print(json.dumps(hit["_source"], indent=2))

logger.info("Form 3: bare DSL query clause")
for hit in client.query(index=index, query={"term": {"test": 4}}, size=10):
    print(json.dumps(hit["_source"], indent=2))

logger.info("Abandoning the generator early; the scroll context should still be cleared")
for i, hit in enumerate(client.query(index=index, query={"match_all": {}}, size=10)):
    print(json.dumps(hit["_source"], indent=2))
    if i >= 2:
        break

stats = client.client.nodes.stats(metric="indices", index_metric="search")
scroll_current = sum(
    node["indices"]["search"]["scroll_current"] for node in stats["nodes"].values()
)
logger.info(f"Open scroll contexts across the cluster: {scroll_current} (expected 0)")
