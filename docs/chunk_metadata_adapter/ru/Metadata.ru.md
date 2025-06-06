# Структура метаданных

- [Основные модели](#основные-модели)
- [Поля идентификации и агрегации](#поля-идентификации-и-агрегации)
- [Поля ChunkMetrics](#поля-chunkmetrics)
- [Валидация данных](#валидация-данных)
- [Конвертация](#конвертация)

# Основные модели

Пакет `chunk_metadata_adapter` предоставляет две основные модели данных для метаданных чанков:

1. `SemanticChunk` - Полностью структурированная модель с вложенными объектами
2. `FlatSemanticChunk` - Плоская структура для систем хранения

## SemanticChunk

Модель `SemanticChunk` представляет собой богатое, структурированное представление метаданных чанка, предназначенное для программной обработки и манипуляций. Она содержит вложенные объекты и типизированные поля.

### Обязательные поля

| Поле | Тип | Описание |
|------|-----|----------|
| `uuid` | `str` | UUIDv4 идентификатор чанка |
| `type` | `ChunkType` | Тип содержимого (DocBlock, CodeBlock и т.д.) |
| `text` | `str` | Фактическое содержимое чанка |
| `language` | `str` | Язык содержимого (код или естественный язык) |
| `sha256` | `str` | SHA256 хеш текстового содержимого |
| `start` | `int` | Смещение начала чанка в исходном тексте (в байтах или символах) |
| `end` | `int` | Смещение конца чанка в исходном тексте (в байтах или символах) |

### Опциональные поля

| Поле | Тип | Описание |
|------|-----|----------|
| `source_id` | `str` | UUIDv4 идентификатор исходного документа |
| `project` | `str` | Идентификатор проекта |
| `task_id` | `str` | Идентификатор задачи |
| `subtask_id` | `str` | Идентификатор подзадачи |
| `unit_id` | `str` | Идентификатор блока обработки |
| `role` | `ChunkRole` | Роль создателя контента |
| `summary` | `str` | Краткое резюме содержимого |
| `source_path` | `str` | Путь к исходному файлу |
| `source_lines` | `List[int]` | Номера строк в исходном файле |
| `ordinal` | `int` | Порядок чанка в источнике |
| `created_at` | `str` | Временная метка ISO8601 с часовым поясом |
| `status` | `ChunkStatus` | Статус обработки |
| `chunking_version` | `str` | Версия алгоритма разбиения на чанки |
| `embedding` | `List[float]` | Векторное представление содержимого |
| `links` | `List[str]` | Связи с другими чанками в формате "relation:uuid" |
| `tags` | `List[str]` | Теги содержимого |
| `metrics` | `ChunkMetrics` | Метрики качества и использования |
| `start` | `int` | Смещение начала чанка в исходном тексте (в байтах или символах) |
| `end` | `int` | Смещение конца чанка в исходном тексте (в байтах или символах) |

## FlatSemanticChunk

Модель `FlatSemanticChunk` представляет собой упрощенное, плоское представление, разработанное для систем хранения, предпочитающих простые форматы ключ-значение.

### Ключевые отличия от SemanticChunk

1. Все поля имеют примитивные типы (без вложенных объектов)
2. Списки представлены в виде строк, разделенных запятыми
3. Значения перечислений хранятся как строки
4. Связанные данные выравниваются:
   - `source_lines` становится `source_lines_start` и `source_lines_end`
   - `links` становится `link_parent` и `link_related`
   - поля `metrics` выравниваются до корневого уровня

### Конвертация

Пакет предоставляет методы для конвертации между этими форматами:

```python
# SemanticChunk в FlatSemanticChunk
flat_chunk = FlatSemanticChunk.from_semantic_chunk(semantic_chunk)
flat_dict = builder.semantic_to_flat(semantic_chunk)

# FlatSemanticChunk в SemanticChunk
semantic_chunk = flat_chunk.to_semantic_chunk()
semantic_chunk = builder.flat_to_semantic(flat_dict)
```

### Поля ChunkMetrics

| Поле           | Тип    | Описание                            |
|----------------|--------|-------------------------------------|
| quality_score  | float  | Оценка качества [0, 1]              |
| coverage       | float  | Покрытие [0, 1]                     |
| cohesion       | float  | Сцепленность [0, 1]                 |
| boundary_prev  | float  | Сходство с предыдущим чанком        |
| boundary_next  | float  | Сходство со следующим чанком        |
| matches        | int    | Количество совпадений при поиске     |
| used_in_generation | bool | Использовался при генерации        |
| used_as_input  | bool   | Использовался как вход              |
| used_as_context| bool   | Использовался как контекст          |
| feedback       | FeedbackMetrics | Метрики обратной связи        |

### Метрики FlatSemanticChunk

| Поле           | Тип    | Описание                            |
|----------------|--------|-------------------------------------|
| coverage       | float  | Покрытие [0, 1]                     |
| cohesion       | float  | Сцепленность [0, 1]                 |
| boundary_prev  | float  | Сходство с предыдущим чанком        |
| boundary_next  | float  | Сходство со следующим чанком        |
| `start` | `int` | Смещение начала чанка в исходном тексте (в байтах или символах) |
| `end` | `int` | Смещение конца чанка в исходном тексте (в байтах или символах) |

## Поля идентификации и агрегации

Следующие поля используются для идентификации, агрегации и установления связей между чанками и их исходными блоками (абзацами, сообщениями, секциями и т.д.). Эти поля позволяют проводить аналитику, агрегацию и восстановление структуры исходного документа.

| Поле        | Тип     | Обяз. | Назначение/Описание | Пример значения | Когда использовать |
|-------------|---------|-------|---------------------|-----------------|-------------------|
| block_id    | str(UUID4) | да  | Уникальный идентификатор исходного блока (абзаца, сообщения и т.д.), к которому относится чанк. Позволяет агрегировать чанки, относящиеся к одному блоку. | "b7e2...c4" | При разметке и агрегации чанков по исходным блокам |
| block_type  | str     | нет   | Тип исходного блока (например, "paragraph", "message", "section"). Помогает при анализе и агрегации. | "paragraph" | Для аналитики, агрегации, восстановления структуры |
| block_index | int     | нет   | Порядковый номер блока в исходном документе/диалоге. | 3 | Для восстановления порядка блоков |
| block_meta  | dict    | нет   | Дополнительные метаданные блока (автор, временные метки и т.д.). | {"author": "user1"} | Для расширенной аналитики |

См. также: [Поля ChunkMetrics](#поля-chunkmetrics), [Сценарии использования](./Usage.ru.md#сценарии-агрегации)

## Валидация данных

Обе модели реализуют строгие правила валидации:

- UUID должны иметь валидный формат UUIDv4
- Временные метки должны быть в формате ISO8601 с часовым поясом
- Связи должны следовать формату "relation:uuid" с валидными UUID
- Числовые метрики (включая coverage, cohesion, boundary_prev, boundary_next) должны быть в диапазоне [0, 1]
- Обязательные поля не могут быть null

Все новые метрики опциональны и полностью совместимы с предыдущими версиями.

Это обеспечивает целостность и согласованность данных во всей системе.

## Best Practices / Рекомендации

### Идентификация и агрегация
- Всегда задавайте `block_id` для каждого чанка, который относится к логическому блоку (абзац, сообщение, секция и т.д.), чтобы обеспечить агрегацию и трассируемость.
- Используйте `block_type` и `block_index` для аналитики и восстановления исходного порядка блоков в документе.
- Для расширенного анализа храните дополнительный контекст в `block_meta` (например, автор, временные метки).
- Поля, связанные с блоками (`block_id` и др.), должны заполняться интеграционным слоем, а не базовым сервисом чанкинга.

### Связи между чанками
- Используйте поле `links` для выражения связей между чанками (например, parent-child, related, reference). Формат: `relation:uuid4`.
- Строго валидируйте все UUID и формат связей ([см. Валидация данных](#валидация-данных)).

### Согласованность данных
- Убедитесь, что все UUID имеют формат UUIDv4, а временные метки — ISO8601 с таймзоной.
- Используйте `ordinal` для сохранения порядка чанков внутри блока или документа.
- Всегда вычисляйте и сохраняйте `sha256` для дедупликации и проверки целостности.

### Типовые ошибки
- Не назначайте `block_id` на уровне базового сервиса чанкинга, если он не знает структуру блоков — это зона ответственности интеграционного слоя.
- Не используйте неуникальные или повторяющиеся идентификаторы блоков — всегда применяйте UUIDv4.
- Не пропускайте обязательные поля (`uuid`, `type`, `text`, `language`, `sha256`, `start`, `end`).

### Пример: Агрегация чанков по block_id
```python
from collections import defaultdict
# Пусть есть список объектов SemanticChunk: chunks
blocks = defaultdict(list)
for chunk in chunks:
    if chunk.block_id:
        blocks[chunk.block_id].append(chunk)
# Теперь blocks[block_id] содержит все чанки для блока
```

### Пример: Восстановление структуры документа
```python
# Для восстановления порядка блоков и их чанков:
ordered_blocks = sorted(blocks.items(), key=lambda x: x[1][0].block_index or 0)
for block_id, block_chunks in ordered_blocks:
    block_chunks.sort(key=lambda c: c.ordinal or 0)
    # Восстановить текст блока
    block_text = " ".join(chunk.text for chunk in block_chunks)
```

См. также: [Поля идентификации и агрегации](#поля-идентификации-и-агрегации), [Сценарии использования](./Usage.ru.md#сценарии-агрегации), [Валидация данных](#валидация-данных) 