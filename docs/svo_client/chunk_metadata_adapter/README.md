# Chunk Metadata Adapter Documentation

This directory contains documentation for the `chunk_metadata_adapter` package.

## Documentation Files

- [Metadata Structure](Metadata.md) - Description of the metadata structure and fields
- [Usage Guide](Usage.md) - Guide for using the package with examples
- [Component Interaction](Component_Interaction.md) - Description of how the components interact

## Russian Documentation

Russian versions of documentation are available with `.ru` suffix before the extension:
- [Metadata Structure (RU)](Metadata.ru.md)
- [Usage Guide (RU)](Usage.ru.md)
- [Component Interaction (RU)](Component_Interaction.ru.md)

## API Reference

The package provides the following main components:

- `ChunkMetadataBuilder` - Main class for creating and transforming metadata
- `SemanticChunk` - Fully structured model for chunk metadata
- `FlatSemanticChunk` - Flat representation of chunk metadata for storage

For detailed API reference, see the [Python docstrings](../chunk_metadata_adapter/) in the source code.

- Support for extended chunk quality metrics: coverage, cohesion, boundary_prev, boundary_next 