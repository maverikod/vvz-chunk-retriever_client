# Vector Store Client

Клиент для взаимодействия с сервисом Vector Store, предоставляющий удобный интерфейс для работы с векторными эмбеддингами.

## Особенности

- Полнофункциональное API для работы с Vector Store
- Асинхронный интерфейс на основе `httpx`
- Автоматическая обработка и валидация параметров
- Комплексное управление ошибками
- Поддержка всех основных операций:
  - Создание записей из текста или векторов
  - Поиск по векторному сходству
  - Фильтрация по метаданным
  - Управление записями
  - Мониторинг и конфигурирование сервиса

## Установка

```bash
pip install vector-store-client
```

Или установка из исходного кода:

```bash
git clone https://github.com/username/vector-store-client.git
cd vector-store-client
pip install -e .
```

## Быстрый старт

```python
import asyncio
from vector_store_client import create_client

async def main():
    # Создание клиента с подключением к сервису
    client = await create_client(base_url="http://localhost:8007")
    
    # Проверка работоспособности сервиса
    health = await client.health()
    print(f"Сервис активен: {health['status'] == 'ok'}")
    
    # Создание записи из текста
    record_id = await client.create_text_record(
        text="Пример текста для векторизации",
        metadata={"type": "example", "tags": ["test", "vector"]}
    )
    print(f"Создана запись с ID: {record_id}")
    
    # Поиск похожих записей
    results = await client.search_text_records(
        text="векторизация примера",
        limit=5
    )
    
    print(f"Найдено {len(results)} похожих записей:")
    for i, result in enumerate(results, 1):
        print(f"{i}. ID: {result.id}, Сходство: {result.score:.4f}")
    
    # Закрытие сессии
    await client._client.aclose()

# Запуск асинхронной функции
if __name__ == "__main__":
    asyncio.run(main())
```

## Основные возможности

### Создание клиента

```python
from vector_store_client import create_client

# Простое создание
client = await create_client(base_url="http://localhost:8007")

# С расширенными параметрами
client = await create_client(
    base_url="http://localhost:8007",
    timeout=30.0,  # Таймаут запросов в секундах
    headers={"Authorization": "Bearer YOUR_TOKEN"},  # Доп. заголовки
    max_retries=3  # Количество повторов для неудачных запросов
)
```

### Управление записями

#### Создание записи из текста

```python
record_id = await client.create_text_record(
    text="Текст для векторизации",
    metadata={  # Опциональные метаданные
        "type": "document",
        "source": "example",
        "tags": ["test", "example"]
    },
    model="text-embedding-3-small",  # Опциональная модель для эмбеддингов
    session_id="session-uuid",  # Опционально
    timestamp="2023-04-25T10:30:00Z"  # Опционально
)
```

#### Создание записи из готового вектора

```python
import numpy as np

# Создание вектора (размерность должна соответствовать вашей модели)
vector = list(np.random.random(384).astype(float))

record_id = await client.create_record(
    vector=vector,
    metadata={
        "type": "vector",
        "source": "custom",
        "body": "Текстовое содержимое или описание для этого вектора"  # Поле 'body' обязательно
    }
)
```

> **Примечание**: API требует наличия поля 'body' в метаданных при создании записи с вектором. Если оно не указано, клиент автоматически добавит значение по умолчанию.

#### Получение данных записи

```python
# Получение метаданных
metadata = await client.get_metadata("record-uuid")

# Получение текста (если доступно)
text = await client.get_text("record-uuid")
```

#### Удаление записей

```python
# Удаление одной записи
await client.delete(record_id="record-uuid")

# Удаление нескольких записей
await client.delete(
    record_ids=["id1", "id2", "id3"],
    confirm=True  # Требуется для удаления нескольких записей
)

# Удаление по фильтру метаданных
await client.delete(
    filter={"type": "test", "source": "example"},
    max_records=100,  # Ограничение для безопасности
    confirm=True  # Требуется для массового удаления
)
```

### Поиск и фильтрация

#### Поиск по тексту

```python
results = await client.search_text_records(
    text="поисковый запрос",
    limit=10,  # Максимальное количество результатов
    model="text-embedding-3-small",  # Опционально
    include_vectors=False,  # Включать векторы в результаты
    include_metadata=True,  # Включать метаданные в результаты
    metadata_filter={"type": "document"}  # Фильтр по метаданным
)

for result in results:
    print(f"ID: {result.id}, Сходство: {result.score}")
    print(f"Метаданные: {result.metadata}")
```

#### Поиск по вектору

```python
results = await client.search_by_vector(
    vector=your_vector,  # Вектор запроса
    limit=10,
    include_vectors=False,
    include_metadata=True
)
```

#### Поиск по вектору с фильтрацией

```python
results = await client.search_records(
    vector=your_vector,
    limit=10,
    include_metadata=True,
    filter_criteria={
        "type": "document",
        "tags": {"$contains": "important"}
    }
)
```

#### Фильтрация по метаданным

```python
results = await client.filter_records(
    metadata_filter={
        "type": "document",
        "source": "database",
        "created_at": {"$gt": "2023-01-01T00:00:00Z"}
    },
    limit=100
)
```

### Сложные фильтры

Клиент поддерживает разнообразные операторы фильтрации:

- `$eq` - равно
- `$ne` - не равно
- `$gt`, `$gte` - больше, больше или равно
- `$lt`, `$lte` - меньше, меньше или равно
- `$in` - находится в списке
- `$nin` - не находится в списке
- `$contains` - содержит элемент (для массивов)
- `$startswith`, `$endswith` - начинается с, заканчивается на (для строк)

Примеры:

```python
# Записи с приоритетом >= 3
filter_criteria = {"priority": {"$gte": 3}}

# Записи с определенными источниками
filter_criteria = {"source": {"$in": ["database", "api", "file"]}}

# Записи с тегом "important" в массиве тегов
filter_criteria = {"tags": {"$contains": "important"}}

# Строковые значения, начинающиеся с "doc"
filter_criteria = {"type": {"$startswith": "doc"}}
```

### Управление сервисом

```python
# Проверка работоспособности
health = await client.health()

# Получение конфигурации
config = await client.config(operation="get")

# Получение значения по пути
storage_config = await client.config(operation="get", path="storage")

# Установка значения (если доступно)
result = await client.config(
    operation="set",
    path="server.max_records_per_request",
    value=1000
)

# Получение справки
help_info = await client.help()
```

## Обработка ошибок

```python
from vector_store_client import (
    ValidationError,
    ResourceNotFoundError,
    JsonRpcException,
    ConnectionError,
    TimeoutError,
    AuthenticationError
)

try:
    await client.get_metadata("non-existent-id")
except ResourceNotFoundError as e:
    print(f"Запись не найдена: {e}")
except ValidationError as e:
    print(f"Ошибка валидации: {e}")
except JsonRpcException as e:
    print(f"Ошибка API: {e.message} (код: {e.code})")
except ConnectionError as e:
    print(f"Ошибка соединения: {e}")
except TimeoutError as e:
    print(f"Таймаут запроса: {e}")
```

## Расширенные примеры

### Пакетное создание записей

```python
import uuid
from datetime import datetime

# Создаем сессию для группировки записей
session_id = str(uuid.uuid4())

# Создаем несколько записей
for i in range(10):
    await client.create_text_record(
        text=f"Документ #{i} для тестирования",
        metadata={
            "index": i,
            "batch": "test-batch",
            "created_at": datetime.now().isoformat()
        },
        session_id=session_id
    )

# Найти все записи из сессии
batch_results = await client.filter_records(
    metadata_filter={"session_id": session_id}
)
```

### Работа с ассистентом и чат-сессиями

```python
# ID сессии и сообщения для связывания записей
session_id = str(uuid.uuid4())
message_id = str(uuid.uuid4())

# Сохранение запроса пользователя
user_record_id = await client.create_text_record(
    text="Объясни как работают векторные эмбеддинги",
    metadata={
        "role": "user",
        "type": "message",
        "conversation": "embeddings"
    },
    session_id=session_id,
    message_id=message_id
)

# Сохранение ответа ассистента
assistant_record_id = await client.create_text_record(
    text="Векторные эмбеддинги - это числовые представления...",
    metadata={
        "role": "assistant",
        "type": "message",
        "conversation": "embeddings"
    },
    session_id=session_id,
    message_id=str(uuid.uuid4())  # Новый ID сообщения
)

# Получение всей истории сессии
conversation = await client.filter_records(
    metadata_filter={"session_id": session_id},
    limit=100
)

# Сортировка сообщений по timestamp
conversation_sorted = sorted(
    conversation, 
    key=lambda x: x.metadata.get("timestamp", "") if x.metadata else ""
)
```

## Часто встречающиеся ошибки

### Проблемы подключения

- **Ошибка**: `ConnectionError: Failed to connect to Vector Store service`
  **Решение**: Проверьте, что сервис Vector Store запущен и доступен по указанному URL. Проверьте сетевые настройки и права доступа.

### Ошибки валидации

- **Ошибка**: `ValidationError: Invalid session_id format`
  **Решение**: Убедитесь, что session_id является допустимым UUID.

- **Ошибка**: `ValidationError: Limit must be between 1 and 100`
  **Решение**: Значение limit должно быть в допустимом диапазоне.

- **Ошибка**: `JsonRpcException: Missing or empty 'body' field`
  **Решение**: При создании записи с помощью `create_record`, включите поле 'body' в метаданные. Это требуется сервером. Если поле не указано, клиент автоматически добавит значение по умолчанию.

### Ошибки API

- **Ошибка**: `JsonRpcException: Invalid params (code: -32602)`
  **Решение**: Проверьте правильность параметров запроса.

- **Ошибка**: `ResourceNotFoundError: Record with ID ... not found`
  **Решение**: Запрашиваемая запись не существует или была удалена.

- **Ошибка**: `AuthenticationError: Not authorized to access configuration`
  **Решение**: Для доступа к конфигурации сервиса требуются специальные права.

## Производительность и оптимизация

### Повторное использование клиента

```python
# Создайте клиент один раз и используйте его повторно для всех запросов
client = await create_client(base_url="http://localhost:8007")

# Используйте контекстный менеджер для автоматического закрытия сессии
async with await create_client(base_url="http://localhost:8007") as client:
    # Используйте клиент здесь
    await client.health()
```

### Пакетная обработка

При работе с большим количеством записей:
- Группируйте записи по session_id для удобства управления
- Используйте фильтрацию метаданных вместо загрузки всех записей
- При массовом удалении используйте фильтры для удаления групп записей

## Лицензия

MIT 