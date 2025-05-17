# Legacy Emotion Data Migration

This directory contains scripts for migrating legacy emotion data to the new unified emotion API.

## migrate_legacy_emotions.js

A Node.js script that reads legacy emotion data from a JSON file, transforms it to the new format, and uploads it to the new API using the EmotionApiAdapter.

### Usage

```sh
node migrate_legacy_emotions.js legacy_emotions.json http://localhost:3000/api
```

- `legacy_emotions.json`: Path to a JSON file containing an array of legacy emotion objects (e.g., `[ { "name": "joy", "value": 0.8 }, ... ]`)
- `http://localhost:3000/api`: Base URL of the new emotion API

### Assumptions
- Legacy data must have at least a `name` and `value` or `intensity` field.
- The script maps legacy fields to the new API format. Update `transformLegacyEmotion()` as needed for custom mappings.

### Troubleshooting
- Ensure the API server is running and accessible.
- Check for network/firewall issues if requests fail.
- Review error messages for failed migrations and update the mapping logic if needed.

### Roadmap
- Add support for batch/parallel uploads
- Add rollback and dry-run options
- Provide migration scripts for other data sources (databases, CSV, etc.) 