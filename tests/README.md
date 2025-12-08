# RedisDemo Tests

This directory contains comprehensive tests for the RedisDemo project.

## Test Structure

```
tests/
├── __init__.py           # Package initialization
├── conftest.py          # Shared pytest fixtures
├── test_redis_manager.py # Tests for RedisManager class
└── test_main.py         # Tests for main.py functions
```

## Running Tests

### Install Development Dependencies

First, install the development the dependencies including pytest:

```bash
pip install -e ".[dev]"
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Files

```bash
pytest tests/test_redis_manager.py
pytest tests/test_main.py
```

### Run Specific Test Classes

```bash
pytest tests/test_redis_manager.py::TestRedisManagerGet
pytest tests/test_main.py::TestGetProductWithCache
```

### Run Specific Test Methods

```bash
pytest tests/test_redis_manager.py::TestRedisManagerGet::test_get_cache_hit
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
```

This will generate a coverage report in the `htmlcov/` directory.

### Run with Verbose Output

```bash
pytest -v
```

### Run and Show Print Statements

```bash
pytest -s
```

## Test Coverage

### RedisManager Tests (`test_redis_manager.py`)

- **Initialization Tests**: Connection success/failure, custom configurations
- **Get Method Tests**: Cache hits, cache misses, error handling, corrupted data
- **Set Method Tests**: Successful writes, error handling, serialization errors
- **Delete Method Tests**: Successful deletes, error handling
- **Helper Method Tests**: Key prefix handling

### Main Module Tests (`test_main.py`)

- **hello_world Tests**: Basic functionality
- **expensive_db_calculation Tests**: Return structure, timing, consistency
- **get_product_with_cache Tests**: Cache-aside pattern, cache hits/misses
- **Integration Tests**: Full cache-aside pattern flow

## Key Testing Patterns

All tests use mocking to avoid requiring a real Redis instance, making them:
- Fast to execute
- Reliable (no external dependencies)
- To run in CI/CD pipelines

## Adding New Tests

When adding new tests:
1. Follow the existing class-based structure
2. Use descriptive test names that explain what is being tested
3. Mock external dependencies (Redis connections, etc.)
4. Test both success and failure scenarios
