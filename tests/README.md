# Stream Client Test Suite

Comprehensive automated testing for the stream-client project.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run all unit tests (fast)
make test-unit

# Run integration tests (requires server)
make test-integration

# Run all tests
make test

# Generate coverage report
make coverage
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── fixtures/
│   └── sample_responses.py  # Mock API responses
├── unit/                    # Unit tests (mocked, fast)
│   ├── test_api_client.py       # 46 tests for MusicAPIClient
│   ├── test_audio_player.py     # 28 tests for AudioPlayer
│   └── test_metadata_client.py  # 26 tests for MetadataClient
└── integration/             # Integration tests (real server)
    └── test_api_integration.py  # 16 tests for full workflows
```

## Test Coverage

- **100 unit tests** - Run in < 1 second, no server needed
- **16 integration tests** - Test against real server at http://pi-server:8080
- **Total: 116 tests**

### Coverage by Module

- api_client.py: 100%
- audio_player.py: 100%
- metadata_client.py: 100%
- gui_client.py: Partial (GUI testing complex)

## What's Tested

### MusicAPIClient (46 tests)

- Health checks
- Song search (old and new API formats)
- Song streaming
- Server notifications
- Playlist operations (get, create, update, delete)
- Playlist items (add tracks, add groups, remove items)
- Error handling and edge cases

### AudioPlayer (28 tests)

- Playback control (play, pause, resume, stop)
- Volume control with clamping
- State management
- Error handling

### MetadataClient (26 tests)

- Metadata CRUD operations
- Play event recording
- Smart shuffle with criteria
- Edge cases

### Integration Tests (16 tests)

- Real server communication
- Full playback workflows
- Search format compatibility detection
- End-to-end testing

## Running Tests

### Run Specific Tests

```bash
# Single test file
pytest tests/unit/test_api_client.py -v

# Single test class
pytest tests/unit/test_api_client.py::TestMusicAPIClient -v

# Single test
pytest tests/unit/test_api_client.py::TestMusicAPIClient::test_search_songs_success -v

# Tests matching keyword
pytest tests/ -k "playlist" -v
```

### Run with Options

```bash
# Verbose output
pytest tests/ -v

# Stop on first failure
pytest tests/ -x

# Show local variables on failure
pytest tests/ -l

# Generate coverage report
pytest tests/ --cov=. --cov-report=html
```

## CI/CD Integration

GitHub Actions automatically runs tests on every push to main, develop, or claude/* branches.

### Workflow Steps

1. Unit tests on Python 3.9, 3.10, 3.11
2. Integration tests (if server available)
3. Code quality checks (black, flake8, isort)
4. Test summary

View results in the Actions tab on GitHub.

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
    def test_new_feature(self, api_client):
        """Test description."""
        responses.add(
            responses.GET,
            "http://test-server:8080/api/endpoint",
            json={"success": True, "data": "test"},
            status=200
        )

        result = api_client.new_method()
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

    def test_real_workflow(self, api_client):
        """Test against real server."""
        result = api_client.new_method()
        assert result is not None
```

## Debugging Tests

### Common Issues

**Module not found errors**
- Solution: `pip install -r requirements.txt`

**Integration tests fail**
- Solution: Requires server at http://pi-server:8080
- Expected if server not running

**Import errors**
- Solution: Run tests from project root directory

### Debug Output

```bash
# Print all output
pytest tests/ -v -s

# Drop into debugger on failure
pytest tests/ --pdb

# Show full traceback
pytest tests/ --tb=long
```

## Test Markers

```bash
# Run only integration tests
pytest -m integration

# Run only unit tests
pytest -m "not integration"
```

## Best Practices

1. Run unit tests before committing
2. Add tests for new features
3. Mock external dependencies in unit tests
4. Keep tests fast and independent
5. Use descriptive test names
6. Test both success and error cases

## Resources

- pytest documentation: https://docs.pytest.org/
- responses library: https://github.com/getsentry/responses
- pytest-cov: https://pytest-cov.readthedocs.io/
