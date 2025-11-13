# FastAPI Application - API Testing Guide & Documentation

## Overview

This directory contains comprehensive documentation for all API endpoints in the FastAPI application, organized to help with integration testing. The application implements a Real World Conduit-like API with user authentication, articles, comments, and social features.

---

## Documentation Files

### 1. **API_ENDPOINTS_QUICK_REFERENCE.md**
**Best for:** Quick lookup and endpoint overview
- Quick reference table of all endpoints
- Authentication requirements breakdown
- HTTP status codes summary
- Query parameter documentation
- Request/Response model summaries
- Error response formats
- Testing statistics

**Use case:** When you need to quickly find an endpoint or check authentication requirements.

---

### 2. **API_ENDPOINTS_INTEGRATION_TESTS.md** 
**Best for:** Comprehensive integration test planning
- Complete endpoint documentation with detailed test scenarios
- All endpoints organized by module
- Request/Response schemas with examples
- Key test scenarios for each endpoint
- Error response handling guide
- Authentication header format
- Testing recommendations and best practices

**Use case:** When planning integration tests or understanding all test scenarios for an endpoint.

---

### 3. **API_ENDPOINTS_BY_MODULE.md**
**Best for:** Understanding module architecture and dependencies
- Detailed module-by-module breakdown
- Use case and dependency information for each endpoint
- Inter-module dependencies and data flows
- Error handling patterns by module
- Authentication flow diagram
- Test execution order recommendations

**Use case:** When you need to understand how modules interact or plan cross-module tests.

---

## Quick Statistics

| Metric | Count |
|--------|-------|
| **Total Endpoints** | 19 |
| **Public Endpoints** | 4 |
| **Protected Endpoints** | 11 |
| **Optional Auth Endpoints** | 4 |
| **Modules** | 5 |
| **Expected Test Cases** | 150+ |

### Endpoint Breakdown by Module:
- **Auth Module:** 3 endpoints
- **Profiles Module:** 3 endpoints  
- **Articles Module:** 8 endpoints
- **Comments Module:** 3 endpoints
- **Tags Module:** 1 endpoint
- **Health Check:** 1 endpoint

### Endpoint Breakdown by Method:
- **GET:** 8 endpoints
- **POST:** 6 endpoints
- **PUT:** 1 endpoint
- **DELETE:** 4 endpoints

---

## Module Architecture

```
FastAPI Application
├── Health Check: GET /health
│
└── /api (prefix)
    ├── Auth Module
    │   ├── POST /users (Register)
    │   ├── POST /users/login (Login)
    │   └── GET /user (Get Current User)
    │
    ├── Profiles Module
    │   ├── GET /profiles/{name}
    │   ├── POST /profiles/{name}/follow
    │   └── DELETE /profiles/{name}/follow
    │
    ├── Articles Module
    │   ├── POST /articles
    │   ├── GET /articles
    │   ├── GET /articles/{slug}
    │   ├── PUT /articles/{slug}
    │   ├── DELETE /articles/{slug}
    │   ├── POST /articles/{slug}/favorite
    │   ├── DELETE /articles/{slug}/favorite
    │   └── GET /articles/feed
    │
    ├── Tags Module
    │   └── GET /tags
    │
    └── Comments Module (under articles)
        ├── POST /articles/{slug}/comments
        ├── GET /articles/{slug}/comments
        └── DELETE /articles/{slug}/comments/{id}
```

---

## Authentication

### Header Format
All protected endpoints require:
```
Authorization: Token <jwt_token>
```

### Token Claims
- Must include `user_id`
- Validated by `JWTService`
- Format: `Token {JWT_STRING}`

### Protected Endpoints (11 total)
- `GET /api/user`
- `POST /api/profiles/{name}/follow`
- `DELETE /api/profiles/{name}/follow`
- `POST /api/articles`
- `PUT /api/articles/{slug}`
- `DELETE /api/articles/{slug}`
- `POST /api/articles/{slug}/favorite`
- `DELETE /api/articles/{slug}/favorite`
- `GET /api/articles/feed`
- `POST /api/articles/{slug}/comments`
- `DELETE /api/articles/{slug}/comments/{id}`

### Optional Auth Endpoints (4 total)
- `GET /api/profiles/{name}` - following status varies
- `GET /api/articles/{slug}` - favorited status varies
- `GET /api/articles` - favorited status varies
- `GET /api/articles/{slug}/comments` - following status varies

### Public Endpoints (4 total)
- `GET /health`
- `POST /api/users` (Register)
- `POST /api/users/login` (Login)
- `GET /api/tags`

---

## Testing Recommendations

### 1. Setup/Teardown Fixtures
Create test fixtures for:
- Test database with sample data
- Multiple test users (3+ users)
- Multiple test articles with tags
- Follow relationships
- Favorite relationships
- Comments on various articles

### 2. Test Organization
```
tests/
├── integration/
│   ├── test_health.py
│   ├── test_auth.py
│   ├── test_profiles.py
│   ├── test_articles.py
│   ├── test_comments.py
│   ├── test_tags.py
│   └── test_cross_module.py
└── conftest.py (fixtures)
```

### 3. Authentication Testing
- Token generation consistency
- Token expiry handling
- Invalid token formats
- Missing headers
- Malformed headers

### 4. Authorization Testing
- Owner operations (update/delete own resources)
- Non-owner operations (403 Forbidden)
- Read permissions (no auth required)

### 5. Data Validation Testing
- Boundary conditions
- Required fields
- Invalid formats
- Field length limits
- Unique constraints

### 6. Edge Cases
- Concurrent operations
- Bulk operations with pagination
- Cascade operations
- Race conditions on favorites/follows
- Empty result sets
- Large datasets

### 7. Error Handling
Test all exception mappings:
- **EntityNotFoundException** → 404
- **EntityAlreadyExistsException** → 422
- **ValidationException** → 422
- **AuthorizationException** → 403
- **DomainException** → 400

---

## HTTP Status Codes Used

| Status | Meaning | Used In |
|--------|---------|---------|
| 200 | OK | GET, POST (updates), DELETE (with response) |
| 201 | Created | POST (resource creation) |
| 204 | No Content | DELETE (no response body) |
| 400 | Bad Request | Domain logic errors |
| 401 | Unauthorized | Missing/invalid auth |
| 403 | Forbidden | Authorization failure |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation/duplicate errors |

---

## Key Test Scenarios by Endpoint

### Auth Module (25 test cases)
**POST /users - Register**
- Valid registration
- Duplicate email
- Invalid email format
- Missing fields
- Password validation
- Token generation

**POST /users/login - Login**
- Valid login
- User not found
- Wrong password
- Missing fields
- Token validity

**GET /user - Get Current User**
- Retrieve user info
- Invalid token
- Missing header
- Malformed header
- Expired token
- User not found

### Profiles Module (20 test cases)
**GET /profiles/{name} - Get Profile**
- Get without auth
- Get with auth
- User not found
- Following status accuracy

**POST /profiles/{name}/follow - Follow**
- Follow existing user
- Follow non-existent user
- Cannot follow self
- Already following (idempotent)
- Missing auth

**DELETE /profiles/{name}/follow - Unfollow**
- Unfollow followed user
- Unfollow non-existent user
- Unfollow when not following (idempotent)
- Missing auth

### Articles Module (70 test cases)
**POST /articles - Create**
- Create with all fields
- Create with tags
- Create without tags
- Missing required fields
- Slug generation
- Author set correctly

**GET /articles/{slug} - Get**
- Get existing article
- Get non-existent article
- Without auth
- With auth
- Favorited status accuracy

**PUT /articles/{slug} - Update**
- Update by author
- Update non-existent article
- Unauthorized update
- Partial updates
- Slug immutability

**DELETE /articles/{slug} - Delete**
- Delete by author
- Delete non-existent article
- Unauthorized delete
- Cascading deletions

**POST/DELETE /articles/{slug}/favorite - Favorite/Unfavorite**
- Favorite/unfavorite existing article
- Favorite/unfavorite non-existent article
- Count changes correctly
- Idempotency

**GET /articles - List**
- List all articles
- Filter by tag
- Filter by author
- Filter by favorited
- Pagination
- Limit validation (1-100)

**GET /articles/feed - Feed**
- Get feed for user following others
- Empty feed when user follows no one
- Pagination
- Only followed author articles

### Comments Module (25 test cases)
**POST /articles/{slug}/comments - Create**
- Create on existing article
- Create on non-existent article
- Empty body rejection
- Author set correctly

**GET /articles/{slug}/comments - List**
- List for article with comments
- List for article with no comments
- List for non-existent article
- Author info included

**DELETE /articles/{slug}/comments/{id} - Delete**
- Delete by author
- Delete non-existent comment
- Unauthorized delete
- Comment removed from list

### Tags Module (5 test cases)
**GET /tags - Get Tags**
- Retrieve all tags
- Tag uniqueness
- Empty tags list
- Correct tag listing

---

## Data Models Reference

### User Response
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "username",
  "bio": "user bio",
  "image": "https://image.url",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Article Response
```json
{
  "slug": "article-title-slug",
  "title": "Article Title",
  "description": "Brief description",
  "body": "Full article content",
  "tagList": ["tag1", "tag2"],
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z",
  "favorited": false,
  "favoritesCount": 5,
  "author": {
    "username": "author_name",
    "bio": "author bio",
    "image": "https://image.url",
    "following": false
  }
}
```

### Comment Response
```json
{
  "id": 1,
  "body": "Comment text",
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z",
  "author": {
    "username": "author_name",
    "bio": "author bio",
    "image": "https://image.url",
    "following": false
  }
}
```

### Profile Response
```json
{
  "name": "username",
  "bio": "user bio",
  "image": "https://image.url",
  "following": false
}
```

---

## Integration Test Template

```python
import pytest
from httpx import AsyncClient
from src.main import app

class TestArticlesAPI:
    """Test articles module endpoints."""

    @pytest.mark.asyncio
    async def test_create_article_success(self, client: AsyncClient, token: str):
        """Test creating an article with valid data."""
        response = await client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Description",
                    "body": "Body content",
                    "tagList": ["test", "api"]
                }
            },
            headers={"Authorization": f"Token {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["article"]["title"] == "Test Article"
        assert data["article"]["tagList"] == ["test", "api"]
        assert "slug" in data["article"]
        assert data["article"]["author"]["username"] is not None

    @pytest.mark.asyncio
    async def test_create_article_missing_auth(self, client: AsyncClient):
        """Test creating article without authentication."""
        response = await client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Description",
                    "body": "Body content",
                    "tagList": []
                }
            }
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_article_by_slug(self, client: AsyncClient):
        """Test retrieving an article by slug."""
        # Setup: create an article first
        # Execute: get the article
        # Assert: response contains correct data
        pass
```

---

## Development Tools

### Running Tests
```bash
# Run all integration tests
pytest tests/integration/

# Run specific test module
pytest tests/integration/test_articles.py

# Run with coverage
pytest --cov=src tests/integration/

# Run in verbose mode
pytest -v tests/integration/
```

### API Documentation
- Swagger UI (dev): `http://localhost:8000/api/docs`
- ReDoc (dev): `http://localhost:8000/api/redoc`

### Debugging
- Enable SQL query logging in config
- Use pytest fixtures for consistent test data
- Log all HTTP requests/responses in tests

---

## Common Issues & Solutions

### Issue: JWT Token Validation Fails
**Solution:** Ensure token format is `Token {jwt_string}`, not just the JWT string.

### Issue: 422 Validation Error on Valid Data
**Solution:** Check request/response wrapper structure. The API uses nested objects (e.g., `{"user": {...}}`, `{"article": {...}}`).

### Issue: 403 Forbidden on Own Resource
**Solution:** Verify author_id matches current user. Check that user is properly authenticated.

### Issue: Slug Not Generated
**Solution:** Ensure article body, title, and description are non-empty strings. Slug generation may fail on invalid input.

---

## Next Steps for Testing Implementation

1. **Create test fixtures** in `tests/conftest.py`
   - Database setup/teardown
   - User creation helpers
   - Authentication helper

2. **Implement test cases** following the test scenarios
   - Start with Auth module
   - Move to Profiles
   - Then Articles and Comments

3. **Set up CI/CD** to run tests
   - Pre-commit hooks
   - GitHub Actions or similar

4. **Add test coverage tracking**
   - Aim for 80%+ coverage
   - Track by module

5. **Document edge cases** discovered during testing

---

## Files Reference

- **Route Files:** `src/modules/*/presentation/routes.py`
- **Use Cases:** `src/modules/*/application/commands/*.py` and `queries/*.py`
- **Repositories:** `src/modules/*/infrastructure/repositories.py`
- **Schemas:** `src/modules/*/presentation/schemas.py`
- **DTOs:** `src/modules/*/application/dtos.py`
- **Exception Handlers:** `src/main.py` (lines 103-165)

---

## Additional Resources

- RealWorld Conduit API Spec: https://api.realworld.io/api-docs/
- FastAPI Documentation: https://fastapi.tiangolo.com/
- JWT Authentication: https://tools.ietf.org/html/rfc7519
- HTTP Status Codes: https://httpwg.org/specs/rfc9110.html

