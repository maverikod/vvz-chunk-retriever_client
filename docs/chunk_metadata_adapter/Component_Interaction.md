# Component Interaction

This document describes how the components of the `chunk_metadata_adapter` package interact with each other and how they can be integrated into larger systems.

## Architecture Overview

The package is designed with a layered architecture:

```
┌─────────────────────────────────────┐
│           Client Application         │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│     ChunkMetadataBuilder (Facade)    │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│         Data Models Layer            │
│  ┌───────────────┐ ┌───────────────┐ │
│  │ SemanticChunk │ │FlatSemanticCh.│ │
│  └───────┬───────┘ └───────┬───────┘ │
│          │                 │         │
│  ┌───────▼───────┐         │         │
│  │ ChunkMetrics  │         │         │
│  └───────┬───────┘         │         │
│          │                 │         │
│  ┌───────▼───────┐         │         │
│  │FeedbackMetrics│         │         │
│  └───────────────┘         │         │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│         Validation Layer             │
└─────────────────────────────────────┘
```

## Component Responsibilities

### ChunkMetadataBuilder

Acts as a facade for the system, providing high-level methods:

- `build_flat_metadata` - Creates flat dictionary metadata
- `build_semantic_chunk` - Creates structured object metadata
- `flat_to_semantic` - Converts flat to structured format
- `semantic_to_flat` - Converts structured to flat format

### Data Models

- `SemanticChunk` - Main structured model with nested objects
- `FlatSemanticChunk` - Flattened representation for storage
- `ChunkMetrics` - Contains quality and usage metrics:
    - quality_score, coverage, cohesion, boundary_prev, boundary_next, matches, used_in_generation, used_as_input, used_as_context, feedback
- `FeedbackMetrics` - Contains user feedback information
- Enums (`ChunkType`, `ChunkRole`, `ChunkStatus`) - Define allowed values

### Validation Layer

Built into the data models, it ensures:

- UUID format validation (must be UUIDv4)
- Timestamp format validation (ISO8601 with timezone)
- Link format validation (relation:uuid pattern)
- Numeric range validation for metrics
- Required field validation

## Integration with External Systems

### Storage Systems

The package is designed to integrate with various storage systems:

```
┌─────────────────┐    ┌─────────────────┐
│  Your RAG App   │    │ ChunkMetadata   │
│                 │◄───┤ Builder         │
└────────┬────────┘    └────────┬────────┘
         │                      │
         ▼                      ▼
┌─────────────────┐    ┌─────────────────┐
│ Vector Database │    │  Document Store │
│ (flat format)   │    │(either format)  │
└─────────────────┘    └─────────────────┘
```

#### Vector Database Integration

```python
from chunk_metadata_adapter import ChunkMetadataBuilder
import chromadb  # Example vector DB

# Create a collection in the vector database
collection = chromadb.Client().create_collection("documents")

# Generate metadata for embedding
builder = ChunkMetadataBuilder(project="MyProject")
metadata = builder.build_flat_metadata(
    text="Content to embed",
    source_id=str(source_uuid),
    ordinal=1,
    type="DocBlock",
    language="english",
    coverage=0.9
)

# Add to vector DB (flat format works best)
collection.add(
    ids=[metadata["uuid"]],
    embeddings=get_embeddings(metadata["text"]),
    metadatas=[metadata]
)
```

#### Document Store Integration

```python
from chunk_metadata_adapter import ChunkMetadataBuilder
import json

# Create structured chunk
builder = ChunkMetadataBuilder(project="MyProject")
chunk = builder.build_semantic_chunk(
    text="Document content",
    language="english",
    type="DocBlock",
    source_id=str(source_uuid),
    coverage=0.9
)

# Store in document DB
with open(f"chunks/{chunk.uuid}.json", "w") as f:
    # Convert to flat format if needed
    flat_data = builder.semantic_to_flat(chunk)
    json.dump(flat_data, f)
```

### Processing Pipeline Integration

The package can be integrated into processing pipelines:

```
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
│  Document  │  │   Text     │  │  Metadata  │  │  Storage   │
│  Loading   ├─►│ Chunking   ├─►│ Generation ├─►│   & Index  │
└────────────┘  └────────────┘  └────────────┘  └────────────┘
                                       ▲
                                       │
                               ┌───────┴───────┐
                               │ChunkMetadata  │
                               │   Builder     │
                               └───────────────┘
```

Example pipeline:

```python
def process_document(doc_path, project_name):
    # Load document
    with open(doc_path, "r") as f:
        content = f.read()
    
    # Generate source ID
    source_id = str(uuid.uuid4())
    
    # Create metadata builder
    builder = ChunkMetadataBuilder(project=project_name)
    
    # Chunking and metadata generation
    chunks = []
    for i, text in enumerate(split_into_chunks(content)):
        chunk = builder.build_semantic_chunk(
            text=text,
            language="english",
            type="DocBlock",
            source_id=source_id,
            ordinal=i,
            source_path=doc_path,
            coverage=0.9
        )
        chunks.append(chunk)
    
    # Add relationships between chunks
    link_chunks(chunks)
    
    # Store and index chunks
    store_chunks(chunks)
    
    return chunks
```

## Performance and Scalability

The package is designed to be lightweight and scale with your application:

- Low memory footprint with minimal dependencies
- Efficient validation using Pydantic
- Option to use either flat or structured formats based on performance needs
- Thread-safe operations for parallel processing 