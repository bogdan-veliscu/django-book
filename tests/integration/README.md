# Integration Tests

This directory contains comprehensive integration tests for the FastAPI application API endpoints. These tests verify the complete behavior of the application including database operations, authentication, and HTTP responses.

## Test Coverage

### Overview
- **124 integration test cases** across 4 modules
- **19 API endpoints** fully tested
- **Authentication, authorization, validation, and error handling** comprehensively covered

### Test Files

| File | Tests | Endpoints Covered |
|------|-------|-------------------|
| `test_auth_api.py` | 31 tests | 3 auth endpoints (register, login, get user) |
| `test_profiles_api.py` | 24 tests | 3 profile endpoints (get, follow, unfollow) |
| `test_articles_api.py` | 47 tests | 9 article endpoints (CRUD, favorite, feed, tags) |
| `test_comments_api.py` | 22 tests | 3 comment endpoints (create, list, delete) |

### Module Breakdown

#### Auth Module (31 tests)
- POST /api/users - Register new user (10 tests)
- POST /api/users/login - Login existing user (9 tests)
- GET /api/user - Get current authenticated user (12 tests)

**Covers:** Success cases, validation errors, duplicate email, invalid credentials, token format, expired tokens, authorization headers

#### Profiles Module (24 tests)
- GET /api/profiles/{name} - Get user profile (7 tests)
- POST /api/profiles/{name}/follow - Follow user (8 tests)
- DELETE /api/profiles/{name}/follow - Unfollow user (9 tests)

**Covers:** Following status, authentication requirements, idempotency, self-follow prevention, user not found, response structure

#### Articles Module (47 tests)
- POST /api/articles - Create article (9 tests)
- GET /api/articles/{slug} - Get single article (4 tests)
- PUT /api/articles/{slug} - Update article (5 tests)
- DELETE /api/articles/{slug} - Delete article (4 tests)
- POST /api/articles/{slug}/favorite - Favorite article (4 tests)
- DELETE /api/articles/{slug}/favorite - Unfavorite article (4 tests)
- GET /api/articles - List articles with filters (9 tests)
- GET /api/articles/feed - Get personalized feed (4 tests)
- GET /api/tags - Get all tags (4 tests)

**Covers:** CRUD operations, filtering (tag, author, favorited), pagination, favorite/unfavorite idempotency, authorization, validation, feed from followed authors

#### Comments Module (22 tests)
- POST /api/articles/{slug}/comments - Create comment (8 tests)
- GET /api/articles/{slug}/comments - List comments (7 tests)
- DELETE /api/articles/{slug}/comments/{id} - Delete comment (7 tests)

**Covers:** Comment creation/deletion, author authorization, validation, following status, article not found, idempotent operations

## Prerequisites

### 1. Database Setup
Integration tests require a PostgreSQL test database:

```bash
# Create test database
createdb conduit_test

# Or using PostgreSQL client
psql -U postgres -c "CREATE DATABASE conduit_test;"
```

### 2. Redis Setup
Tests use Redis for caching (test database 1):

```bash
# Ensure Redis is running
redis-cli ping  # Should return PONG
```

### 3. Environment Configuration
The test suite uses the following configuration (defined in `tests/conftest.py`):

```python
database_url="postgresql+asyncpg://postgres:postgres@localhost:5432/conduit_test"
redis_url="redis://localhost:6379/1"
environment="development"
```

## Running Tests

### Run All Integration Tests

```bash
# Using uv (recommended)
uv run pytest tests/integration/ -v

# Using pytest directly
pytest tests/integration/ -v

# With coverage report
uv run pytest tests/integration/ --cov=src --cov-report=html
```

### Run Specific Module Tests

```bash
# Auth tests only
uv run pytest tests/integration/test_auth_api.py -v

# Profiles tests only
uv run pytest tests/integration/test_profiles_api.py -v

# Articles tests only
uv run pytest tests/integration/test_articles_api.py -v

# Comments tests only
uv run pytest tests/integration/test_comments_api.py -v
```

### Run Specific Test Class or Test

```bash
# Run specific test class
uv run pytest tests/integration/test_auth_api.py::TestRegisterUser -v

# Run specific test
uv run pytest tests/integration/test_auth_api.py::TestRegisterUser::test_register_user_success -v
```

### Run with Detailed Output

```bash
# Show print statements and detailed output
uv run pytest tests/integration/ -vv -s

# Show only test names (no output)
uv run pytest tests/integration/ -v

# Show test durations
uv run pytest tests/integration/ -v --durations=10
```

## Using Docker Compose

The easiest way to run integration tests is using Docker Compose to start all required services:

```bash
# Start PostgreSQL and Redis
docker-compose up -d db redis

# Wait for services to be ready
sleep 5

# Run tests
uv run pytest tests/integration/ -v

# Stop services when done
docker-compose down
```

## Test Fixtures

Integration tests use the following fixtures (defined in `tests/conftest.py` and `tests/integration/conftest.py`):

### Database Fixtures
- `db_manager` - Database manager with connection pool
- `db_session` - Database session with automatic rollback
- `test_settings` - Test configuration settings

### HTTP Client Fixtures
- `client` - Unauthenticated HTTP client
- `authenticated_client` - HTTP client with test_user auth
- `authenticated_client2` - HTTP client with test_user2 auth

### User Fixtures
- `test_user` - First test user (testuser@example.com)
- `test_user2` - Second test user (test2@example.com)
- `test_user_token` - JWT token for test_user
- `test_user2_token` - JWT token for test_user2

### Repository Fixtures
- `user_repository` - UserRepository instance
- `jwt_service` - JWTService instance

## Test Data Management

### Automatic Cleanup
- Each test runs in a transaction that is rolled back after completion
- Tests are isolated and can run in any order
- Database state is reset between tests

### Test Users
Tests create standard test users with these credentials:
- **User 1:** testuser / test@example.com / password123
- **User 2:** testuser2 / test2@example.com / password123

### Test Articles
Articles are created with predictable patterns:
- Titles: "Test Article 1", "Test Article 2", etc.
- Slugs: "test-article-1", "test-article-2", etc.
- Tags: ["test", "python", "fastapi"]

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: conduit_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:6
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install dependencies
        run: uv sync

      - name: Run integration tests
        run: uv run pytest tests/integration/ -v --cov=src

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Troubleshooting

### Connection Refused Error

```
ConnectionRefusedError: [Errno 111] Connect call failed ('127.0.0.1', 5432)
```

**Solution:** Ensure PostgreSQL is running:
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Start PostgreSQL (Ubuntu/Debian)
sudo systemctl start postgresql

# Start PostgreSQL (macOS with Homebrew)
brew services start postgresql@15
```

### Database Does Not Exist

```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) FATAL:  database "conduit_test" does not exist
```

**Solution:** Create the test database:
```bash
createdb conduit_test
```

### Redis Connection Error

```
redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379. Connection refused.
```

**Solution:** Ensure Redis is running:
```bash
# Check if Redis is running
redis-cli ping

# Start Redis (Ubuntu/Debian)
sudo systemctl start redis

# Start Redis (macOS with Homebrew)
brew services start redis
```

### Permission Denied

```
psycopg2.OperationalError: FATAL:  role "postgres" does not exist
```

**Solution:** Update database URL in `tests/conftest.py` with your PostgreSQL credentials.

## Coverage Goals

Current integration test coverage targets:

- **Overall:** 80%+ code coverage including presentation, infrastructure, and use case layers
- **API Endpoints:** 100% of public endpoints tested
- **Auth Flows:** All authentication and authorization scenarios covered
- **Error Handling:** All error responses (400, 401, 403, 404, 422) verified
- **Edge Cases:** Idempotency, validation, boundary conditions tested

## Best Practices

1. **Test Independence:** Each test should work in isolation
2. **Descriptive Names:** Test names clearly describe what is being tested
3. **Arrange-Act-Assert:** Follow AAA pattern in test structure
4. **Use Fixtures:** Leverage fixtures for common setup
5. **Test Real Behavior:** Integration tests should test actual HTTP requests and database operations
6. **Clean Up:** Use transaction rollback for automatic cleanup
7. **Error Messages:** Include descriptive assertion messages

## Related Documentation

- `API_TESTING_GUIDE.md` - Complete API endpoint documentation
- `API_ENDPOINTS_INTEGRATION_TESTS.md` - Detailed test scenarios for each endpoint
- `API_ENDPOINTS_QUICK_REFERENCE.md` - Quick reference for all endpoints
- `tests/conftest.py` - Global test fixtures and configuration
- `tests/integration/conftest.py` - Integration-specific fixtures

## Contributing

When adding new integration tests:

1. Follow the existing test structure and naming conventions
2. Add tests for both success and error cases
3. Include edge cases and boundary conditions
4. Test with and without authentication where applicable
5. Verify response structure and status codes
6. Add docstrings explaining what each test verifies
7. Update this README with new test counts

## Questions or Issues?

If you encounter problems running integration tests:

1. Check Prerequisites section above
2. Review Troubleshooting section
3. Verify services are running (PostgreSQL, Redis)
4. Check test database permissions
5. Review error messages in test output
