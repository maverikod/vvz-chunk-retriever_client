#!/usr/bin/env python
"""
Пример использования обновленного клиента Vector Store.

Демонстрирует основные операции с использованием обновленного API:
- Создание записей (из вектора и из текста)
- Поиск записей (по вектору и по тексту)
- Фильтрация по метаданным
- Удаление записей
"""

import asyncio
import json
import logging
from datetime import datetime
from uuid import uuid4

from vector_store_client import VectorStoreClient, create_client

# Настройка логирования для демонстрации работы
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """Основная функция примера."""
    # Создание клиента с инициализацией
    client = await create_client(base_url="http://localhost:8007")
    
    # Проверка подключения и версии сервиса
    health_info = await client.health()
    logger.info(f"Сервис активен: {health_info}")
    
    # Получение информации о доступных командах
    help_info = await client.help()
    logger.info(f"Доступные команды: {', '.join(cmd for cmd in help_info['commands'])}")
    
    # Создание записи из текста (автоматическое векторизованиe)
    record_id_1 = await client.create_text_record(
        text="Это пример текста для векторизации в обновленном API",
        metadata={
            "type": "example",
            "category": "documentation",
            "tags": ["vector", "store", "api", "updated"]
        }
    )
    logger.info(f"Запись из текста создана, ID: {record_id_1}")
    
    # Создание записи из готового вектора (384 размерности)
    # Для примера создадим случайный вектор
    import numpy as np
    random_vector = list(np.random.random(384).astype(float))
    
    record_id_2 = await client.create_record(
        vector=random_vector,
        metadata={
            "type": "example",
            "category": "test",
            "source": "random",
            "timestamp": datetime.now().isoformat()
        }
    )
    logger.info(f"Запись из вектора создана, ID: {record_id_2}")
    
    # Поиск по тексту
    text_search_results = await client.search_text_records(
        text="векторизация API",
        limit=5,
        include_metadata=True
    )
    
    logger.info(f"Найдено {len(text_search_results)} записей по тексту:")
    for i, result in enumerate(text_search_results, 1):
        logger.info(f"{i}. ID: {result.id}, Оценка: {result.score:.4f}")
        if result.metadata:
            logger.info(f"   Метаданные: {json.dumps(result.metadata, ensure_ascii=False)}")
    
    # Фильтрация записей по метаданным
    filter_results = await client.filter_records(
        metadata_filter={"type": "example"},
        limit=10
    )
    
    logger.info(f"Найдено {len(filter_results)} записей по фильтру:")
    for i, result in enumerate(filter_results, 1):
        logger.info(f"{i}. ID: {result.id}")
        if result.metadata:
            logger.info(f"   Категория: {result.metadata.get('category', 'не указана')}")
    
    # Получение метаданных записи
    metadata = await client.get_metadata(record_id_1)
    logger.info(f"Метаданные записи {record_id_1}: {json.dumps(metadata, ensure_ascii=False)}")
    
    # Получение текста записи (если доступно)
    try:
        text = await client.get_text(record_id_1)
        logger.info(f"Текст записи {record_id_1}: {text}")
    except Exception as e:
        logger.error(f"Не удалось получить текст: {e}")
    
    # Поиск по вектору с фильтрацией по метаданным
    vector_search_results = await client.search_records(
        vector=random_vector,
        limit=5,
        filter_criteria={"category": "test"}
    )
    
    logger.info(f"Найдено {len(vector_search_results)} записей по вектору с фильтрацией:")
    for i, result in enumerate(vector_search_results, 1):
        logger.info(f"{i}. ID: {result.id}, Оценка: {result.score:.4f}")
    
    # Удаление записей
    if len(filter_results) > 0:
        record_to_delete = str(filter_results[0].id)
        delete_result = await client.delete(record_id=record_to_delete)
        logger.info(f"Удаление записи {record_to_delete}: {'успешно' if delete_result else 'не удалось'}")
    
    # Массовое удаление
    if len(filter_results) >= 2:
        records_to_delete = [str(result.id) for result in filter_results[1:3]]
        delete_result = await client.delete(
            record_ids=records_to_delete,
            confirm=True
        )
        logger.info(f"Массовое удаление записей: {'успешно' if delete_result else 'не удалось'}")
    
    # Удаление по фильтру (с подтверждением и лимитом)
    delete_result = await client.delete(
        filter={"type": "example", "category": "test"},
        max_records=5,
        confirm=True
    )
    logger.info(f"Удаление по фильтру: {'успешно' if delete_result else 'не удалось'}")

if __name__ == "__main__":
    asyncio.run(main()) 