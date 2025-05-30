import asyncio
from chunk_retriever_client.client import ChunkRetrieverClient

async def main():
    # Example 1: Invalid UUID
    response, errstr = await ChunkRetrieverClient.find_chunks_by_source_id(
        url="http://localhost", port=8010, source_id="not-a-uuid"
    )
    print("[Invalid UUID] Response:", response)
    print("[Invalid UUID] Error:", errstr)

    # Example 2: Unavailable server
    response, errstr = await ChunkRetrieverClient.find_chunks_by_source_id(
        url="http://localhost", port=9999, source_id="b7e2c4a0-1234-4f56-8abc-1234567890ab"
    )
    print("[Unavailable server] Response:", response)
    print("[Unavailable server] Error:", errstr)

    # Example 3: Wrong protocol
    response, errstr = await ChunkRetrieverClient.find_chunks_by_source_id(
        url="http://nonexistent", port=8010, source_id="b7e2c4a0-1234-4f56-8abc-1234567890ab"
    )
    print("[Wrong host] Response:", response)
    print("[Wrong host] Error:", errstr)

if __name__ == "__main__":
    asyncio.run(main()) 