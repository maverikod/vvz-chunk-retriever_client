# Жизненный цикл данных

## Обзор

Данная библиотека имплементирует детальную модель жизненного цикла данных, которая позволяет отслеживать состояние данных на всех этапах их обработки - от момента начального сбора до финальной валидации и использования. Это критически важный компонент для систем, где требуется высокая надежность и прозрачность данных.

## Этапы жизненного цикла

Жизненный цикл данных включает следующие основные этапы:

| Статус | Значение | Описание |
|--------|---------|----------|
| `RAW` | "raw" | Исходные, необработанные данные, поступившие в систему |
| `CLEANED` | "cleaned" | Данные после первичной очистки от шума, опечаток и простых ошибок |
| `VERIFIED` | "verified" | Данные, проверенные на соответствие определенным правилам и стандартам |
| `VALIDATED` | "validated" | Данные, прошедшие проверку в контексте других данных и внешних источников |
| `RELIABLE` | "reliable" | Надежные, проверенные данные, готовые к использованию в критически важных системах |

## Детальное описание этапов

### 1. RAW (Сырые данные)

**Определение**: Данные в их первоначальном, необработанном виде, как они поступили в систему.

**Характеристики**:
- Могут содержать ошибки, опечатки, шум
- Структура может быть непоследовательной
- Могут содержать дубликаты или противоречивую информацию
- Не подходят для прямого использования в критичных процессах

**Пример кода**:
```python
raw_chunk = builder.build_semantic_chunk(
    text="Данные пользователя: Иван Иванов, ivan@eample.com, 123-45-6789",
    language="text",
    type=ChunkType.DOC_BLOCK,
    source_id=source_id,
    status=ChunkStatus.RAW
)
```

### 2. CLEANED (Очищенные данные)

**Определение**: Данные, прошедшие первичную обработку и очистку.

**Характеристики**:
- Исправлены очевидные опечатки и форматирование
- Удалены или помечены явно некорректные значения
- Стандартизован формат данных
- Структура приведена к единому виду
- По-прежнему требуют дополнительной проверки

**Процессы очистки**:
- Исправление опечаток и орфографических ошибок
- Нормализация регистра и форматирования
- Удаление дубликатов
- Стандартизация дат, чисел, адресов, телефонов и т.д.
- Приведение к единой кодировке и формату

**Пример кода**:
```python
cleaned_chunk = SemanticChunk(**raw_chunk.model_dump())
cleaned_chunk.text = "Данные пользователя: Иван Иванов, ivan@example.com, 123-456-7890"
cleaned_chunk.status = ChunkStatus.CLEANED
```

### 3. VERIFIED (Проверенные данные)

**Определение**: Данные, которые прошли проверку на соответствие определенным правилам, ограничениям и стандартам.

**Характеристики**:
- Подтверждено соответствие данных бизнес-правилам
- Проверена целостность и непротиворечивость
- Проверены ограничения (длина, диапазон значений и т.д.)
- Подтверждено соответствие форматам и стандартам

**Процессы верификации**:
- Проверка форматов email, телефонов, документов
- Валидация по регулярным выражениям
- Проверка ограничений (мин/макс длина, диапазон значений)
- Проверка на соответствие справочникам и классификаторам
- Проверка на уникальность ключевых полей

**Пример кода**:
```python
verified_chunk = SemanticChunk(**cleaned_chunk.model_dump())
verified_chunk.status = ChunkStatus.VERIFIED
# Добавляем метки проверок
verified_chunk.tags.append("verified_email")
verified_chunk.tags.append("verified_phone")
```

### 4. VALIDATED (Валидированные данные)

**Определение**: Данные, прошедшие комплексную валидацию с учетом контекста и перекрестных проверок.

**Характеристики**:
- Подтверждена согласованность с другими наборами данных
- Проверены в контексте внешних источников данных
- Проверены временные и логические зависимости
- Данные могут быть использованы для принятия решений

**Процессы валидации**:
- Перекрестная проверка с другими системами (CRM, ERP и т.д.)
- Сверка с официальными источниками (реестры, базы данных)
- Временная валидация (проверка истории изменений)
- Комплексная проверка бизнес-процессов

**Пример кода**:
```python
validated_chunk = SemanticChunk(**verified_chunk.model_dump())
validated_chunk.status = ChunkStatus.VALIDATED
# Добавляем ссылку на источник валидации
validated_chunk.links.append(f"reference:{reference_id}")
validated_chunk.tags.append("crm_validated")
```

### 5. RELIABLE (Надежные данные)

**Определение**: Полностью проверенные, надежные данные, готовые к использованию в критических системах.

**Характеристики**:
- Прошли все этапы проверки и валидации
- Имеют высокий уровень достоверности
- Могут использоваться для критически важных процессов
- Обычно сопровождаются метаданными о проверках
- Могут быть опубликованы или переданы в другие системы

**Дополнительные метрики**:
- Высокие показатели качества (quality_score, coverage, cohesion, boundary_prev, boundary_next)
- Полная история обработки
- Ссылки на все источники верификации и валидации

**Пример кода**:
```python
reliable_chunk = SemanticChunk(**validated_chunk.model_dump())
reliable_chunk.status = ChunkStatus.RELIABLE
# Заполнение всех метрик качества
reliable_chunk.metrics.quality_score = 0.98
reliable_chunk.metrics.coverage = 0.95
reliable_chunk.metrics.cohesion = 0.9
reliable_chunk.metrics.boundary_prev = 0.85
reliable_chunk.metrics.boundary_next = 0.92
```

## Дополнительные статусы жизненного цикла

В дополнение к основным этапам, система поддерживает следующие операционные статусы:

| Статус | Значение | Описание |
|--------|---------|----------|
| `NEW` | "new" | Новые данные, еще не обработанные |
| `INDEXED` | "indexed" | Данные, добавленные в индекс поиска |
| `OBSOLETE` | "obsolete" | Устаревшие данные, требующие обновления |
| `REJECTED` | "rejected" | Данные, отклоненные из-за критических проблем |
| `IN_PROGRESS` | "in_progress" | Данные в процессе обработки |
| `NEEDS_REVIEW` | "needs_review" | Данные, требующие ручной проверки |
| `ARCHIVED` | "archived" | Архивированные данные |

## Фильтрация данных по уровню надежности

Библиотека предоставляет механизмы для фильтрации данных по уровню надежности:

```python
def filter_chunks_by_status(chunks, min_status):
    """
    Фильтрует чанки по минимальному требуемому статусу в жизненном цикле данных.
    
    Порядок статусов: 
    RAW < CLEANED < VERIFIED < VALIDATED < RELIABLE
    
    Args:
        chunks: список чанков для фильтрации
        min_status: минимальный требуемый статус (ChunkStatus)
        
    Returns:
        отфильтрованный список чанков
    """
    status_order = {
        ChunkStatus.RAW.value: 1,
        ChunkStatus.CLEANED.value: 2,
        ChunkStatus.VERIFIED.value: 3,
        ChunkStatus.VALIDATED.value: 4, 
        ChunkStatus.RELIABLE.value: 5
    }
    
    min_level = status_order.get(min_status.value, 0)
    
    return [
        chunk for chunk in chunks 
        if status_order.get(chunk.status.value, 0) >= min_level
    ]
```

Пример использования:
```python
# Получить только надежные данные
reliable_only = filter_chunks_by_status(all_chunks, ChunkStatus.RELIABLE)

# Получить проверенные и валидированные данные
verified_and_above = filter_chunks_by_status(all_chunks, ChunkStatus.VERIFIED)
```

## Переходы между состояниями

Данные могут переходить между состояниями как последовательно (от RAW к RELIABLE), так и в произвольном порядке в зависимости от бизнес-логики. Например:

1. Если данные не проходят верификацию, они могут быть отправлены обратно в статус CLEANED для дополнительной обработки
2. Данные могут быть помечены как NEEDS_REVIEW на любом этапе, если требуется ручная проверка
3. Данные могут быть помечены как REJECTED, если обнаружены критические проблемы
4. При обновлении данных они могут вернуться на этап RAW и пройти весь цикл заново

## Преимущества подхода

Структурированный подход к жизненному циклу данных обеспечивает ряд преимуществ:

1. **Прозрачность** - ясное понимание состояния данных на каждом этапе
2. **Качество данных** - возможность контролировать и улучшать качество данных
3. **Аудит и отслеживание** - полная история обработки данных
4. **Управление рисками** - использование данных соответствующего уровня надежности для разных задач
5. **Соответствие требованиям** - возможность доказать соответствие нормативным требованиям (GDPR, и др.)
6. **Оптимизация процессов** - анализ и улучшение процессов обработки данных

## Полный пример жизненного цикла

```python
from chunk_metadata_adapter import ChunkMetadataBuilder, ChunkType, ChunkStatus
import uuid

# Создаем builder и ID источника
builder = ChunkMetadataBuilder(project="DataQualityProject")
source_id = str(uuid.uuid4())

# 1. RAW - Первичный ввод данных
raw_chunk = builder.build_semantic_chunk(
    text="Пользователь: Петр Сидоров, pеtr@eample.cоm, Москва, 89997771234",
    language="text",
    type=ChunkType.DOC_BLOCK,
    source_id=source_id,
    status=ChunkStatus.RAW,
    tags=["user_data", "personal"]
)
print(f"RAW: {raw_chunk.uuid}, статус: {raw_chunk.status.value}")

# 2. CLEANED - Очистка данных
cleaned_chunk = SemanticChunk(**raw_chunk.model_dump())
# Исправляем опечатки в email и форматируем телефон
cleaned_chunk.text = "Пользователь: Петр Сидоров, petr@example.com, Москва, +7 (999) 777-12-34"
cleaned_chunk.status = ChunkStatus.CLEANED
cleaned_chunk.tags.append("cleaned_email")
cleaned_chunk.tags.append("formatted_phone")
print(f"CLEANED: {cleaned_chunk.uuid}, статус: {cleaned_chunk.status.value}")

# 3. VERIFIED - Проверка данных
verified_chunk = SemanticChunk(**cleaned_chunk.model_dump())
verified_chunk.status = ChunkStatus.VERIFIED
verified_chunk.tags.append("verified_email")
verified_chunk.tags.append("verified_phone")
# Добавляем метаданные о проверках
verified_chunk.metrics.quality_score = 0.75  # Предварительная оценка качества
print(f"VERIFIED: {verified_chunk.uuid}, статус: {verified_chunk.status.value}")

# 4. VALIDATED - Валидация с учетом контекста
validated_chunk = SemanticChunk(**verified_chunk.model_dump())
validated_chunk.status = ChunkStatus.VALIDATED
# Добавляем связь с записью в CRM
reference_id = str(uuid.uuid4())
validated_chunk.links.append(f"reference:{reference_id}")
validated_chunk.tags.append("crm_validated")
validated_chunk.metrics.quality_score = 0.85  # Повышаем оценку качества
print(f"VALIDATED: {validated_chunk.uuid}, статус: {validated_chunk.status.value}")

# 5. RELIABLE - Надежные данные
reliable_chunk = SemanticChunk(**validated_chunk.model_dump())
reliable_chunk.status = ChunkStatus.RELIABLE
# Заполнение всех метрик качества
reliable_chunk.metrics.quality_score = 0.98
reliable_chunk.metrics.coverage = 0.95
reliable_chunk.metrics.cohesion = 0.9
reliable_chunk.metrics.boundary_prev = 0.85
reliable_chunk.metrics.boundary_next = 0.92
print(f"RELIABLE: {reliable_chunk.uuid}, статус: {reliable_chunk.status.value}")

# Использование данных разного уровня качества для разных задач
chunks = [raw_chunk, cleaned_chunk, verified_chunk, validated_chunk, reliable_chunk]

# Для аналитики используем только проверенные данные
analytics_data = filter_chunks_by_status(chunks, ChunkStatus.VERIFIED)
print(f"Чанков для аналитики: {len(analytics_data)}")

# Для критически важных операций используем только надежные данные
critical_data = filter_chunks_by_status(chunks, ChunkStatus.RELIABLE)
print(f"Чанков для критичных операций: {len(critical_data)}")
```

## Заключение

Имплементированный подход к жизненному циклу данных обеспечивает прозрачный и устойчивый механизм управления качеством данных. Он позволяет гибко управлять процессами обработки и использовать данные соответствующего уровня надежности для разных задач, что критически важно для систем, где требуется высокое качество данных. 

Библиотека поддерживает расширенные метрики качества чанков: quality_score, coverage, cohesion, boundary_prev, boundary_next (все float, диапазон [0, 1], опциональны). 