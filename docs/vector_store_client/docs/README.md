# Vector Store Client

A client for interacting with the Vector Store service, providing a convenient interface for working with vector embeddings.

## Features

- Full-featured API for Vector Store operations
- Asynchronous interface based on `httpx`
- Automatic parameter handling and validation
- Comprehensive error management
- Support for all key operations:
  - Creating records from text or vectors
  - Vector similarity search
  - Metadata filtering
  - Record management
  - Service monitoring and configuration

## Installation

```bash
pip install vector-store-client
```

Or install from source:

```bash
git clone https://github.com/username/vector-store-client.git
cd vector-store-client
pip install -e .
```

## Quick Start

```python
import asyncio
from vector_store_client import create_client

async def main():
    # Create client with connection to the service
    client = await create_client(base_url="http://localhost:8007")
    
    # Check service health
    health = await client.health()
    print(f"Service is healthy: {health['status'] == 'ok'}")
    
    # Create a record from text
    record_id = await client.create_text_record(
        text="Example text for vectorization",
        metadata={"type": "example", "tags": ["test", "vector"]}
    )
    print(f"Created record with ID: {record_id}")
    
    # Search for similar records
    results = await client.search_text_records(
        text="vectorization example",
        limit=5
    )
    
    print(f"Found {len(results)} similar records:")
    for i, result in enumerate(results, 1):
        print(f"{i}. ID: {result.id}, Similarity: {result.score:.4f}")
    
    # Close the session
    await client._client.aclose()

# Run the async function
if __name__ == "__main__":
    asyncio.run(main())
```

## Core Functionality

### Creating a Client

```python
from vector_store_client import create_client

# Simple creation
client = await create_client(base_url="http://localhost:8007")

# With advanced parameters
client = await create_client(
    base_url="http://localhost:8007",
    timeout=30.0,  # Request timeout in seconds
    headers={"Authorization": "Bearer YOUR_TOKEN"},  # Additional headers
    max_retries=3  # Number of retries for failed requests
)
```

### Record Management

#### Creating a Record from Text

```python
record_id = await client.create_text_record(
    text="Text for vectorization",
    metadata={  # Optional metadata
        "type": "document",
        "source": "example",
        "tags": ["test", "example"]
    },
    model="text-embedding-3-small",  # Optional embedding model
    session_id="session-uuid",  # Optional
    timestamp="2023-04-25T10:30:00Z"  # Optional
)
```

#### Creating a Record from a Vector

```python
import numpy as np

# Create a vector (dimension should match your model)
vector = list(np.random.random(384).astype(float))

record_id = await client.create_record(
    vector=vector,
    metadata={
        "type": "vector",
        "source": "custom",
        "body": "Text content or description for this vector"  # 'body' field is required
    }
)
```

> **Note**: The API requires a 'body' field in the metadata when creating a record with a vector. If not provided, the client will automatically add a default value.

#### Getting Record Data

```python
# Get metadata
metadata = await client.get_metadata("record-uuid")

# Get text (if available)
text = await client.get_text("record-uuid")
```

#### Deleting Records

```python
# Delete a single record
await client.delete(record_id="record-uuid")

# Delete multiple records
await client.delete(
    record_ids=["id1", "id2", "id3"],
    confirm=True  # Required for deleting multiple records
)

# Delete by metadata filter
await client.delete(
    filter={"type": "test", "source": "example"},
    max_records=100,  # Limit for safety
    confirm=True  # Required for bulk deletion
)
```

### Search and Filtering

#### Text Search

```python
results = await client.search_text_records(
    text="search query",
    limit=10,  # Maximum number of results
    model="text-embedding-3-small",  # Optional
    include_vectors=False,  # Include vectors in results
    include_metadata=True,  # Include metadata in results
    metadata_filter={"type": "document"}  # Filter by metadata
)

for result in results:
    print(f"ID: {result.id}, Similarity: {result.score}")
    print(f"Metadata: {result.metadata}")
```

#### Vector Search

```python
results = await client.search_by_vector(
    vector=your_vector,  # Query vector
    limit=10,
    include_vectors=False,
    include_metadata=True
)
```

#### Vector Search with Filtering

```python
results = await client.search_records(
    vector=your_vector,
    limit=10,
    include_metadata=True,
    filter_criteria={
        "type": "document",
        "tags": {"$contains": "important"}
    }
)
```

#### Metadata Filtering

```python
results = await client.filter_records(
    metadata_filter={
        "type": "document",
        "source": "database",
        "created_at": {"$gt": "2023-01-01T00:00:00Z"}
    },
    limit=100
)
```

### Complex Filters

The client supports various filter operators:

- `$eq` - equals
- `$ne` - not equals
- `$gt`, `$gte` - greater than, greater than or equal
- `$lt`, `$lte` - less than, less than or equal
- `$in` - in list
- `$nin` - not in list
- `$contains` - contains element (for arrays)
- `$startswith`, `$endswith` - starts with, ends with (for strings)

Examples:

```python
# Records with priority >= 3
filter_criteria = {"priority": {"$gte": 3}}

# Records with specific sources
filter_criteria = {"source": {"$in": ["database", "api", "file"]}}

# Records with "important" tag in tags array
filter_criteria = {"tags": {"$contains": "important"}}

# String values starting with "doc"
filter_criteria = {"type": {"$startswith": "doc"}}
```

### Service Management

```python
# Health check
health = await client.health()

# Get configuration
config = await client.config(operation="get")

# Get value by path
storage_config = await client.config(operation="get", path="storage")

# Set value (if allowed)
result = await client.config(
    operation="set",
    path="server.max_records_per_request",
    value=1000
)

# Get help information
help_info = await client.help()
```

## Error Handling

```python
from vector_store_client import (
    ValidationError,
    ResourceNotFoundError,
    JsonRpcException,
    ConnectionError,
    TimeoutError,
    AuthenticationError
)

try:
    await client.get_metadata("non-existent-id")
except ResourceNotFoundError as e:
    print(f"Record not found: {e}")
except ValidationError as e:
    print(f"Validation error: {e}")
except JsonRpcException as e:
    print(f"API error: {e.message} (code: {e.code})")
except ConnectionError as e:
    print(f"Connection error: {e}")
except TimeoutError as e:
    print(f"Request timeout: {e}")
```

## Advanced Examples

### Batch Record Creation

```python
import uuid
from datetime import datetime

# Create a session for grouping records
session_id = str(uuid.uuid4())

# Create multiple records
for i in range(10):
    await client.create_text_record(
        text=f"Document #{i} for testing",
        metadata={
            "index": i,
            "batch": "test-batch",
            "created_at": datetime.now().isoformat()
        },
        session_id=session_id
    )

# Find all records from the session
batch_results = await client.filter_records(
    metadata_filter={"session_id": session_id}
)
```

### Working with Assistant and Chat Sessions

```python
# Session and message IDs for linking records
session_id = str(uuid.uuid4())
message_id = str(uuid.uuid4())

# Save user query
user_record_id = await client.create_text_record(
    text="Explain how vector embeddings work",
    metadata={
        "role": "user",
        "type": "message",
        "conversation": "embeddings"
    },
    session_id=session_id,
    message_id=message_id
)

# Save assistant response
assistant_record_id = await client.create_text_record(
    text="Vector embeddings are numerical representations...",
    metadata={
        "role": "assistant",
        "type": "message",
        "conversation": "embeddings"
    },
    session_id=session_id,
    message_id=str(uuid.uuid4())  # New message ID
)

# Get the entire session history
conversation = await client.filter_records(
    metadata_filter={"session_id": session_id},
    limit=100
)

# Sort messages by timestamp
conversation_sorted = sorted(
    conversation, 
    key=lambda x: x.metadata.get("timestamp", "") if x.metadata else ""
)
```

## Common Errors

### Connection Issues

- **Error**: `ConnectionError: Failed to connect to Vector Store service`
  **Solution**: Verify that the Vector Store service is running and accessible at the specified URL. Check network settings and access permissions.

### Validation Errors

- **Error**: `ValidationError: Invalid session_id format`
  **Solution**: Ensure that session_id is a valid UUID.

- **Error**: `ValidationError: Limit must be between 1 and 100`
  **Solution**: The limit value must be within the valid range.

- **Error**: `JsonRpcException: Missing or empty 'body' field`
  **Solution**: When creating a record with `create_record`, include a 'body' field in the metadata. This is required by the server. If not provided, the client will automatically add a default value.

### API Errors

- **Error**: `JsonRpcException: Invalid params (code: -32602)`
  **Solution**: Check the correctness of your request parameters.

- **Error**: `ResourceNotFoundError: Record with ID ... not found`
  **Solution**: The requested record doesn't exist or has been deleted.

- **Error**: `AuthenticationError: Not authorized to access configuration`
  **Solution**: Special permissions are required to access service configuration.

## Performance and Optimization

### Client Reuse

```python
# Create client once and reuse it for all requests
client = await create_client(base_url="http://localhost:8007")

# Use context manager for automatic session closing
async with await create_client(base_url="http://localhost:8007") as client:
    # Use client here
    await client.health()
```

### Batch Processing

When working with large numbers of records:
- Group records by session_id for easier management
- Use metadata filtering instead of loading all records
- For bulk deletion, use filters to delete groups of records

## License

MIT 