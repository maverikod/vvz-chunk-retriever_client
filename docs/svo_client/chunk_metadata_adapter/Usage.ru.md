# Руководство по использованию

Это руководство демонстрирует, как использовать пакет `chunk_metadata_adapter` для различных сценариев.

## Установка

```bash
pip install chunk-metadata-adapter
```

## Базовое использование

### Создание плоских метаданных

Наиболее распространенный случай использования - создание плоских метаданных для чанка:

```python
import uuid
from chunk_metadata_adapter import ChunkMetadataBuilder, ChunkType, ChunkRole

# Создаем построитель метаданных для проекта
builder = ChunkMetadataBuilder(project="MyProject", unit_id="chunker-service")

# Генерируем UUID для исходного документа
source_id = str(uuid.uuid4())

# Создаем метаданные для фрагмента кода
metadata = builder.build_flat_metadata(
    text="def hello_world():\n    print('Hello, World!')",
    source_id=source_id,
    ordinal=1,
    type=ChunkType.CODE_BLOCK,
    language="python",
    source_path="src/hello.py",
    source_lines_start=10,
    source_lines_end=12,
    tags="example,hello",
    role=ChunkRole.DEVELOPER,
    coverage=0.95,  # Опционально, float в [0, 1]
    cohesion=0.8,   # Опционально, float в [0, 1]
    boundary_prev=0.7, # float в [0, 1]
    boundary_next=0.9  # float в [0, 1]
)

print(f"UUID чанка: {metadata['uuid']}")
print(f"SHA256: {metadata['sha256']}")
```

### Создание структурированного чанка

Когда вам нужен полностью структурированный объект:

```python
from chunk_metadata_adapter import ChunkMetadataBuilder, ChunkType, ChunkRole

# Создаем построитель для документационного проекта
builder = ChunkMetadataBuilder(
    project="DocumentationProject",
    unit_id="docs-generator"
)

# Создаем структурированный чанк
chunk = builder.build_semantic_chunk(
    text="# Введение\n\nЭто документация по системе.",
    language="markdown",
    type=ChunkType.DOC_BLOCK,
    source_id=str(uuid.uuid4()),
    summary="Раздел введения проекта",
    role=ChunkRole.DEVELOPER,
    source_path="docs/intro.md",
    source_lines=[1, 3],
    ordinal=0,
    task_id="DOC-123",
    subtask_id="DOC-123-A",
    tags=["introduction", "documentation", "overview"],
    links=[f"parent:{str(uuid.uuid4())}"],
    coverage=0.95,
    cohesion=0.8,
    boundary_prev=0.7,
    boundary_next=0.9
)

print(f"UUID чанка: {chunk.uuid}")
print(f"Краткое описание: {chunk.summary}")
```

### Преобразование между форматами

Пакет позволяет без проблем конвертировать между форматами:

```python
# Преобразование из структурированного в плоский формат
flat_dict = builder.semantic_to_flat(chunk)

# Преобразование из плоского в структурированный формат
restored_chunk = builder.flat_to_semantic(flat_dict)

# Проверка, что они эквивалентны
assert restored_chunk.uuid == chunk.uuid
assert restored_chunk.text == chunk.text
assert restored_chunk.type == chunk.type
```

## Продвинутое использование

### Обработка цепочки чанков

При работе с последовательностью чанков из документа:

```python
# Создаем построитель для проекта
builder = ChunkMetadataBuilder(project="ChainExample", unit_id="processor")
source_id = str(uuid.uuid4())

# Создаем последовательность чанков из документа
chunks = []
for i, text in enumerate([
    "# Заголовок документа",
    "## Раздел 1\n\nСодержимое раздела 1.",
    "## Раздел 2\n\nСодержимое раздела 2.",
    "## Заключение\n\nИтоговые мысли по теме."
]):
    chunk = builder.build_semantic_chunk(
        text=text,
        language="markdown",
        type=ChunkType.DOC_BLOCK,
        source_id=source_id,
        ordinal=i,
        summary=f"Раздел {i}" if i > 0 else "Заголовок"
    )
    chunks.append(chunk)

# Создаем явные связи между чанками (отношения родитель-потомок)
for i in range(1, len(chunks)):
    # Добавляем ссылку на заголовок как родителя
    chunks[i].links.append(f"parent:{chunks[0].uuid}")
    
# Обрабатываем метрики чанков
for chunk in chunks:
    chunk.metrics.quality_score = 0.95
    chunk.metrics.used_in_generation = True
    chunk.metrics.feedback.accepted = 2
```

### Использование валидации UUID

Пакет выполняет строгую валидацию UUID:

```python
try:
    metadata = builder.build_flat_metadata(
        text="Тестовое содержимое",
        source_id="invalid-uuid",  # Неверный формат UUID
        ordinal=1,
        type=ChunkType.DOC_BLOCK,
        language="text"
    )
except ValueError as e:
    print(f"Ошибка валидации: {e}")
```

### Работа с временными метками

Все временные метки проверяются и хранятся в формате ISO8601 с часовым поясом:

```python
from datetime import datetime, timezone

# Валидная временная метка с часовым поясом
valid_timestamp = datetime.now(timezone.utc).isoformat()

# Библиотека автоматически будет использовать валидный формат временной метки
chunk = builder.build_semantic_chunk(
    text="Временно-чувствительный контент",
    language="text",
    type=ChunkType.MESSAGE,
    created_at=valid_timestamp  # Опционально, автоматически сгенерируется если не указано
)
```

#### Round-trip с расширенными метриками

```python
chunk = builder.build_semantic_chunk(
    text="metrics roundtrip",
    language="text",
    type=ChunkType.DOC_BLOCK,
    source_id=str(uuid.uuid4()),
    coverage=0.7,
    cohesion=0.6,
    boundary_prev=0.5,
    boundary_next=0.4
)
flat = builder.semantic_to_flat(chunk)
restored = builder.flat_to_semantic(flat)
assert restored.metrics.coverage == 0.7
assert restored.metrics.cohesion == 0.6
assert restored.metrics.boundary_prev == 0.5
assert restored.metrics.boundary_next == 0.4
```

## Соображения производительности

- Метод `build_flat_metadata` работает быстрее, чем `build_semantic_chunk`, поскольку не создает экземпляры моделей Pydantic
- Для массовой обработки рассмотрите возможность использования плоских метаданных и преобразования в структурированный формат только при необходимости
- Вычисление SHA256 относительно дорого для больших текстов; рассмотрите возможность кэширования результатов, если обрабатываете один и тот же контент несколько раз 

## Best Practice: Рекомендованные сценарии использования

### 1. Создание чанка с расширенными метриками качества

```python
from chunk_metadata_adapter import ChunkMetadataBuilder, ChunkType, ChunkStatus
import uuid

builder = ChunkMetadataBuilder(project="MetricsDemo", unit_id="metrics-unit")
source_id = str(uuid.uuid4())
chunk = builder.build_semantic_chunk(
    text="Sample text for metrics.",
    language="text",
    type=ChunkType.DOC_BLOCK,
    source_id=source_id,
    status=ChunkStatus.RELIABLE,
    coverage=0.95,
    cohesion=0.8,
    boundary_prev=0.7,
    boundary_next=0.9
)
print(chunk.metrics)
```

### 2. Конвертация между flat и structured форматами

```python
from chunk_metadata_adapter import ChunkMetadataBuilder, ChunkType, ChunkRole
import uuid

builder = ChunkMetadataBuilder(project="ConversionExample")
structured_chunk = builder.build_semantic_chunk(
    text="This is a sample chunk for conversion demonstration.",
    language="text",
    type=ChunkType.COMMENT,
    source_id=str(uuid.uuid4()),
    role=ChunkRole.REVIEWER
)
flat_dict = builder.semantic_to_flat(structured_chunk)
restored_chunk = builder.flat_to_semantic(flat_dict)
assert restored_chunk.uuid == structured_chunk.uuid
```

### 3. Цепочка обработки документа с обновлением статусов и метрик

```python
from chunk_metadata_adapter import ChunkMetadataBuilder, ChunkType, ChunkStatus
import uuid

builder = ChunkMetadataBuilder(project="ChainExample", unit_id="processor")
source_id = str(uuid.uuid4())
chunks = []
for i, text in enumerate([
    "# Document Title",
    "## Section 1\n\nThis is the content of section 1.",
    "## Section 2\n\nThis is the content of section 2.",
    "## Conclusion\n\nFinal thoughts on the topic."
]):
    chunk = builder.build_semantic_chunk(
        text=text,
        language="markdown",
        type=ChunkType.DOC_BLOCK,
        source_id=source_id,
        ordinal=i,
        summary=f"Section {i}" if i > 0 else "Title"
    )
    chunks.append(chunk)
# Устанавливаем связи и статусы
for i in range(1, len(chunks)):
    chunks[i].links.append(f"parent:{chunks[0].uuid}")
    chunks[i].status = ChunkStatus.INDEXED
# Обновляем метрики
for chunk in chunks:
    chunk.metrics.quality_score = 0.95
    chunk.metrics.used_in_generation = True
    chunk.metrics.matches = 3
    chunk.metrics.feedback.accepted = 2
```

### 4. Round-trip: flat -> structured -> flat

```python
from chunk_metadata_adapter import ChunkMetadataBuilder, ChunkType
import uuid

builder = ChunkMetadataBuilder(project="RoundTripDemo")
source_id = str(uuid.uuid4())
flat = builder.build_flat_metadata(
    text="Round-trip test chunk.",
    source_id=source_id,
    ordinal=1,
    type=ChunkType.DOC_BLOCK,
    language="text"
)
structured = builder.flat_to_semantic(flat)
flat2 = builder.semantic_to_flat(structured)
assert flat2["uuid"] == flat["uuid"]
``` 