# FastAPI Application - API Endpoints Quick Reference

## Endpoint Summary Table

| Module | HTTP Method | Endpoint | Full Path | Auth | Status | Key Tests |
|--------|-------------|----------|-----------|------|--------|-----------|
| **Health** | GET | /health | /health | None | 200 | Health status response |
| **Auth** | POST | /users | /api/users | None | 201 | Register, duplicate email, validation |
| **Auth** | POST | /users/login | /api/users/login | None | 200 | Login, invalid credentials |
| **Auth** | GET | /user | /api/user | Required | 200 | Get current user, token validation |
| **Profiles** | GET | /profiles/{name} | /api/profiles/{name} | Optional | 200 | Get profile, following status |
| **Profiles** | POST | /profiles/{name}/follow | /api/profiles/{name}/follow | Required | 200 | Follow user, idempotent |
| **Profiles** | DELETE | /profiles/{name}/follow | /api/profiles/{name}/follow | Required | 200 | Unfollow user, idempotent |
| **Articles** | POST | /articles | /api/articles | Required | 201 | Create article, slug generation |
| **Articles** | GET | /articles/{slug} | /api/articles/{slug} | Optional | 200 | Get article, favorited status |
| **Articles** | PUT | /articles/{slug} | /api/articles/{slug} | Required | 200 | Update article, authorization |
| **Articles** | DELETE | /articles/{slug} | /api/articles/{slug} | Required | 204 | Delete article, authorization |
| **Articles** | POST | /articles/{slug}/favorite | /api/articles/{slug}/favorite | Required | 200 | Favorite article, count increment |
| **Articles** | DELETE | /articles/{slug}/favorite | /api/articles/{slug}/favorite | Required | 200 | Unfavorite article, count decrement |
| **Articles** | GET | /articles | /api/articles | Optional | 200 | List articles, filtering, pagination |
| **Articles** | GET | /articles/feed | /api/articles/feed | Required | 200 | Get user feed, pagination |
| **Tags** | GET | /tags | /api/tags | None | 200 | Get all tags, uniqueness |
| **Comments** | POST | /articles/{slug}/comments | /api/articles/{slug}/comments | Required | 201 | Create comment on article |
| **Comments** | GET | /articles/{slug}/comments | /api/articles/{slug}/comments | Optional | 200 | List article comments |
| **Comments** | DELETE | /articles/{slug}/comments/{id} | /api/articles/{slug}/comments/{id} | Required | 204 | Delete comment, authorization |

---

## Authentication Requirements

### Public Endpoints (No Auth Required)
1. `GET /health` - Health check
2. `POST /api/users` - User registration
3. `POST /api/users/login` - User login
4. `GET /api/tags` - Get all tags

### Protected Endpoints (Auth Required)
1. `GET /api/user` - Get current user
2. `POST /api/profiles/{name}/follow` - Follow user
3. `DELETE /api/profiles/{name}/follow` - Unfollow user
4. `POST /api/articles` - Create article
5. `PUT /api/articles/{slug}` - Update article
6. `DELETE /api/articles/{slug}` - Delete article
7. `POST /api/articles/{slug}/favorite` - Favorite article
8. `DELETE /api/articles/{slug}/favorite` - Unfavorite article
9. `GET /api/articles/feed` - Get user feed
10. `POST /api/articles/{slug}/comments` - Create comment
11. `DELETE /api/articles/{slug}/comments/{id}` - Delete comment

### Optional Auth Endpoints (Behavior Differs)
1. `GET /api/profiles/{name}` - Get profile (following status varies)
2. `GET /api/articles/{slug}` - Get article (favorited status varies)
3. `GET /api/articles` - List articles (favorited status varies)
4. `GET /api/articles/{slug}/comments` - List comments (following status varies)

---

## HTTP Status Codes Summary

| Code | Count | Used For |
|------|-------|----------|
| 200 | 10 | Successful GET, POST (updates), DELETE with response |
| 201 | 3 | Successful resource creation (POST) |
| 204 | 3 | Successful resource deletion (DELETE) |
| 400 | - | Domain-level business logic errors |
| 401 | - | Missing/invalid authentication |
| 403 | - | Authorization failure (forbidden) |
| 404 | - | Resource not found |
| 422 | - | Validation/duplicate entity errors |

---

## Query Parameters by Endpoint

### GET /api/articles
- `tag` (string, optional) - Filter by tag name
- `author` (string, optional) - Filter by author username
- `favorited` (string, optional) - Filter by user who favorited
- `limit` (integer, 1-100, default=20) - Results per page
- `offset` (integer, >=0, default=0) - Pagination offset

### GET /api/articles/feed
- `limit` (integer, 1-100, default=20) - Results per page
- `offset` (integer, >=0, default=0) - Pagination offset

---

## Request/Response Models

### Auth Module

**RegisterUserRequest**
```json
{"user": {"email": "string", "name": "string", "password": "string"}}
```

**LoginUserRequest**
```json
{"user": {"email": "string", "password": "string"}}
```

**AuthResponse**
```json
{"email": "string", "token": "string", "name": "string", "bio": "string", "image": "string"}
```

**UserResponse**
```json
{"id": "integer", "email": "string", "name": "string", "bio": "string", "image": "string", "created_at": "datetime", "updated_at": "datetime"}
```

### Articles Module

**CreateArticleRequest**
```json
{"article": {"title": "string", "description": "string", "body": "string", "tagList": ["string"]}}
```

**UpdateArticleRequest**
```json
{"article": {"title": "string", "description": "string", "body": "string"}}
```

**ArticleResponse** (includes full article data with author profile and tags)

**MultipleArticlesResponse**
```json
{"articles": [ArticleSchema], "articlesCount": "integer"}
```

### Comments Module

**CreateCommentRequest**
```json
{"comment": {"body": "string"}}
```

**CommentResponse** (includes comment data with author profile)

**MultipleCommentsResponse**
```json
{"comments": [CommentSchema]}
```

---

## Authorization Header Format

```
Authorization: Token <jwt_token>
```

**Example:**
```
Authorization: Token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Error Response Format

All errors follow this structure:

```json
{"errors": {"{field_or_body}": ["error message"]}}
```

**Examples:**
- 404: `{"errors": {"body": ["Article not found"]}}`
- 422: `{"errors": {"email": ["Email already exists"]}}`
- 403: `{"errors": {"body": ["Not authorized to modify"]}}`
- 401: `{"errors": {"body": ["Invalid or expired token"]}}`

---

## Testing Statistics

- **Total Endpoints:** 19
- **Total Test Cases:** 150+ (estimated with all scenarios)
- **Public Endpoints:** 4
- **Protected Endpoints:** 11
- **Optional Auth Endpoints:** 4
- **Modules:** 5 (Auth, Profiles, Articles, Comments, Tags)

### Coverage by Module:
- **Auth:** 3 endpoints, ~25 test cases
- **Profiles:** 3 endpoints, ~20 test cases
- **Articles:** 8 endpoints, ~70 test cases
- **Comments:** 3 endpoints, ~25 test cases
- **Tags:** 1 endpoint, ~5 test cases
- **Health:** 1 endpoint, ~3 test cases

