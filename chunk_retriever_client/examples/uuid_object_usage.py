import asyncio
import uuid
from chunk_retriever_client.client import ChunkRetrieverClient

async def main():
    # Example 1: source_id as uuid.UUID object (valid)
    valid_uuid = uuid.UUID("b7e2c4a0-1234-4f56-8abc-1234567890ab")
    response, errstr = await ChunkRetrieverClient.find_chunks_by_source_id(
        url="http://localhost", port=8010, source_id=valid_uuid
    )
    print("[UUID object] Response:", response)
    print("[UUID object] Error:", errstr)

    # Example 2: source_id as string (valid)
    response, errstr = await ChunkRetrieverClient.find_chunks_by_source_id(
        url="http://localhost", port=8010, source_id="b7e2c4a0-1234-4f56-8abc-1234567890ab"
    )
    print("[UUID string] Response:", response)
    print("[UUID string] Error:", errstr)

    # Example 3: source_id as uuid.UUID (not version 4)
    not_v4 = uuid.UUID("b7e2c4a0-1234-4f56-8abc-1234567890aa")  # still v4, but let's try a wrong type
    response, errstr = await ChunkRetrieverClient.find_chunks_by_source_id(
        url="http://localhost", port=8010, source_id=not_v4
    )
    print("[UUID object, not v4] Response:", response)
    print("[UUID object, not v4] Error:", errstr)

    # Example 4: source_id as int (invalid)
    response, errstr = await ChunkRetrieverClient.find_chunks_by_source_id(
        url="http://localhost", port=8010, source_id=12345
    )
    print("[int as source_id] Response:", response)
    print("[int as source_id] Error:", errstr)

if __name__ == "__main__":
    asyncio.run(main()) 