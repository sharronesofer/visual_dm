# Migrating from API v1 to v2

This guide outlines the steps required to migrate your application from API v1 to v2. API v1 will be sunset on [DATE] and all applications should migrate to v2 before then.

## Breaking Changes

### 1. Response Envelope Format

#### V1 Format
```json
{
    "data": {},
    "status": "success",
    "message": null
}
```

#### V2 Format
```json
{
    "data": {},
    "metadata": {
        "status": "success",
        "message": null,
        "timestamp": "2024-03-21T10:30:00Z",
        "version": "v2"
    }
}
```

### 2. Relationship Endpoints

Relationship management has been moved to dedicated endpoints for better organization and functionality.

#### V1 Approach
```
POST /api/v1/npcs/{id}/factions/{faction_id}
DELETE /api/v1/npcs/{id}/factions/{faction_id}
```

#### V2 Approach
```
POST /api/v2/relationships/npcs/{id}/factions
{
    "faction_id": "string",
    "relationship_type": "member|ally|enemy",
    "metadata": {}
}

DELETE /api/v2/relationships/npcs/{id}/factions/{faction_id}
```

### 3. Pagination Metadata

#### V1 Format
```json
{
    "data": [],
    "total": 100,
    "page": 1,
    "per_page": 20
}
```

#### V2 Format
```json
{
    "data": [],
    "metadata": {
        "pagination": {
            "total_items": 100,
            "total_pages": 5,
            "current_page": 1,
            "items_per_page": 20,
            "has_next": true,
            "has_previous": false
        }
    }
}
```

## New Features in V2

1. **Batch Operations**
   - Support for creating, updating, and deleting multiple entities in a single request
   - Example: `POST /api/v2/npcs/batch`

2. **Enhanced Filtering**
   - More powerful query parameters for filtering collections
   - Support for complex logical operations (AND, OR)
   - Example: `GET /api/v2/npcs?status=active&faction=rebels&level[gte]=10`

3. **Improved Error Handling**
   - More detailed error responses with error codes
   - Validation errors include field-specific details
   - Example error response:
     ```json
     {
         "error": {
             "code": "validation_error",
             "message": "Invalid request parameters",
             "details": [
                 {
                     "field": "level",
                     "error": "must be between 1 and 100"
                 }
             ]
         }
     }
     ```

4. **Real-time Updates**
   - WebSocket support for real-time entity updates
   - Event streams for monitoring changes
   - Example: `ws://api.example.com/v2/npcs/{id}/updates`

## Migration Steps

1. **Update Base URL**
   - Change API base URL from `/api/v1` to `/api/v2`
   - Update any hardcoded version references

2. **Update Response Handling**
   - Modify response parsing to handle new envelope format
   - Update pagination handling for new metadata structure
   - Example:
     ```typescript
     // V1
     const { data, status } = response;
     
     // V2
     const { data, metadata } = response;
     const { status } = metadata;
     ```

3. **Update Relationship Management**
   - Move relationship operations to new dedicated endpoints
   - Update relationship payloads to include new fields
   - Example:
     ```typescript
     // V1
     await api.post(`/npcs/${npcId}/factions/${factionId}`);
     
     // V2
     await api.post(`/relationships/npcs/${npcId}/factions`, {
         faction_id: factionId,
         relationship_type: 'member'
     });
     ```

4. **Update Error Handling**
   - Modify error handling to process new error format
   - Add handling for new error codes
   - Example:
     ```typescript
     // V1
     try {
         await api.post('/npcs', data);
     } catch (error) {
         console.error(error.message);
     }
     
     // V2
     try {
         await api.post('/npcs', data);
     } catch (error) {
         if (error.code === 'validation_error') {
             error.details.forEach(detail => {
                 console.error(`${detail.field}: ${detail.error}`);
             });
         }
     }
     ```

5. **Test Migration**
   - Test all API interactions with v2 endpoints
   - Verify error handling works correctly
   - Check pagination and filtering still work
   - Validate relationship management functions

## Need Help?

If you need assistance with the migration:

1. Check our [API Documentation](https://api.example.com/docs)
2. Join our [Discord Community](https://discord.gg/example)
3. Contact support at api-support@example.com

## Feedback

We value your feedback on the v2 API. Please submit any issues or suggestions to our [GitHub repository](https://github.com/example/api/issues). 