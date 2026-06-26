"""Curated GraphQL query catalog for OpenCTI 6.9.x.

These are static, schema-verified query documents (validated against
``docs/opencti-6.9.6.graphql``). They are the "shape" decisions -- which fields
to fetch -- separated from the connector logic so they stay readable and are
easy to validate in CI.

Notes verified against the live 6.9.6 schema:
    - ``StixCoreObject`` is an interface; it has no ``name``. Every entity does
      expose ``representative { main secondary }``, a universal display label,
      so the generic search selects that instead of per-type fragments.
    - ``Filter.key`` is ``[String!]!`` and ``values`` is ``[Any!]!`` (both lists).
    - List connections expose ``pageInfo { endCursor hasNextPage globalCount }``.
    - ``stixCoreRelationships`` takes list args (``fromId``/``toId``/
      ``relationship_type`` are ``[String]``).
"""

# Common OpenCTI entity types accepted by the `types` argument of
# `stixCoreObjects` / `stixCyberObservables`. Not exhaustive -- extend as needed.
SEARCHABLE_TYPES = (
    "Stix-Cyber-Observable",
    "Indicator",
    # threats
    "Threat-Actor-Group",
    "Threat-Actor-Individual",
    "Intrusion-Set",
    "Campaign",
    # arsenal
    "Malware",
    "Tool",
    "Channel",
    "Vulnerability",
    # techniques
    "Attack-Pattern",
    "Narrative",
    "Course-Of-Action",
    # locations
    "Region",
    "Country",
    "City",
    "Position",
    "Administrative-Area",
    # entities
    "Individual",
    "Organization",
    "Sector",
    "System",
    "Event",
    "Infrastructure",
)


# Generic entity search/listing across any STIX core object type.
# Uses `representative` for a type-agnostic display label.
SEARCH_ENTITIES_QUERY = """
query SearchEntities($types: [String], $search: String, $filters: FilterGroup, $first: Int, $after: ID) {
  stixCoreObjects(types: $types, search: $search, filters: $filters, first: $first, after: $after) {
    edges {
      node {
        id
        standard_id
        entity_type
        parent_types
        created_at
        updated_at
        representative { main secondary }
      }
    }
    pageInfo { endCursor hasNextPage globalCount }
  }
}
"""


INDICATORS_QUERY = """
query Indicators($filters: FilterGroup, $search: String, $first: Int, $after: ID) {
  indicators(filters: $filters, search: $search, first: $first, after: $after) {
    edges {
      node {
        id
        standard_id
        entity_type
        created_at
        updated_at
        name
        description
        pattern
        pattern_type
        indicator_types
        valid_from
        valid_until
        revoked
        confidence
        x_opencti_score
        x_opencti_detection
        x_opencti_main_observable_type
      }
    }
    pageInfo { endCursor hasNextPage globalCount }
  }
}
"""


OBSERVABLES_QUERY = """
query Observables($types: [String], $filters: FilterGroup, $search: String, $first: Int, $after: ID) {
  stixCyberObservables(types: $types, filters: $filters, search: $search, first: $first, after: $after) {
    edges {
      node {
        id
        standard_id
        entity_type
        created_at
        updated_at
        observable_value
        x_opencti_score
        x_opencti_description
      }
    }
    pageInfo { endCursor hasNextPage globalCount }
  }
}
"""


RELATIONSHIPS_QUERY = """
query Relationships($fromId: [String], $toId: [String], $relationship_type: [String], $filters: FilterGroup, $first: Int, $after: ID) {
  stixCoreRelationships(fromId: $fromId, toId: $toId, relationship_type: $relationship_type, filters: $filters, first: $first, after: $after) {
    edges {
      node {
        id
        standard_id
        entity_type
        relationship_type
        fromId
        fromType
        toId
        toType
        start_time
        stop_time
        created_at
        confidence
      }
    }
    pageInfo { endCursor hasNextPage globalCount }
  }
}
"""
