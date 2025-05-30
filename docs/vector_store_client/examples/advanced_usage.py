#!/usr/bin/env python
"""
Advanced usage examples for Vector Store Client

This example demonstrates more advanced features of the Vector Store Client:
- Batch operations
- Complex metadata filtering
- Vector similarity search with filtering
- Error handling and retry strategies
- Configuration access
"""

import asyncio
import json
import logging
import uuid
from typing import List, Dict, Any
import numpy as np
import random
from datetime import datetime, timedelta

from vector_store_client import (
    VectorStoreClient, 
    create_client,
    ValidationError,
    ResourceNotFoundError,
    JsonRpcException,
    ConnectionError,
    TimeoutError,
    AuthenticationError
)

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global settings
SERVER_URL = "http://localhost:8007"
BATCH_SIZE = 10  # Number of records to create in batch
VECTOR_DIM = 384  # Dimension of vectors (depends on your model)


async def batch_create_records(client: VectorStoreClient) -> List[str]:
    """Create multiple records in a batch and return their IDs.
    
    Demonstrates creating multiple records efficiently.
    """
    record_ids = []
    session_id = str(uuid.uuid4())
    
    # Generate random text documents with varied metadata
    categories = ["article", "document", "message", "note", "reference"]
    sources = ["example", "test", "sample", "demo"]
    
    logger.info(f"Creating {BATCH_SIZE} records in batch (session: {session_id})")
    
    try:
        # Create multiple records in sequence
        for i in range(BATCH_SIZE):
            # Create varied metadata
            category = random.choice(categories)
            source = random.choice(sources)
            tags = random.sample(["text", "vector", "search", "example", "test", "batch"], 
                               k=random.randint(1, 3))
            
            # Create record with timestamp spread over last 30 days
            days_ago = random.randint(0, 30)
            timestamp = (datetime.now() - timedelta(days=days_ago)).isoformat()
            
            # Different record types for demonstration
            if i % 3 == 0:
                # Create from text
                text = f"Sample document #{i} for advanced vector store testing. This is a {category} from {source}."
                record_id = await client.create_text_record(
                    text=text,
                    metadata={
                        "type": category,
                        "source": source,
                        "tags": tags,
                        "index": i,
                        "created_by": "advanced_example.py",
                        "priority": random.randint(1, 5)
                    },
                    session_id=session_id,
                    timestamp=timestamp
                )
            else:
                # Create from vector
                vector = list(np.random.random(VECTOR_DIM).astype(float))
                record_id = await client.create_record(
                    vector=vector,
                    metadata={
                        "type": category,
                        "source": source,
                        "tags": tags,
                        "index": i,
                        "body": f"Vector record #{i} for advanced testing",  # Required by the server
                        "created_by": "advanced_example.py",
                        "is_vector_only": True,
                        "priority": random.randint(1, 5)
                    },
                    session_id=session_id,
                    timestamp=timestamp
                )
            
            record_ids.append(record_id)
            
        logger.info(f"Successfully created {len(record_ids)} records")
        return record_ids
        
    except ValidationError as e:
        logger.error(f"Validation error in batch creation: {e}")
    except JsonRpcException as e:
        logger.error(f"API error in batch creation: {e.message} (code: {e.code})")
    except Exception as e:
        logger.error(f"Unexpected error in batch creation: {e}")
        
    return record_ids


async def complex_metadata_filtering(client: VectorStoreClient, session_id: str) -> None:
    """Demonstrate complex metadata filtering capabilities.
    
    Shows how to use more complex filtering criteria.
    """
    logger.info("=== Complex Metadata Filtering ===")
    
    # Filter by session and priority range
    try:
        logger.info("Finding high priority records (4-5) in session")
        high_priority_filter = {
            "session_id": session_id,
            "priority": {"$gte": 4}  # Priority >= 4
        }
        
        results = await client.filter_records(
            metadata_filter=high_priority_filter,
            limit=5
        )
        
        logger.info(f"Found {len(results)} high priority records")
        for i, result in enumerate(results, 1):
            if result.metadata:
                logger.info(f"{i}. ID: {result.id}, " +
                           f"Type: {result.metadata.get('type')}, " +
                           f"Priority: {result.metadata.get('priority')}")
    
    except Exception as e:
        logger.error(f"Error in priority filtering: {e}")
    
    # Filter by type and tags
    try:
        logger.info("Finding documents tagged with 'vector'")
        tag_filter = {
            "session_id": session_id,
            "type": "document",
            "tags": {"$contains": "vector"}
        }
        
        results = await client.filter_records(
            metadata_filter=tag_filter,
            limit=10
        )
        
        logger.info(f"Found {len(results)} documents with 'vector' tag")
        for i, result in enumerate(results, 1):
            if result.metadata:
                logger.info(f"{i}. ID: {result.id}, " +
                           f"Tags: {result.metadata.get('tags')}")
    
    except Exception as e:
        logger.error(f"Error in tag filtering: {e}")


async def vector_search_with_filter(client: VectorStoreClient, session_id: str) -> None:
    """Demonstrate vector similarity search with metadata filtering.
    
    Shows how to combine vector search with metadata filters.
    """
    logger.info("=== Vector Search with Filtering ===")
    
    try:
        # Create a query vector
        query_vector = list(np.random.random(VECTOR_DIM).astype(float))
        
        # Search with metadata filter
        filter_criteria = {
            "session_id": session_id,
            "type": {"$in": ["article", "document"]}  # Only these types
        }
        
        logger.info("Searching with vector and metadata filter (type=article or document)")
        results = await client.search_records(
            vector=query_vector,
            limit=5,
            include_metadata=True,
            filter_criteria=filter_criteria
        )
        
        logger.info(f"Found {len(results)} matching records")
        for i, result in enumerate(results, 1):
            logger.info(f"{i}. ID: {result.id}, Score: {result.score:.4f}")
            if result.metadata:
                logger.info(f"   Type: {result.metadata.get('type')}, " +
                           f"Source: {result.metadata.get('source')}")
    
    except ValidationError as e:
        logger.error(f"Validation error in vector search: {e}")
    except JsonRpcException as e:
        logger.error(f"API error in vector search: {e.message} (code: {e.code})")


async def batch_delete(client: VectorStoreClient, session_id: str) -> None:
    """Delete multiple records in batch using session ID.
    
    Shows how to clean up multiple records at once.
    """
    logger.info("=== Batch Deletion ===")
    
    try:
        # First check how many records will be affected
        count_filter = {"session_id": session_id}
        records = await client.filter_records(
            metadata_filter=count_filter,
            limit=100
        )
        
        total_records = len(records)
        logger.info(f"Found {total_records} records to delete")
        
        if total_records == 0:
            logger.warning("No records to delete")
            return
            
        # Delete all records with this session ID
        result = await client.delete(
            filter={"session_id": session_id},
            max_records=total_records,
            confirm=True  # Must be True for batch deletion
        )
        
        logger.info(f"Batch deletion result: {result}")
        
        # Verify deletion
        remaining = await client.filter_records(
            metadata_filter=count_filter,
            limit=10
        )
        
        logger.info(f"Remaining records after deletion: {len(remaining)}")
    
    except ValidationError as e:
        logger.error(f"Validation error in batch deletion: {e}")
    except JsonRpcException as e:
        logger.error(f"API error in batch deletion: {e.message} (code: {e.code})")


async def access_configuration(client: VectorStoreClient) -> None:
    """Access and display service configuration (if permissions allow).
    
    Shows how to interact with server configuration.
    """
    logger.info("=== Service Configuration ===")
    
    try:
        # Get current configuration
        config = await client.config(operation="get")
        logger.info("Service configuration:")
        logger.info(json.dumps(config, indent=2, sort_keys=True))
        
        # Get specific configuration path
        try:
            server_config = await client.config(operation="get", path="server")
            logger.info(f"Server configuration: {server_config}")
        except Exception as e:
            logger.warning(f"Could not get server configuration: {e}")
            
    except AuthenticationError:
        logger.error("Not authorized to access configuration")
    except JsonRpcException as e:
        logger.error(f"API error accessing configuration: {e.message} (code: {e.code})")


async def error_handling_demo(client: VectorStoreClient) -> None:
    """Demonstrate error handling with deliberate errors.
    
    Shows how the client handles various error conditions.
    """
    logger.info("=== Error Handling Demonstration ===")
    
    # 1. Try to get a non-existent record
    try:
        logger.info("Attempting to get non-existent record...")
        fake_uuid = str(uuid.uuid4())
        await client.get_metadata(fake_uuid)
    except ResourceNotFoundError as e:
        logger.info(f"✓ Correctly handled not found error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error type: {e}")
    
    # 2. Send invalid parameters
    try:
        logger.info("Sending invalid parameters...")
        # Empty vector is invalid
        await client.search_by_vector(vector=[])
    except ValidationError as e:
        logger.info(f"✓ Correctly handled validation error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error type: {e}")
    
    # 3. Try to delete without confirmation
    try:
        logger.info("Attempting batch delete without confirmation...")
        await client.delete(
            filter={"type": "example"},
            confirm=False  # Missing required confirmation
        )
    except ValidationError as e:
        logger.info(f"✓ Correctly handled missing confirmation error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error type: {e}")


async def main():
    """Main function running the advanced examples."""
    # Create client with connection to the service
    try:
        client = await create_client(
            base_url=SERVER_URL,
            timeout=30.0,  # Increased timeout for batch operations
            max_retries=3   # Automatic retries for transient errors
        )
        logger.info(f"Connected to Vector Store service at {SERVER_URL}")
    except ConnectionError as e:
        logger.error(f"Failed to connect to Vector Store service: {e}")
        return
    
    try:
        # Get service information
        health = await client.health()
        logger.info(f"Service: {health.get('version', 'unknown')}, Model: {health.get('model', 'unknown')}")
        
        # Generate a session ID for this run to group records
        session_id = str(uuid.uuid4())
        logger.info(f"Using session ID: {session_id}")
        
        # Create batch records
        record_ids = await batch_create_records(client)
        if not record_ids:
            logger.warning("No records created, exiting")
            return
            
        # Run the advanced examples
        await complex_metadata_filtering(client, session_id)
        await vector_search_with_filter(client, session_id)
        await error_handling_demo(client)
        await access_configuration(client)
        
        # Clean up
        await batch_delete(client, session_id)
        
        logger.info("Advanced examples completed successfully")
    
    finally:
        # Close the client session
        await client._client.aclose()
        logger.info("Client session closed")


if __name__ == "__main__":
    asyncio.run(main()) 