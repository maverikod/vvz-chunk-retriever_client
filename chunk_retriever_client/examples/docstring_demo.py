"""
Example: How to use ChunkRetrieverClient to fetch chunks by source_id.

This script demonstrates the typical workflow and error handling.
"""
import asyncio
from chunk_retriever_client.client import ChunkRetrieverClient

async def main():
    """
    Run a request to the Chunk Retriever and print the result.
    """
    # Replace with your actual source_id
    source_id = "b7e2c4a0-1234-4f56-8abc-1234567890ab"
    response, errstr = await ChunkRetrieverClient.find_chunks_by_source_id(
        url="http://localhost", port=8010, source_id=source_id
    )
    if errstr:
        print(f"Error occurred: {errstr}")
    else:
        print("Chunks found:")
        print(response)

if __name__ == "__main__":
    asyncio.run(main()) 