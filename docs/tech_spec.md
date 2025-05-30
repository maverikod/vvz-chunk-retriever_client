# Chunk Retriever Client: Technical Specification

## Overview
This document describes the architecture, requirements, and testing strategy for the asynchronous Python client for the Chunk Retriever microservice.

## Project Structure (PyPi-ready)
- The project must follow the standard PyPi package structure:
  - Source code in a dedicated package directory (e.g., `chunk_retriever_client/`)
  - `examples/` directory at the project root with real usage examples of the client
  - `tests/` directory for unit and integration tests
  - All code and examples must be fully tested (including example scripts)
  - Ready for packaging and publishing to PyPi

## Client Requirements
- **Input parameters:**
  - `url`: Base URL of the Chunk Retriever server
  - `port`: Server port
  - `source_id`: UUID4 string
- **Output:**
  - Tuple `(response, errstr)`
    - `response`: The response from the retriever (parsed JSON or raw text)
    - `errstr`: Error description (string) or empty string if no error. If an error occurs, `response` is `None`.
- **Implementation:**
  - Class-based, with an asynchronous method (can be called without instantiating the class)
  - 100% test coverage (unit + integration)
  - The client must handle **all exceptional situations**, including server unavailability, timeouts, invalid responses, and network errors.

## Testing
- **Unit tests:** Cover all code paths, including error handling.
- **Integration tests:**
  - Use real services:
    - Chunk Retriever: `localhost:8010`
    - SVO Chunker: `localhost:8009`
    - Vector Store DBs: `localhost:3007`, `localhost:8007`
  - Workflow:
    1. Use `@chunk_metadata_adapter` to manage metadata.
    2. Use `@svo_client` to obtain chunks from the chunker.
    3. Use `@vector_store_client` to write/read chunks to/from the DBs.
    4. Query the retriever and verify the response matches the expected chunks in the DBs.
- **Example tests:**
  - All scripts in the `examples/` directory must have corresponding tests that verify their correct operation against the specified servers.

## Dependencies
- `@chunk_metadata_adapter` — metadata manager
- `@svo_client` — chunker client
- `@vector_store_client` — vector store client

## Example Usage
```python
response, errstr = await ChunkRetrieverClient.find_chunks_by_source_id(
    url="http://localhost", port=8010, source_id="b7e2c4a0-1234-4f56-8abc-1234567890ab"
)
```

## Error Handling
- If `source_id` is not a valid UUID4, return error string.
- If network or server error, return error string and `None` as response.
- If response is not valid JSON, return error string and `None` as response.
- All exceptions (including server unavailability, timeouts, etc.) must be handled gracefully and reported via `errstr`.

## File Structure
- `chunk_retriever_client/` — client implementation (PyPi package)
- `examples/` — real usage examples
- `tests/` — unit and integration tests (including tests for examples)
- Documentation in both English (`docs/tech_spec.md`) and Russian (`docs/chunk_metadata_adapter/ru/tech_spec.ru.md`) 