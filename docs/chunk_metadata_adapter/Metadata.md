# Metadata Structure

- [Main Models](#main-models)
- [Identification and Aggregation Fields](#identification-and-aggregation-fields)
- [ChunkMetrics Fields](#chunkmetrics-fields)
- [Data Validation](#data-validation)
- [Conversion](#conversion)

# Main Models

The `chunk_metadata_adapter` package provides two main data models for chunk metadata:

1. `SemanticChunk` - A fully structured model with nested objects
2. `FlatSemanticChunk` - A flat structure for storage systems

## SemanticChunk

The `SemanticChunk` model is a rich, structured representation of chunk metadata designed for programmatic manipulation and processing. It contains nested objects and typed fields.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `uuid` | `str` | UUIDv4 identifier of the chunk |
| `type` | `ChunkType` | Type of content (DocBlock, CodeBlock, etc.) |
| `text` | `str` | Actual content of the chunk |
| `language` | `str` | Content language (code or natural language) |
| `sha256` | `str` | SHA256 hash of the text content |
| `start` | `int` | Start offset of the chunk in the source text (in bytes or characters) |
| `end` | `int` | End offset of the chunk in the source text (in bytes or characters) |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `source_id` | `str` | UUIDv4 identifier of the source document |
| `project` | `str` | Project identifier |
| `task_id` | `str` | Task identifier |
| `subtask_id` | `str` | Subtask identifier |
| `unit_id` | `str` | Processing unit identifier |
| `role` | `ChunkRole` | Role of the content creator |
| `summary` | `str` | Brief summary of the content |
| `source_path` | `str` | Path to the source file |
| `source_lines` | `List[int]` | Line numbers in source file |
| `ordinal` | `int` | Order of the chunk in the source |
| `created_at` | `str` | ISO8601 timestamp with timezone |
| `status` | `ChunkStatus` | Processing status |
| `chunking_version` | `str` | Version of chunking algorithm |
| `embedding` | `List[float]` | Vector embedding of the content |
| `links` | `List[str]` | Links to other chunks in format "relation:uuid" |
| `tags` | `List[str]` | Content tags |
| `metrics` | `ChunkMetrics` | Quality and usage metrics |
| `start` | `int` | Start offset of the chunk in the source text (in bytes or characters) |
| `end` | `int` | End offset of the chunk in the source text (in bytes or characters) |

## FlatSemanticChunk

The `FlatSemanticChunk` model is a simplified, flat representation designed for storage systems that prefer simple key-value formats.

### Key Differences from SemanticChunk

1. All fields are primitive types (no nested objects)
2. Lists are represented as comma-separated strings
3. Enum values are stored as strings
4. Related data is flattened:
   - `source_lines` becomes `source_lines_start` and `source_lines_end`
   - `links` becomes `link_parent` and `link_related`
   - `metrics` fields are flattened to the root level

### Conversion

The package provides methods to convert between these formats:

```python
# SemanticChunk to FlatSemanticChunk
flat_chunk = FlatSemanticChunk.from_semantic_chunk(semantic_chunk)
flat_dict = builder.semantic_to_flat(semantic_chunk)

# FlatSemanticChunk to SemanticChunk
semantic_chunk = flat_chunk.to_semantic_chunk()
semantic_chunk = builder.flat_to_semantic(flat_dict)
```

### ChunkMetrics Fields

| Field           | Type    | Description                        |
|-----------------|---------|------------------------------------|
| quality_score   | float   | Quality score [0, 1]               |
| coverage        | float   | Coverage [0, 1]                    |
| cohesion        | float   | Cohesion [0, 1]                    |
| boundary_prev   | float   | Boundary similarity with previous  |
| boundary_next   | float   | Boundary similarity with next      |
| matches         | int     | Retrieval matches                  |
| used_in_generation | bool | Used in generation                 |
| used_as_input   | bool    | Used as input                      |
| used_as_context | bool    | Used as context                    |
| feedback        | FeedbackMetrics | User feedback metrics         |

### FlatSemanticChunk Metrics Fields

| Field           | Type    | Description                        |
|-----------------|---------|------------------------------------|
| coverage        | float   | Coverage [0, 1]                    |
| cohesion        | float   | Cohesion [0, 1]                    |
| boundary_prev   | float   | Boundary similarity with previous  |
| boundary_next   | float   | Boundary similarity with next      |
| start           | int     | Start offset of the chunk in the source text (in bytes or characters) |
| end             | int     | End offset of the chunk in the source text (in bytes or characters) |

## Data Validation

Both models implement strict validation rules:

- UUIDs must be valid UUIDv4 format
- Timestamps must be ISO8601 with timezone
- Links must follow the format "relation:uuid" with valid UUIDs
- Numeric metrics (including coverage, cohesion, boundary_prev, boundary_next) must be within [0, 1]
- Required fields cannot be null

All new metric fields are optional and backward compatible.

## Identification and Aggregation Fields

The following fields are used to identify, aggregate, and relate chunks to their source blocks (paragraphs, messages, sections, etc.). These fields enable advanced analytics, aggregation, and reconstruction of original document structure.

| Field        | Type     | Required | Description | Example | When to use |
|-------------|----------|----------|-------------|---------|-------------|
| block_id    | str(UUID4) | yes      | Unique identifier of the source block (e.g., paragraph, message, section) to which the chunk belongs. Enables aggregation of all chunks from the same block. | "b7e2...c4" | When chunking and aggregating by source blocks |
| block_type  | str      | no       | Type of the source block (e.g., "paragraph", "message", "section"). Useful for analytics and aggregation. | "paragraph" | For analytics, aggregation, structure recovery |
| block_index | int      | no       | Index of the block in the source document/dialogue. | 3 | For restoring block order |
| block_meta  | dict     | no       | Additional metadata about the block (author, timestamps, etc.). | {"author": "user1"} | For extended analytics |

See also: [ChunkMetrics Fields](#chunkmetrics-fields), [Usage Scenarios](./Usage.md#aggregation-scenarios)

### Conversion

The package provides methods to convert between these formats:

```python
# SemanticChunk to FlatSemanticChunk
flat_chunk = FlatSemanticChunk.from_semantic_chunk(semantic_chunk)
flat_dict = builder.semantic_to_flat(semantic_chunk)

# FlatSemanticChunk to SemanticChunk
semantic_chunk = flat_chunk.to_semantic_chunk()
semantic_chunk = builder.flat_to_semantic(flat_dict)
```

### ChunkMetrics Fields

| Field           | Type    | Description                        |
|-----------------|---------|------------------------------------|
| quality_score   | float   | Quality score [0, 1]               |
| coverage        | float   | Coverage [0, 1]                    |
| cohesion        | float   | Cohesion [0, 1]                    |
| boundary_prev   | float   | Boundary similarity with previous  |
| boundary_next   | float   | Boundary similarity with next      |
| matches         | int     | Retrieval matches                  |
| used_in_generation | bool | Used in generation                 |
| used_as_input   | bool    | Used as input                      |
| used_as_context | bool    | Used as context                    |
| feedback        | FeedbackMetrics | User feedback metrics         |

### FlatSemanticChunk Metrics Fields

| Field           | Type    | Description                        |
|-----------------|---------|------------------------------------|
| coverage        | float   | Coverage [0, 1]                    |
| cohesion        | float   | Cohesion [0, 1]                    |
| boundary_prev   | float   | Boundary similarity with previous  |
| boundary_next   | float   | Boundary similarity with next      |
| start           | int     | Start offset of the chunk in the source text (in bytes or characters) |
| end             | int     | End offset of the chunk in the source text (in bytes or characters) |

## Data Validation

Both models implement strict validation rules:

- UUIDs must be valid UUIDv4 format
- Timestamps must be ISO8601 with timezone
- Links must follow the format "relation:uuid" with valid UUIDs
- Numeric metrics (including coverage, cohesion, boundary_prev, boundary_next) must be within [0, 1]
- Required fields cannot be null

All new metric fields are optional and backward compatible.

## Best Practices

### Identification and Aggregation
- Always set `block_id` for each chunk that belongs to a logical block (paragraph, message, section, etc.) to enable aggregation and traceability.
- Use `block_type` and `block_index` to facilitate analytics and to restore the original order of blocks in the document.
- Store additional context in `block_meta` if you need to track authorship, timestamps, or other block-level metadata.
- The integration layer (not the base chunker) is responsible for assigning and maintaining block-level fields.

### Chunk Linking
- Use the `links` field to express relationships between chunks (e.g., parent-child, related, reference). Format: `relation:uuid4`.
- Validate all UUIDs and link formats strictly ([see Data Validation](#data-validation)).

### Data Consistency
- Ensure all UUIDs are valid UUIDv4 and all timestamps are ISO8601 with timezone.
- Use `ordinal` to preserve chunk order within a block or document.
- Always compute and store `sha256` for deduplication and integrity checks.

### Common Pitfalls
- Do not assign `block_id` at the chunking service level if the service does not know the logical block structure—this is the responsibility of the integration layer.
- Avoid using ambiguous or reused block identifiers; always use UUIDv4 for uniqueness.
- Do not omit required fields (`uuid`, `type`, `text`, `language`, `sha256`, `start`, `end`).

### Example: Aggregating Chunks by Block
```python
from collections import defaultdict
# Suppose you have a list of SemanticChunk objects: chunks
blocks = defaultdict(list)
for chunk in chunks:
    if chunk.block_id:
        blocks[chunk.block_id].append(chunk)
# Now blocks[block_id] contains all chunks for that block
```

### Example: Restoring Document Structure
```python
# To restore the order of blocks and their chunks:
ordered_blocks = sorted(blocks.items(), key=lambda x: x[1][0].block_index or 0)
for block_id, block_chunks in ordered_blocks:
    block_chunks.sort(key=lambda c: c.ordinal or 0)
    # Reconstruct block text
    block_text = " ".join(chunk.text for chunk in block_chunks)
```

See also: [Identification and Aggregation Fields](#identification-and-aggregation-fields), [Usage Scenarios](./Usage.md#aggregation-scenarios), [Data Validation](#data-validation) 