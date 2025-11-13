# Technical Debt & Implementation Plan

**Document Version**: 2.0
**Last Updated**: 2025-01-12
**Status**: Comprehensive Technical Review Complete

---

## Executive Summary

This document provides a complete technical debt review of the RealWorld Conduit migration project (both FastAPI backend and Lit PWA frontend), identifies critical issues, and provides a detailed remediation plan.

### Current State
- **Backend**: 5 phases complete, 82 tests passing, but **significant technical debt**
- **Frontend**: Only phases 1-2 complete (setup), **requires full implementation**

### Priority Summary
- **🔴 Critical (Fix Immediately)**: 6 backend issues + complete frontend
- **🟡 High Priority (Fix Soon)**: 12 issues
- **🟢 Medium Priority (Technical Debt)**: 20+ issues

### Estimated Timeline
- **Backend Fixes**: 3 weeks
- **Frontend Implementation**: 7 weeks
- **Total**: 10-12 weeks for production-ready application

---

## Table of Contents

1. [Backend Technical Debt](#backend-technical-debt)
2. [Frontend Technical Debt](#frontend-technical-debt)
3. [Infrastructure Issues](#infrastructure-issues)
4. [Security Concerns](#security-concerns)
5. [Remediation Plan](#remediation-plan)
6. [Implementation Checklist](#implementation-checklist)

---

## Backend Technical Debt

### 🔴 CRITICAL ISSUES (Fix Immediately)

#### 1. Missing Authentication Dependencies File ⚠️
**Severity**: Critical - Application won't start
**Files Affected**:
- `src/modules/articles/presentation/routes.py:31`
- `src/modules/comments/presentation/routes.py:13`

**Problem**:
```python
from src.modules.auth.presentation.dependencies import get_current_user, get_optional_user
# ❌ This file doesn't exist!
```

**Impact**: Import errors prevent application startup

**Fix Required**:
Create `src/modules/auth/presentation/dependencies.py`:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.infrastructure.database import get_db_session
from src.modules.auth.domain.entities import User
from src.modules.auth.infrastructure.jwt import JWTService
from src.modules.auth.infrastructure.repositories import UserRepository

security = HTTPBearer()
jwt_service = JWTService()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Extract and verify JWT token, return user dict."""
    try:
        payload = jwt_service.decode_token(credentials.credentials)
        user_repo = UserRepository(session)
        user = await user_repo.get_by_email(payload.get("sub"))

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
    session: AsyncSession = Depends(get_db_session),
) -> dict | None:
    """Return user if authenticated, None otherwise."""
    if not credentials:
        return None
    try:
        return await get_current_user(credentials, session)
    except HTTPException:
        return None
```

---

#### 2. Broken Article List Endpoint ⚠️
**Severity**: Critical - Core feature broken
**File**: `src/modules/articles/presentation/routes.py:363-364`

**Problem**:
```python
else:
    # Get all articles (we'll need to add this method)
    article_entities = []  # ❌ Returns empty array!
```

**Impact**: Users can't browse all articles

**Fix Required**:
1. Add method to `ArticleRepository`:
```python
async def list_all(
    self, limit: int = 20, offset: int = 0
) -> list[Article]:
    """List all articles."""
    stmt = (
        select(ArticleModel)
        .options(
            selectinload(ArticleModel.tags),
            selectinload(ArticleModel.favorited_by)
        )
        .order_by(ArticleModel.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await self._session.execute(stmt)
    models = result.scalars().all()
    return [self._model_to_entity(model) for model in models]
```

2. Call it in route:
```python
else:
    article_entities = await article_repo.list_all(limit, offset)
```

---

#### 3. N+1 Query Performance Issues 🐌
**Severity**: Critical - Severe performance degradation
**Files**:
- `src/modules/articles/presentation/routes.py:369-405, 439-469`
- `src/modules/profiles/infrastructure/repositories.py:114-118`

**Problem**:
```python
for article_entity in article_entities:
    author_user = await user_repo.get(article_entity.author_id)  # ❌ N+1!
    ...
    profile = await profile_repo.get_by_user_id(author_user.id)  # ❌ N+1!
```

**Impact**:
- 100 articles = 200 extra database queries
- Severe performance degradation
- API timeouts under load

**Fix Required**:
Implement eager loading in `ArticleRepository`:
```python
async def list_with_authors_and_profiles(
    self,
    filters: ArticleFilters
) -> list[tuple[Article, User, Profile | None]]:
    """List articles with authors and profiles in single query."""
    stmt = (
        select(ArticleModel, UserModel, ProfileModel)
        .join(UserModel, ArticleModel.author_id == UserModel.id)
        .outerjoin(ProfileModel, ProfileModel.user_id == UserModel.id)
        .options(
            selectinload(ArticleModel.tags),
            selectinload(ArticleModel.favorited_by)
        )
    )

    # Apply filters...
    if filters.tag:
        stmt = stmt.join(ArticleModel.tags).where(TagModel.name == filters.tag.lower())
    if filters.author_id:
        stmt = stmt.where(ArticleModel.author_id == filters.author_id)

    stmt = stmt.order_by(ArticleModel.created_at.desc())
    stmt = stmt.limit(filters.limit).offset(filters.offset)

    result = await self._session.execute(stmt)
    return result.all()
```

---

#### 4. Insecure Default Secret Key 🔐
**Severity**: Critical - Security vulnerability
**File**: `src/config.py:36`

**Problem**:
```python
secret_key: str = Field(default="your-secret-key-change-this-in-production...")
# ❌ Weak default, could be left in production
```

**Impact**: JWT tokens can be forged if default key used

**Fix Required**:
```python
from pydantic import field_validator

class Settings(BaseSettings):
    secret_key: str = Field(
        ...,  # No default - required
        min_length=32,
        description="Secret key for JWT signing (min 32 chars)"
    )

    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if v == "your-secret-key-change-this-in-production":
            raise ValueError("Must change default secret key")
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters")
        return v
```

---

#### 5. Docker Healthcheck Fails 🐳
**Severity**: Critical - Containers unhealthy
**File**: `Dockerfile:57`

**Problem**:
```dockerfile
CMD curl -f http://localhost:8000/health || exit 1
# ❌ curl not installed
```

**Impact**: Docker reports container as unhealthy

**Fix Required**:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1
```

---

#### 6. Wrong Parameter Types 💥
**Severity**: Critical - Runtime errors
**Files**: `src/modules/articles/presentation/routes.py:145, 262, 300`

**Problem**:
```python
profile = await profile_repo.get_by_user_id(article_dto.author.name)
# ❌ expects int, gets str
```

**Impact**: TypeError crashes requests

**Fix Required**:
```python
# Need to track author_id properly in DTO
profile = await profile_repo.get_by_user_id(author.id)  # Use author.id, not author.name
```

Also need to add `author_id` field to `ArticleDTO`.

---

### 🟡 HIGH PRIORITY ISSUES (Fix Soon)

#### 7. No Test Coverage for FastAPI Backend
**Impact**: Can't safely refactor, bugs slip through

**Missing**:
- ❌ No integration tests for API endpoints
- ❌ No repository tests with real database
- ❌ No E2E API tests
- ❌ No authentication flow tests
- ❌ No authorization tests

**Fix Required**: Create comprehensive test suite
```
tests/
├── integration/
│   ├── conftest.py          # Shared fixtures
│   ├── test_api_auth.py     # /api/users/* endpoints
│   ├── test_api_articles.py # /api/articles/* endpoints
│   ├── test_api_profiles.py # /api/profiles/* endpoints
│   └── test_api_comments.py # /api/comments/* endpoints
├── unit/ (existing)
└── e2e/
    └── test_user_flows.py   # Complete workflows
```

**Example Test**:
```python
# tests/integration/conftest.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

@pytest.fixture
async def test_db():
    """Create test database."""
    engine = create_async_engine("postgresql+asyncpg://test:test@localhost/test_conduit")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def client(test_db):
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def auth_token(client):
    """Create user and return auth token."""
    response = await client.post("/api/users", json={
        "user": {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        }
    })
    return response.json()["user"]["token"]

# tests/integration/test_api_articles.py
@pytest.mark.asyncio
async def test_create_article(client, auth_token):
    """Test creating an article."""
    response = await client.post(
        "/api/articles",
        json={
            "article": {
                "title": "Test Article",
                "description": "Test Description",
                "body": "Test Body",
                "tagList": ["test"]
            }
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["article"]["title"] == "Test Article"
    assert "test" in data["article"]["tagList"]
```

---

#### 8. Missing Update User Endpoint
**Impact**: Users can't update their profile

**Problem**: Schema exists but no route handler

**Fix Required**:
```python
# src/modules/auth/presentation/routes.py
@router.put("/user", response_model=UserResponseWrapper)
async def update_current_user(
    request: UpdateUserRequest,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Update current user profile."""
    user_repo = UserRepository(session)

    # Get current user entity
    user = await user_repo.get(current_user["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields
    if request.user.email:
        user._email = Email(request.user.email)
    if request.user.username:
        user._name = request.user.username
    if request.user.password:
        user.update_password(Password.from_raw(request.user.password))
    if request.user.bio is not None:
        user._bio = request.user.bio
    if request.user.image is not None:
        user._image = request.user.image

    # Save
    updated_user = await user_repo.update(user)

    # Generate new token
    jwt_service = JWTService()
    token = jwt_service.create_token({"sub": updated_user.email.value})

    return UserResponseWrapper(
        user=UserResponse(
            email=updated_user.email.value,
            token=token,
            username=updated_user.name,
            bio=updated_user.bio,
            image=updated_user.image,
        )
    )
```

---

#### 9. No Authorization Checks
**Impact**: Security vulnerability - users can modify others' data

**Problem**: Missing ownership verification

**Fix Required**: Add authorization checks to all protected operations
```python
# src/core/application/authorization.py
from src.core.domain.exceptions import AuthorizationException

class AuthorizationService:
    """Service for authorization checks."""

    @staticmethod
    def require_ownership(
        resource_owner_id: int,
        current_user_id: int,
        resource_type: str = "resource"
    ) -> None:
        """Verify user owns the resource."""
        if resource_owner_id != current_user_id:
            raise AuthorizationException(
                f"Not authorized to modify this {resource_type}"
            )

# Usage in use case:
class UpdateArticle(IUseCase[UpdateArticleRequest, ArticleDTO]):
    def __init__(
        self,
        article_repository: IArticleRepository,
        auth_service: AuthorizationService,
    ):
        self._article_repository = article_repository
        self._auth_service = auth_service

    async def execute(
        self,
        slug: str,
        current_user_id: int,
        request: UpdateArticleRequest,
    ) -> ArticleDTO:
        article = await self._article_repository.get_by_slug(slug)
        if not article:
            raise EntityNotFoundException("Article", slug)

        # ✅ Authorization check
        self._auth_service.require_ownership(
            article.author_id,
            current_user_id,
            "article"
        )

        # Update article...
```

---

#### 10. Inefficient Count Queries
**Impact**: Performance - loads all records into memory

**Files**:
- `src/modules/auth/infrastructure/repositories.py:136-138`
- `src/modules/profiles/infrastructure/repositories.py:127-129`

**Problem**:
```python
stmt = select(UserModel)
result = await self._session.execute(stmt)
return len(result.scalars().all())  # ❌ Loads everything!
```

**Fix Required**:
```python
from sqlalchemy import func

stmt = select(func.count()).select_from(UserModel)
result = await self._session.execute(stmt)
return result.scalar_one()
```

---

#### 11. Missing Database Indexes
**Impact**: Slow queries as data grows

**Missing Indexes**:
- `articles.author_id` (FK queries)
- `articles.created_at` (ordering)
- `comments.article_id` (FK queries)
- `comments.author_id` (FK queries)
- Compound index on `follows(follower_id, followee_id)`
- Compound index on `article_tags(article_id, tag_name)`

**Fix Required**: Create migration `002_add_indexes.py`
```python
"""Add performance indexes

Revision ID: 002_add_indexes
Revises: 001_initial
"""

def upgrade() -> None:
    # Article indexes
    op.create_index('ix_articles_author_id', 'articles', ['author_id'])
    op.create_index('ix_articles_created_at', 'articles', ['created_at'])

    # Comment indexes
    op.create_index('ix_comments_article_id', 'comments', ['article_id'])
    op.create_index('ix_comments_author_id', 'comments', ['author_id'])

    # Association table compound indexes
    op.create_index(
        'ix_follows_compound',
        'follows',
        ['follower_id', 'followee_id']
    )
    op.create_index(
        'ix_article_tags_compound',
        'article_tags',
        ['article_id', 'tag_name']
    )

def downgrade() -> None:
    op.drop_index('ix_articles_author_id', table_name='articles')
    op.drop_index('ix_articles_created_at', table_name='articles')
    op.drop_index('ix_comments_article_id', table_name='comments')
    op.drop_index('ix_comments_author_id', table_name='comments')
    op.drop_index('ix_follows_compound', table_name='follows')
    op.drop_index('ix_article_tags_compound', table_name='article_tags')
```

---

#### 12. Broad Exception Handling
**Impact**: Hides bugs, makes debugging difficult

**Problem**: Catches all exceptions
```python
except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))  # ❌ Too broad
```

**Fix Required**: Specific exception handlers
```python
from src.core.domain.exceptions import (
    EntityNotFoundException,
    ValidationException,
    AuthorizationException,
)
import logging

logger = logging.getLogger(__name__)

try:
    # Operation...
except EntityNotFoundException as e:
    raise HTTPException(status_code=404, detail=str(e))
except ValidationException as e:
    raise HTTPException(status_code=422, detail=str(e))
except AuthorizationException as e:
    raise HTTPException(status_code=403, detail=str(e))
except IntegrityError as e:
    logger.error(f"Database integrity error: {e}")
    raise HTTPException(status_code=409, detail="Resource conflict")
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

---

### 🟢 MEDIUM PRIORITY (Technical Debt)

#### 13. Code Duplication - Repository Instantiation
**Impact**: Maintenance burden

**Problem**: Repeated in every route handler
```python
article_repo = ArticleRepository(session)
user_repo = UserRepository(session)
profile_repo = ProfileRepository(session)
```

**Fix**: Use FastAPI dependencies
```python
# src/core/presentation/dependencies.py
def get_article_repository(
    session: AsyncSession = Depends(get_db_session)
) -> ArticleRepository:
    return ArticleRepository(session)

# In route:
@router.get("/articles")
async def list_articles(
    article_repo: ArticleRepository = Depends(get_article_repository),
):
    ...
```

---

#### 14. No Caching Utilized
**Impact**: Missing performance optimization

**Problem**: CacheManager initialized but never used

**Fix**: Implement caching layer
```python
# src/services/cache_service.py
from typing import Any
import json
from src.core.infrastructure.cache import cache_manager

class CacheService:
    """Service for caching frequently accessed data."""

    @staticmethod
    async def get_or_set(
        key: str,
        fetch_func: callable,
        ttl: int = 300
    ) -> Any:
        """Get from cache or fetch and cache."""
        cached = await cache_manager.get(key)
        if cached:
            return json.loads(cached)

        data = await fetch_func()
        await cache_manager.set(key, json.dumps(data), ttl)
        return data

# Usage:
async def get_popular_articles() -> list[Article]:
    return await cache_service.get_or_set(
        "popular_articles",
        lambda: article_repo.get_popular(limit=10),
        ttl=600  # 10 minutes
    )
```

---

#### 15-25. Additional Technical Debt Items

See full details in [Backend Technical Debt Backlog](#backend-technical-debt-backlog) section.

---

## Frontend Technical Debt

### 🔴 CRITICAL - Complete Frontend Implementation Required

#### Current State: Only 18% Complete
- ✅ Phase 1: Project Setup
- ✅ Phase 2: Core Architecture
- ❌ Phase 3-11: **All features missing**

### Missing Implementation (Phases 3-11)

#### Phase 3: Authentication Module ❌
**Missing Components**:
```
src/components/auth/
  ├── login-form.ts          # Login form with validation
  ├── register-form.ts       # Registration form
  └── user-settings-form.ts  # Settings form
```

**Required Implementation**:
- Login form with email/password validation
- Registration form with username/email/password
- Settings form for profile updates
- Form error handling and display
- Loading states
- Success/error messages

---

#### Phase 4: Article Components ❌
**Missing Components**:
```
src/components/articles/
  ├── article-list.ts        # List of article previews
  ├── article-preview.ts     # Individual preview card
  ├── article-detail.ts      # Full article view
  ├── article-meta.ts        # Author/date/actions
  └── tag-list.ts            # Tag display/filtering
```

**Required API Clients**:
```typescript
// src/services/api/articles.ts
export const articlesApi = {
  async list(filters?: ArticleFilters): Promise<MultipleArticlesResponse> { },
  async get(slug: string): Promise<ArticleResponse> { },
  async create(article: NewArticle): Promise<ArticleResponse> { },
  async update(slug: string, article: UpdateArticle): Promise<ArticleResponse> { },
  async delete(slug: string): Promise<void> { },
  async favorite(slug: string): Promise<ArticleResponse> { },
  async unfavorite(slug: string): Promise<ArticleResponse> { },
  async getFeed(limit?: number, offset?: number): Promise<MultipleArticlesResponse> { },
};

// src/services/api/tags.ts
export const tagsApi = {
  async list(): Promise<TagsResponse> { },
};
```

---

#### Phase 5: Article Editor ❌
**Missing**:
```
src/components/articles/
  └── article-editor.ts      # Rich text editor
```

**Features Needed**:
- Title input
- Description textarea
- Body textarea (markdown support optional)
- Tag input with add/remove
- Form validation
- Save/publish button
- Draft autosave (optional)

---

#### Phase 6: Profile Module ❌
**Missing Components**:
```
src/components/profiles/
  ├── profile-page.ts        # User profile display
  ├── profile-articles.ts    # User's articles tab
  ├── profile-favorited.ts   # Favorited articles tab
  └── follow-button.ts       # Follow/unfollow button
```

**Missing API Client**:
```typescript
// src/services/api/profiles.ts
export const profilesApi = {
  async get(username: string): Promise<ProfileResponse> { },
  async follow(username: string): Promise<ProfileResponse> { },
  async unfollow(username: string): Promise<ProfileResponse> { },
};
```

---

#### Phase 7: Comments Module ❌
**Missing Components**:
```
src/components/comments/
  ├── comment-list.ts        # List of comments
  ├── comment-item.ts        # Individual comment
  └── comment-form.ts        # Add comment form
```

**Missing API Client**:
```typescript
// src/services/api/comments.ts
export const commentsApi = {
  async list(slug: string): Promise<MultipleCommentsResponse> { },
  async create(slug: string, comment: NewComment): Promise<CommentResponse> { },
  async delete(slug: string, id: number): Promise<void> { },
};
```

**Missing WebSocket**:
```typescript
// src/services/websocket.ts
export class WebSocketService {
  private ws: WebSocket | null = null;

  connect(articleSlug: string): void { }
  disconnect(): void { }
  onCommentAdded(callback: (comment: Comment) => void): void { }
  onCommentDeleted(callback: (commentId: number) => void): void { }
}
```

---

#### Phase 8: Shared Components ❌
**Missing Components**:
```
src/components/common/
  ├── app-header.ts          # Navigation header
  ├── app-footer.ts          # Footer
  ├── loading-spinner.ts     # Loading indicator
  ├── error-message.ts       # Error display
  ├── toast.ts               # Toast notifications
  ├── modal.ts               # Modal dialog
  ├── pagination.ts          # Pagination controls
  └── empty-state.ts         # Empty state display
```

---

#### Phase 9: PWA Features ❌
**Missing Files**:
```
public/
  ├── manifest.json          # App manifest (incomplete)
  ├── icons/                 # PWA icons (missing)
  │   ├── icon-72x72.png
  │   ├── icon-96x96.png
  │   ├── icon-128x128.png
  │   ├── icon-144x144.png
  │   ├── icon-152x152.png
  │   ├── icon-192x192.png
  │   ├── icon-384x384.png
  │   └── icon-512x512.png
  └── offline.html           # Offline fallback page
```

**Service Worker**: Configured in Vite but not tested

---

#### Phase 10: Testing ❌
**Missing Test Files**:
```
tests/
  ├── unit/
  │   ├── services/
  │   │   ├── api-client.test.ts
  │   │   └── auth-service.test.ts
  │   └── utils/
  │       └── validators.test.ts
  └── component/
      ├── auth/
      │   ├── login-form.test.ts
      │   └── register-form.test.ts
      └── articles/
          ├── article-list.test.ts
          └── article-preview.test.ts
```

**Missing Test Infrastructure**:
- No vitest.config.ts
- No test setup files
- No component test utilities
- No mock data factories

---

#### Phase 11: Optimization ❌
**Missing**:
- Bundle size analysis
- Code splitting implementation
- Lazy loading for routes
- Image optimization
- Performance monitoring
- Lighthouse audits

---

## Infrastructure Issues

### 🔴 CRITICAL

#### No Frontend Docker Configuration
**Missing Files**:
- `frontend/Dockerfile`
- Frontend service in `docker-compose.yml`

**Required**:
```dockerfile
# frontend/Dockerfile
FROM oven/bun:1 AS builder
WORKDIR /app
COPY package.json bun.lockb* ./
RUN bun install --frozen-lockfile
COPY . .
RUN bun run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```yaml
# docker-compose.yml - add service
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    environment:
      - VITE_API_BASE_URL=http://app:8000/api
    depends_on:
      - app
```

---

### 🟡 HIGH PRIORITY

#### No CI/CD Pipeline
**Missing**: Automated testing and deployment

**Required**: Create `.github/workflows/ci.yml`
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          pip install uv
          uv sync
      - name: Run tests
        run: uv run pytest tests/ -v
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: oven-sh/setup-bun@v1
      - name: Install dependencies
        run: cd frontend && bun install
      - name: Run tests
        run: cd frontend && bun test
      - name: Build
        run: cd frontend && bun run build
```

---

## Security Concerns

### 🔴 CRITICAL

#### CORS Configuration Too Permissive
**File**: `src/config.py:50-53`

**Problem**:
```python
cors_allow_credentials: bool = True
cors_allow_methods: list[str] = ["*"]  # ❌ Too permissive
cors_allow_headers: list[str] = ["*"]  # ❌ Too permissive
```

**Fix**:
```python
cors_allow_credentials: bool = True
cors_allow_methods: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
cors_allow_headers: list[str] = ["Content-Type", "Authorization", "Accept"]
cors_origins: list[str] = Field(
    default=["http://localhost:3000"],
    env="CORS_ORIGINS"
)
```

---

#### No HTTPS Enforcement
**Missing**: SSL/TLS configuration

**Fix**: Add to nginx/load balancer:
```nginx
# Force HTTPS redirect
server {
    listen 80;
    server_name conduit.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name conduit.example.com;

    ssl_certificate /etc/ssl/certs/conduit.crt;
    ssl_certificate_key /etc/ssl/private/conduit.key;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;

    # Proxy to backend
    location /api {
        proxy_pass http://app:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Serve frontend
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
}
```

---

#### No Rate Limiting
**Missing**: Protection against abuse

**Fix**: Add rate limiting middleware
```python
# src/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# In routes:
@router.post("/users/login")
@limiter.limit("5/minute")
async def login(...):
    pass
```

---

## Remediation Plan

### Timeline: 10 Weeks to Production

### Week 1-2: Critical Backend Fixes
**Goal**: Stable, functional backend

**Tasks**:
- [ ] Create auth dependencies file
- [ ] Fix broken article list endpoint
- [ ] Fix N+1 queries with eager loading
- [ ] Update Docker healthcheck
- [ ] Enforce secure secret key
- [ ] Add database indexes migration
- [ ] Fix profile lookup type errors
- [ ] Set up integration test infrastructure
- [ ] Write tests for critical paths

**Deliverable**: Backend fully functional, tested

---

### Week 3: Backend Quality & Security
**Goal**: Production-ready backend

**Tasks**:
- [ ] Implement authorization checks
- [ ] Add rate limiting
- [ ] Restrict CORS configuration
- [ ] Implement caching for common queries
- [ ] Add comprehensive logging
- [ ] Create update user endpoint
- [ ] Write remaining tests
- [ ] Fix exception handling

**Deliverable**: Secure, performant backend with 80%+ test coverage

---

### Week 4-5: Frontend Authentication & Articles
**Goal**: Core frontend functionality

**Tasks**:
- [ ] Implement login form component
- [ ] Implement register form component
- [ ] Implement settings form component
- [ ] Create article list component
- [ ] Create article preview component
- [ ] Create article detail component
- [ ] Create article meta component
- [ ] Implement articles API client
- [ ] Add tag filtering
- [ ] Implement favorite/unfavorite

**Deliverable**: Users can auth, browse, and favorite articles

---

### Week 6: Article Editor & Profiles
**Goal**: Content creation and social features

**Tasks**:
- [ ] Implement article editor component
- [ ] Add markdown support (optional)
- [ ] Create profile page component
- [ ] Create profile articles tab
- [ ] Create follow button component
- [ ] Implement profiles API client
- [ ] Add article creation
- [ ] Add article editing
- [ ] Add profile viewing
- [ ] Implement follow/unfollow

**Deliverable**: Users can create, edit articles and follow others

---

### Week 7: Comments & Shared Components
**Goal**: Complete feature set

**Tasks**:
- [ ] Implement comment list component
- [ ] Implement comment form component
- [ ] Implement comment item component
- [ ] Create comments API client
- [ ] Implement WebSocket service
- [ ] Create app header component
- [ ] Create app footer component
- [ ] Create loading spinner
- [ ] Create error message component
- [ ] Create toast notifications

**Deliverable**: Full-featured social blogging platform

---

### Week 8: PWA & Polish
**Goal**: Progressive Web App features

**Tasks**:
- [ ] Configure service worker properly
- [ ] Create offline page
- [ ] Generate all PWA icons
- [ ] Test install prompt
- [ ] Test offline functionality
- [ ] Add empty states
- [ ] Polish UI/UX
- [ ] Add loading skeletons
- [ ] Implement dark mode
- [ ] Add accessibility features

**Deliverable**: Installable PWA with offline support

---

### Week 9: Testing & Optimization
**Goal**: Quality and performance

**Tasks**:
- [ ] Write unit tests for services
- [ ] Write component tests
- [ ] Write E2E tests
- [ ] Run Lighthouse audits
- [ ] Optimize bundle size
- [ ] Implement code splitting
- [ ] Add lazy loading
- [ ] Optimize images
- [ ] Fix performance issues
- [ ] Achieve Lighthouse > 90

**Deliverable**: High-quality, performant application

---

### Week 10: Deployment & Documentation
**Goal**: Production deployment

**Tasks**:
- [ ] Create frontend Dockerfile
- [ ] Update docker-compose
- [ ] Set up CI/CD pipeline
- [ ] Configure production environment
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Set up error tracking (Sentry)
- [ ] Implement backup strategy
- [ ] Update all documentation
- [ ] Create deployment guide
- [ ] Deploy to production

**Deliverable**: Deployed, monitored production application

---

## Implementation Checklist

### Backend Critical Fixes
- [ ] Create `src/modules/auth/presentation/dependencies.py`
- [ ] Add `list_all()` method to ArticleRepository
- [ ] Fix N+1 queries with eager loading
- [ ] Update Dockerfile healthcheck
- [ ] Add secret key validation
- [ ] Create indexes migration
- [ ] Fix profile lookup type errors

### Backend Testing
- [ ] Create integration test fixtures
- [ ] Test all API endpoints
- [ ] Test authentication flows
- [ ] Test authorization
- [ ] Test error handling
- [ ] Achieve 80%+ coverage

### Backend Security
- [ ] Add authorization checks
- [ ] Implement rate limiting
- [ ] Restrict CORS
- [ ] Add HTTPS enforcement
- [ ] Implement audit logging

### Frontend Implementation
- [ ] Phase 3: Auth components (3 components)
- [ ] Phase 4: Article components (5 components + API)
- [ ] Phase 5: Editor component
- [ ] Phase 6: Profile components (4 components + API)
- [ ] Phase 7: Comments (3 components + API + WebSocket)
- [ ] Phase 8: Shared components (8 components)
- [ ] Phase 9: PWA (service worker, icons, offline)
- [ ] Phase 10: Testing (unit + component + E2E)
- [ ] Phase 11: Optimization

### Infrastructure
- [ ] Create frontend Dockerfile
- [ ] Update docker-compose.yml
- [ ] Create CI/CD pipeline
- [ ] Set up monitoring
- [ ] Configure production environment
- [ ] Implement backups

### Documentation
- [ ] Update API documentation
- [ ] Create deployment guide
- [ ] Write development guide
- [ ] Document architecture
- [ ] Create troubleshooting guide

---

## Success Criteria

### Backend
- ✅ All critical issues resolved
- ✅ 80%+ test coverage
- ✅ All endpoints functional
- ✅ < 100ms average response time
- ✅ No N+1 queries
- ✅ Zero security vulnerabilities
- ✅ Authorization on all protected routes

### Frontend
- ✅ All 11 phases complete
- ✅ Lighthouse score > 90
- ✅ < 2s first contentful paint
- ✅ Works offline (basic features)
- ✅ Installable as PWA
- ✅ WCAG 2.1 AA compliant
- ✅ < 150KB gzipped bundle

### Infrastructure
- ✅ Automated deployments
- ✅ Monitoring operational
- ✅ Backups automated
- ✅ CI/CD pipeline working
- ✅ Zero downtime deployments

---

## Conclusion

This plan provides a complete roadmap to transform the Conduit application from its current state (backend functional but with debt, frontend incomplete) to a production-ready, high-quality application.

**Total Effort**: 10 weeks
**Priority**: Backend fixes first, then frontend implementation
**Risk**: Manageable with phased approach

**Next Immediate Action**: Start with Week 1 backend critical fixes.

---

**Document Version**: 2.0
**Maintained By**: Development Team
**Review Frequency**: Weekly
**Last Review**: 2025-01-12

**See Also**:
- [Original Frontend Migration Plan](./Frontend-Plan-Original.md)
- [Backend Migration Guide](../MIGRATION_GUIDE.md)
- [Frontend README](../frontend/README.md)
