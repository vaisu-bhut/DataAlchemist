# Analytics Agent

Provides metrics and statistics API for chat conversations, issues, and agent performance.

## Endpoints

### Summary Metrics
```
GET /api/v1/analytics/summary
```
Returns high-level overview including:
- Total conversations, issues, solutions, agents, customers
- Average resolution time
- Top 5 issues
- Top 5 performing agents

### Issue Distribution
```
GET /api/v1/analytics/issues/distribution?limit=10
```
Returns top issues by occurrence count.

### Trending Issues
```
GET /api/v1/analytics/issues/trending?days=7
```
Returns issues that are trending in the last N days.

### Agent Performance
```
GET /api/v1/analytics/agents/performance?limit=10
```
Returns agent performance metrics including:
- Total chats handled
- Resolution rate
- Top issues they handle

### Agent Specialization
```
GET /api/v1/analytics/agents/{agent_id}/specialization
```
Returns what issues a specific agent handles most and their success rate.

## Running

The service runs on port 8004 and is included in docker-compose.yml.

```bash
docker-compose up analytics-agent
```

## Health Check
```
GET /health
```
