import asyncio
from chunk_retriever_client.client import ChunkRetrieverClient
from chunk_metadata_adapter import FlatSemanticChunk

async def main():
    response, errstr = await ChunkRetrieverClient.find_chunks_by_source_id(
        url="http://localhost", port=8010, source_id="b7e2c4a0-1234-4f56-8abc-1234567890ab"
    )
    print("Response:", response)
    if response and "chunks" in response:
        for chunk in response["chunks"]:
            FlatSemanticChunk(**chunk)
    print("Error:", errstr)

if __name__ == "__main__":
    asyncio.run(main()) 