# Search Engine Integration (Elasticsearch)

## Architecture
- Elasticsearch deployed as StatefulSet in Kubernetes (see k8s/elasticsearch.yaml)
- Exposed via ClusterIP service (see k8s/elasticsearch-service.yaml)
- App connects using endpoint from ConfigMap/Secret
- Supports scaling to multi-node cluster for production

## Configuration
- Endpoint: http://elasticsearch:9200
- Credentials: Managed via Kubernetes Secret (if needed)
- JVM options: -Xms512m -Xmx512m (adjust for prod)
- Persistent storage: 10Gi per node

## App Integration
- Use @elastic/elasticsearch npm package
- Configure client with endpoint and credentials
- Implement data connector module for indexing

## Indexing Pipeline
- Initial full indexing script for bootstrapping
- Incremental indexing on data changes
- Custom mappings and analyzers for relevance
- Document transformation/enrichment pipeline

## Example: Indexing Script
```js
const { Client } = require('@elastic/elasticsearch');
const client = new Client({ node: 'http://elasticsearch:9200' });

async function indexDocument(doc) {
  await client.index({
    index: 'visualdm',
    document: doc
  });
}
```

## Monitoring
- Monitor cluster health via _cluster/health API
- Set up alerts for node failures, disk usage, etc.

## Maintenance
- Reindex as needed for schema changes
- Scale StatefulSet for more capacity
- Backup indices regularly

## Query Processing and Ranking

- Query parsing and expansion: Handles synonyms, typo correction, and contextual expansion
- Relevance scoring: Uses Elasticsearch BM25, field boosts, and custom scoring
- Personalized ranking: Boosts results based on userId and behavior
- Faceted search: Aggregation queries for dynamic facets
- Performance: Caching, efficient filters, and pagination

### Example Usage
```ts
import { Client } from '@elastic/elasticsearch';
import { QueryProcessor } from './src/search/queryProcessor';

const client = new Client({ node: 'http://elasticsearch:9200' });
const qp = new QueryProcessor(client);
const results = await qp.search('magic adventure', 'user123', ['category', 'author']);
```

### Testing
- Unit tests for query expansion, scoring, and faceting
- Integration tests with real/synthetic queries
- Tune scoring and ranking based on test results 