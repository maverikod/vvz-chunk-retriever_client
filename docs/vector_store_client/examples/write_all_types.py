import asyncio
from vector_store_client.client import VectorStoreClient
import random

async def main():
    client = await VectorStoreClient.create(base_url="http://localhost:8007")

    # 1. create_text_record
    messages = [
        "Первое тестовое сообщение",
        "Второе тестовое сообщение",
        "Третье тестовое сообщение"
    ]
    metadata = {"source": "test", "project": "vector-store"}
    print("Запись текстовых сообщений:")
    for msg in messages:
        record_id = await client.create_text_record(
            text=msg,
            metadata=metadata
        )
        print(f"  text_record: '{msg}' -> id: {record_id}")

    # 2. create_record (с вектором)
    print("\nЗапись векторов:")
    for i in range(2):
        vector = [random.random() for _ in range(384)]
        meta = {"source": "test", "type": "vector", "index": i}
        record_id = await client.create_record(
            vector=vector,
            metadata=meta
        )
        print(f"  vector_record {i}: id: {record_id}")

    # 3. create_text_record с расширенными метаданными
    print("\nЗапись с расширенными метаданными:")
    record_id = await client.create_text_record(
        text="Сообщение с расширенными метаданными",
        metadata={
            "source": "test",
            "project": "vector-store",
            "custom": "value",
            "tags": ["example", "test"]
        },
        model={"name": "test-model"}
    )
    print(f"  text_record (расширенный): id: {record_id}")

    await client._client.aclose()

if __name__ == "__main__":
    asyncio.run(main()) 