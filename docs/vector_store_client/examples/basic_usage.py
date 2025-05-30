#!/usr/bin/env python
"""
Basic example of using Vector Store Client

This example demonstrates the main functionality of the Vector Store Client:
- Connecting to the service
- Creating records (both from text and vector)
- Searching by text and vector
- Filtering by metadata
- Error handling
"""

import asyncio
import json
import logging
import uuid
from typing import List, Dict
import numpy as np
from datetime import datetime

from vector_store_client import (
    VectorStoreClient, 
    create_client,
    ValidationError,
    ResourceNotFoundError,
    JsonRpcException,
    ConnectionError
)

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global settings
SERVER_URL = "http://localhost:8007"  # Update this to your server URL


async def check_service_health(client: VectorStoreClient) -> bool:
    """Check if the service is healthy and return status."""
    try:
        health = await client.health()
        logger.info(f"Service is {'healthy' if health['status'] == 'ok' else 'unhealthy'}")
        logger.info(f"Active model: {health['model']}")
        logger.info(f"Service version: {health['version']}")
        return health['status'] == 'ok'
    except ConnectionError as e:
        logger.error(f"Could not connect to the service: {e}")
        return False
    except Exception as e:
        logger.error(f"Error checking service health: {e}")
        return False


async def create_sample_records(client: VectorStoreClient) -> Dict[str, str]:
    """Create sample records for testing and return their IDs."""
    record_ids = {}
    
    # Create a record from text (will be automatically vectorized)
    try:
        text_record_id = await client.create_text_record(
            text="This is a sample text for testing vector search capabilities",
            metadata={
                "type": "example",
                "category": "documentation",
                "tags": ["sample", "test", "vector", "search"],
                "created_by": "basic_example.py"
            }
        )
        logger.info(f"Created text record with ID: {text_record_id}")
        record_ids["text"] = text_record_id
    except ValidationError as e:
        logger.error(f"Validation error creating text record: {e}")
    except JsonRpcException as e:
        logger.error(f"API error creating text record: {e.message} (code: {e.code})")
    
    # Create a record with custom vector
    try:
        # Generate a random vector of correct dimensionality (e.g., 384 for many embedding models)
        vector = list(np.random.random(384).astype(float))
        vector_record_id = await client.create_record(
            vector=vector,
            metadata={
                "type": "example",
                "category": "test",
                "source": "random",
                "body": "Vector record for testing purposes",  # Required by the server
                "timestamp": datetime.now().isoformat(),
                "session_id": str(uuid.uuid4()),
                "created_by": "basic_example.py"
            }
        )
        logger.info(f"Created vector record with ID: {vector_record_id}")
        record_ids["vector"] = vector_record_id
    except ValidationError as e:
        logger.error(f"Validation error creating vector record: {e}")
    except JsonRpcException as e:
        logger.error(f"API error creating vector record: {e.message} (code: {e.code})")
    
    return record_ids


async def search_by_text(client: VectorStoreClient, query_text: str) -> None:
    """Search records by text similarity."""
    try:
        logger.info(f"Searching for records similar to text: '{query_text}'")
        results = await client.search_text_records(
            text=query_text,
            limit=5,
            include_metadata=True  # Include metadata in results
        )
        
        logger.info(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            logger.info(f"{i}. ID: {result.id}, Score: {result.score:.4f}")
            if result.metadata:
                logger.info(f"   Metadata: {json.dumps(result.metadata, ensure_ascii=False)}")
    except ValidationError as e:
        logger.error(f"Validation error in text search: {e}")
    except JsonRpcException as e:
        logger.error(f"API error in text search: {e.message} (code: {e.code})")


async def search_with_metadata_filter(client: VectorStoreClient) -> None:
    """Search records with metadata filtering."""
    try:
        logger.info("Searching records with metadata filter (type=example)")
        results = await client.filter_records(
            metadata_filter={"type": "example"},
            limit=10
        )
        
        logger.info(f"Found {len(results)} records:")
        for i, result in enumerate(results, 1):
            logger.info(f"{i}. ID: {result.id}")
            category = result.metadata.get("category", "not specified") if result.metadata else "no metadata"
            logger.info(f"   Category: {category}")
    except ValidationError as e:
        logger.error(f"Validation error in filter search: {e}")
    except JsonRpcException as e:
        logger.error(f"API error in filter search: {e.message} (code: {e.code})")


async def get_record_details(client: VectorStoreClient, record_id: str) -> None:
    """Get metadata and text (if available) for a specific record."""
    # Get metadata
    try:
        metadata = await client.get_metadata(record_id)
        logger.info(f"Metadata for record {record_id}:")
        logger.info(json.dumps(metadata, indent=2, ensure_ascii=False))
    except ResourceNotFoundError:
        logger.error(f"Record {record_id} not found")
    except JsonRpcException as e:
        logger.error(f"API error getting metadata: {e.message} (code: {e.code})")
    
    # Get text (this might fail if the record doesn't have text)
    try:
        text = await client.get_text(record_id)
        logger.info(f"Text for record {record_id}: {text}")
    except ResourceNotFoundError:
        logger.warning(f"Record {record_id} doesn't have text content")
    except JsonRpcException as e:
        logger.error(f"API error getting text: {e.message} (code: {e.code})")


async def delete_record(client: VectorStoreClient, record_id: str) -> None:
    """Delete a specific record."""
    try:
        logger.info(f"Deleting record {record_id}")
        result = await client.delete(record_id=record_id)
        logger.info(f"Delete operation result: {result}")
    except ResourceNotFoundError:
        logger.error(f"Record {record_id} not found for deletion")
    except ValidationError as e:
        logger.error(f"Validation error in delete: {e}")
    except JsonRpcException as e:
        logger.error(f"API error in delete: {e.message} (code: {e.code})")


async def main():
    """Main example function demonstrating Vector Store Client usage."""
    # Create client with connection to the service
    try:
        client = await create_client(base_url=SERVER_URL)
        logger.info(f"Connected to Vector Store service at {SERVER_URL}")
    except ConnectionError as e:
        logger.error(f"Failed to connect to Vector Store service: {e}")
        return
    
    try:
        # Check service health
        if not await check_service_health(client):
            logger.error("Service is not healthy, exiting")
            return
        
        # Create sample records
        record_ids = await create_sample_records(client)
        if not record_ids:
            logger.warning("No records created, exiting")
            return
        
        # Search by text
        await search_by_text(client, "vector search capabilities")
        
        # Search with metadata filter
        await search_with_metadata_filter(client)
        
        # Get record details
        if "text" in record_ids:
            await get_record_details(client, record_ids["text"])
        
        # Clean up (delete one record)
        if "vector" in record_ids:
            await delete_record(client, record_ids["vector"])
        
        logger.info("Example completed successfully")
    
    finally:
        # Close the client session
        await client._client.aclose()
        logger.info("Client session closed")


if __name__ == "__main__":
    asyncio.run(main()) 