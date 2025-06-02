import asyncio
from chunk_retriever_client.client import ChunkRetrieverClient
from chunk_metadata_adapter import FlatSemanticChunk

async def fetch(source_id):
    response, errstr = await ChunkRetrieverClient.find_chunks_by_source_id(
        url="http://localhost", port=8010, source_id=source_id
    )
    print(f"[source_id={source_id}] Response:", response)
    if response and "chunks" in response:
        for chunk in response["chunks"]:
            FlatSemanticChunk(**chunk)
    print(f"[source_id={source_id}] Error:", errstr)

async def main():
    source_ids = [
        "b7e2c4a0-1234-4f56-8abc-1234567890ab",
        "c7e2c4a0-1234-4f56-8abc-1234567890ab",
        "not-a-uuid"
    ]
    await asyncio.gather(*(fetch(sid) for sid in source_ids))

if __name__ == "__main__":
    asyncio.run(main()) 