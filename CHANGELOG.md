# Changelog

All notable changes to this project are documented in this file.

This project follows a Keep a Changelog style and uses Semantic Versioning (`MAJOR.MINOR.PATCH`) for releases.

## [Unreleased]

### Added

- Lightweight static demo page in `demo/` for:
  - paste seed queries
  - generate JSONL preview
  - download JSONL file
- Demo deployment instructions in `demo/README.md`.
- `CONTRIBUTING.md` with setup, test, and merge request guidance.

### Changed

- Improved root `README.md` structure and discoverability:
  - clearer project positioning and quick links
  - table of contents
  - refined quick start and output descriptions
  - demo, roadmap, and contributing sections

## [0.1.0]

### Added

- Initial `nativqa` package and CLI entrypoint.
- Query collection workflow using seed queries and search engines.
- Domain reliability checking script.
- LLM-based annotation helper script.
- Basic unit/integration test scaffold in `tests/`.
