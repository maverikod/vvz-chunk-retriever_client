# Metadata Structure

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