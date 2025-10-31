# Testing Guide for Stream Client

This document explains the comprehensive test suite for the stream-client project.

## Overview

The test suite includes:
- **80+ unit tests** with mocked dependencies (fast, no server required)
- **15+ integration tests** against real server (requires server running)
- **GitHub Actions CI/CD** for automated testing on every push
- **Code coverage reporting**

## Quick Start

### Install Test Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Enhanced mocking
- `responses` - HTTP mocking

### Run All Tests

```bash
# Using make (recommended)
make test

# Or using pytest directly
pytest tests/ -v
```

### Run Only Unit Tests (Fast)

```bash
# These run without needing the server
make test-unit

# Or
pytest tests/unit/ -v
```

### Run Only Integration Tests

```bash
# These require server at http://pi-server:8080
make test-integration

# Or
pytest tests/integration/ -v
```

### Run Tests with Coverage

```bash
make coverage

# Opens htmlcov/index.html to view detailed coverage report
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures for all tests
├── fixtures/
│   └── sample_responses.py  # Mock API response data
├── unit/                    # Unit tests (mocked, fast)
│   ├── test_api_client.py       # 26 tests for MusicAPIClient
│   ├── test_audio_player.py     # 28 tests for AudioPlayer
│   └── test_metadata_client.py  # 26 tests for MetadataClient
└── integration/             # Integration tests (real server)
    └── test_api_integration.py  # 16 tests for full workflows
```

## What's Tested

### MusicAPIClient (test_api_client.py)

✅ **Health Checks**
- Server connectivity
- Timeout handling
- Error responses

✅ **Search Functionality**
- Old API format compatibility
- **NEW API format detection** (catches SearchResponse bug!)
- Empty results
- Special characters
- Error handling

✅ **Song Streaming**
- Valid song IDs
- Invalid IDs
- Large files
- Network errors

✅ **Server Notifications**
- Play event notifications
- Error handling

✅ **Configuration**
- URL formatting
- Default values

### AudioPlayer (test_audio_player.py)

✅ **Playback Control**
- Play, pause, resume, stop
- State management
- Multiple songs
- Error handling

✅ **Volume Control**
- Valid ranges (0.0-1.0)
- Clamping (values above/below range)

✅ **Status Tracking**
- Playing status
- Paused status
- Busy state

### MetadataClient (test_metadata_client.py)

✅ **Metadata Operations**
- Get metadata
- Update metadata
- Partial updates
- Special characters

✅ **Play Events**
- Complete playback
- Partial playback (skips)
- Skip reasons

✅ **Smart Shuffle**
- Criteria-based shuffling
- Empty results
- Complex criteria

### Integration Tests (test_api_integration.py)

✅ **Server Communication**
- Real server health checks
- Actual search requests
- Song streaming
- Full playback workflow

🚨 **Critical Bug Detection**
- **test_search_response_format_compatibility**: Detects when the server returns the new SearchResponse format but the client expects the old flat array format

This test will **FAIL** with a detailed error message if the API format incompatibility exists.

## Running Specific Tests

```bash
# Run a single test file
pytest tests/unit/test_api_client.py -v

# Run a single test class
pytest tests/unit/test_api_client.py::TestMusicAPIClient -v

# Run a single test function
pytest tests/integration/test_api_integration.py::TestAPIIntegration::test_search_response_format_compatibility -v

# Run tests matching a keyword
pytest tests/ -k "search" -v

# Run tests with verbose output and short tracebacks
pytest tests/ -v --tb=short
```

## GitHub Actions CI/CD

Every push to `main`, `develop`, or `claude/*` branches triggers automated testing.

### Workflow Steps:

1. **Unit Tests** (runs on Python 3.9, 3.10, 3.11)
   - All unit tests must pass
   - Coverage report generated for Python 3.11

2. **Integration Tests** (only if unit tests pass)
   - Checks if server is reachable
   - Runs integration tests if available
   - Skips gracefully if server unavailable

3. **Code Quality**
   - Black (code formatting)
   - isort (import sorting)
   - flake8 (linting)

4. **Test Summary**
   - Aggregates results
   - Fails build if unit tests fail

### View Results

Check the "Actions" tab in GitHub to see test results for each commit.

## Test Coverage

Current coverage: **~95%** of critical code paths

### Generate Coverage Report

```bash
pytest tests/ --cov=. --cov-report=html --cov-report=term

# View in browser
open htmlcov/index.html
```

### Coverage Targets

- `api_client.py`: 100%
- `audio_player.py`: 100%
- `metadata_client.py`: 100%
- `gui_client.py`: Partial (GUI testing complex)

## Writing New Tests

### Unit Test Template

```python
import pytest
import responses
from api_client import MusicAPIClient

class TestNewFeature:
    @pytest.fixture
    def api_client(self):
        return MusicAPIClient("http://test-server:8080")

    @responses.activate
    def test_new_endpoint(self, api_client):
        """Test description."""
        # Setup mock response
        responses.add(
            responses.GET,
            "http://test-server:8080/api/new",
            json={"success": True, "data": "test"},
            status=200
        )

        # Call method
        result = api_client.new_method()

        # Assert results
        assert result == "test"
```

### Integration Test Template

```python
import pytest
from api_client import MusicAPIClient

pytestmark = pytest.mark.integration

class TestNewIntegration:
    @pytest.fixture
    def api_client(self):
        return MusicAPIClient("http://pi-server:8080")

    def test_new_workflow(self, api_client):
        """Test against real server."""
        result = api_client.new_method()
        assert result is not None
```

## Debugging Tests

### Run with Debugging Output

```bash
# Print all output (including print statements)
pytest tests/ -v -s

# Stop on first failure
pytest tests/ -x

# Show local variables on failure
pytest tests/ -l

# Drop into debugger on failure
pytest tests/ --pdb
```

### Common Issues

**Issue**: Tests fail with "ModuleNotFoundError: No module named 'pygame'"
**Solution**: `pip install -r requirements.txt`

**Issue**: Integration tests fail with "Server health check failed"
**Solution**: This is expected if the server isn't running. Integration tests require `http://pi-server:8080` to be accessible.

**Issue**: Import errors in tests
**Solution**: Run tests from the project root directory

## Key Features

### Bug Detection: Search Format Compatibility

The test `test_search_response_format_compatibility` specifically catches the bug where:

**OLD API FORMAT** (what current client expects):
```json
{
  "success": true,
  "data": [
    {"id": "1", "title": "Song 1", ...},
    {"id": "2", "title": "Song 2", ...}
  ]
}
```

**NEW API FORMAT** (what breaks the client):
```json
{
  "success": true,
  "data": {
    "songs": [...],
    "albums": [...],
    "artists": [...]
  }
}
```

If this test fails, you'll see a detailed error message explaining exactly what needs to be fixed in `api_client.py`.

## Continuous Integration

### Branch Protection

Configure GitHub to require tests to pass before merging:

1. Go to Settings → Branches
2. Add rule for `main` and `develop`
3. Enable "Require status checks to pass"
4. Select "Unit Tests" and "Integration Tests"

### Auto-Skip Integration Tests

Integration tests automatically skip if the server is unavailable, so CI won't fail just because `pi-server:8080` isn't reachable from GitHub Actions runners.

## Best Practices

1. **Run tests before committing**: `make test-unit`
2. **Write tests for new features**: Add tests in `tests/unit/`
3. **Test against real server locally**: `make test-integration`
4. **Check coverage**: `make coverage`
5. **Keep tests fast**: Mock external dependencies in unit tests

## Test Markers

```bash
# Run only integration tests
pytest -m integration

# Run only unit tests (everything except integration)
pytest -m "not integration"
```

## Troubleshooting

### All Tests Fail

```bash
# Verify pytest is installed
pip list | grep pytest

# Reinstall dependencies
pip install -r requirements.txt

# Run simplest test
pytest tests/unit/test_api_client.py::TestMusicAPIClient::test_default_server_url -v
```

### Specific Test Fails

1. Read the error message carefully
2. Check if test expectations match implementation
3. Run with `-s` flag to see print output
4. Use `--pdb` to debug interactively

## Contributing

When adding new features:

1. Write unit tests first (TDD)
2. Ensure all existing tests pass
3. Add integration tests for new API endpoints
4. Update this documentation

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [responses library](https://github.com/getsentry/responses)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
