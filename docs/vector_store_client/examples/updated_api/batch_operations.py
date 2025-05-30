#!/usr/bin/env python
"""
Пример пакетных операций с обновленным клиентом Vector Store.

Демонстрирует:
- Массовое создание записей
- Фильтрацию по сложным условиям
- Массовое удаление
"""

import asyncio
import json
import logging
import random
from datetime import datetime, timedelta
from uuid import uuid4

from vector_store_client import create_client

# Настройка логирования
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Категории для примера
CATEGORIES = ["documents", "articles", "notes", "emails", "books"]
TAGS = ["business", "personal", "work", "research", "education", "important", "draft"]
SOURCES = ["web", "database", "user", "api", "system"]

async def generate_records(client, count=20):
    """Генерирует и создает набор тестовых записей."""
    import numpy as np
    
    record_ids = []
    
    # Создаем заданное количество записей
    for i in range(count):
        # Генерируем случайные метаданные
        category = random.choice(CATEGORIES)
        tags = random.sample(TAGS, random.randint(1, 3))
        source = random.choice(SOURCES)
        
        # Создаем случайную дату за последний месяц
        days_ago = random.randint(0, 30)
        creation_date = (datetime.now() - timedelta(days=days_ago)).isoformat()
        
        # Генерируем случайный текст
        text = f"Пример записи {i+1} в категории {category} из источника {source}"
        
        # Добавляем приоритет для демонстрации фильтрации
        priority = random.randint(1, 5)
        
        # Создаем запись с тестовыми данными
        metadata = {
            "category": category,
            "tags": tags,
            "source": source,
            "priority": priority,
            "batch_id": str(uuid4()),
            "index": i + 1,
            "creation_date": creation_date
        }
        
        # Решаем, создавать запись из текста или из вектора
        if random.random() < 0.7:  # 70% текстовых записей
            record_id = await client.create_text_record(
                text=text,
                metadata=metadata,
                timestamp=creation_date
            )
        else:  # 30% векторных записей
            # Создаем случайный вектор
            vector = list(np.random.random(384).astype(float))
            record_id = await client.create_record(
                vector=vector,
                metadata=metadata,
                timestamp=creation_date
            )
        
        record_ids.append(record_id)
        
        # Логируем каждую 5-ю запись для наглядности
        if (i + 1) % 5 == 0:
            logger.info(f"Создано {i + 1} записей из {count}")
    
    logger.info(f"Создано всего {len(record_ids)} записей")
    return record_ids

async def perform_complex_filtering(client):
    """Выполняет примеры сложной фильтрации записей."""
    # 1. Найти все записи с высоким приоритетом (4-5) из категории документов
    high_priority_docs = await client.filter_records(
        metadata_filter={
            "category": "documents",
            "priority": {"$gte": 4}
        },
        limit=10
    )
    logger.info(f"Документы с высоким приоритетом: {len(high_priority_docs)}")
    
    # 2. Найти все записи с тегом "important" из любой категории, кроме "notes"
    important_non_notes = await client.filter_records(
        metadata_filter={
            "tags": {"$in": ["important"]},
            "category": {"$ne": "notes"}
        },
        limit=20
    )
    logger.info(f"Важные записи (не заметки): {len(important_non_notes)}")
    
    # 3. Найти записи, созданные за последнюю неделю
    one_week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    recent_records = await client.filter_records(
        metadata_filter={
            "creation_date": {"$gte": one_week_ago}
        },
        limit=50
    )
    logger.info(f"Записи за последнюю неделю: {len(recent_records)}")
    
    # 4. Сложный запрос: бизнес-записи с приоритетом 3+ из веб-источников или API
    complex_filter = await client.filter_records(
        metadata_filter={
            "tags": {"$in": ["business"]},
            "priority": {"$gte": 3},
            "source": {"$in": ["web", "api"]}
        },
        limit=15
    )
    logger.info(f"Результаты сложного фильтра: {len(complex_filter)}")
    
    return {
        "high_priority_docs": high_priority_docs,
        "important_non_notes": important_non_notes,
        "recent_records": recent_records,
        "complex_filter": complex_filter
    }

async def batch_delete_examples(client, filter_results):
    """Выполняет примеры массового удаления записей."""
    # 1. Удаление по списку ID (до 3 записей)
    if filter_results["high_priority_docs"]:
        record_ids = [str(r.id) for r in filter_results["high_priority_docs"][:3]]
        if record_ids:
            result = await client.delete(
                record_ids=record_ids,
                confirm=True
            )
            logger.info(f"Удаление по списку ID: {'успешно' if result else 'не удалось'}")
    
    # 2. Удаление по фильтру - все записи с приоритетом 1 (низкий)
    result = await client.delete(
        filter={"priority": 1},
        max_records=10,
        confirm=True
    )
    logger.info(f"Удаление записей с низким приоритетом: {'успешно' if result else 'не удалось'}")
    
    # 3. Удаление по сложному фильтру - черновики из категории заметок
    result = await client.delete(
        filter={
            "category": "notes",
            "tags": {"$in": ["draft"]}
        },
        max_records=5,
        confirm=True
    )
    logger.info(f"Удаление черновиков заметок: {'успешно' if result else 'не удалось'}")

async def main():
    """Основная функция примера."""
    # Создание клиента
    client = await create_client(base_url="http://localhost:8007")
    
    try:
        # Генерация тестовых данных
        logger.info("Генерация тестовых записей...")
        record_ids = await generate_records(client, count=20)
        
        # Примеры фильтрации
        logger.info("\nВыполнение сложных запросов фильтрации...")
        filter_results = await perform_complex_filtering(client)
        
        # Примеры удаления
        logger.info("\nВыполнение пакетного удаления...")
        await batch_delete_examples(client, filter_results)
        
        # Итоговая статистика
        remaining = await client.filter_records(
            metadata_filter={},
            limit=100,
            include_metadata=False
        )
        logger.info(f"\nИтого осталось записей: {len(remaining)}")
        
    except Exception as e:
        logger.error(f"Ошибка при выполнении примера: {e}")
    finally:
        logger.info("Пример завершен")

if __name__ == "__main__":
    asyncio.run(main()) 