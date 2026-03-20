# FastAPI Application - API Endpoints By Module

## Module Architecture Overview

```
FastAPI Application (src/main.py)
├── /health (standalone)
├── /api (prefix) - Routes registered from modules
│   ├── Auth Module (/api/users, /api/user)
│   ├── Profiles Module (/api/profiles)
│   ├── Articles Module (/api/articles)
│   ├── Tags Module (/api/tags)
│   └── Comments Module (/api/articles/{slug}/comments)
```

---

## Module 1: Auth Module

**Location:** `src/modules/auth/presentation/routes.py`  
**Base Path:** `/api`  
**Tag:** `auth`

### Endpoints

#### 1.1 POST /users - Register User
```
POST /api/users
Status: 201 Created
Auth: None (Public)
```

**Purpose:** Register a new user account

**Request Schema:**
```python
RegisterRequestWrapper(user: RegisterRequest)
# user.email: str
# user.name: str
# user.password: str
```

**Response Schema:**
```python
AuthResponseWrapper(user: AuthResponse)
# user.email: str
# user.token: str (JWT)
# user.name: str
# user.bio: str | None
# user.image: str | None
```

**Use Case:** `RegisterUser`
- Dependency: `IUserRepository`, `JWTService`
- Validates email uniqueness
- Hashes password
- Generates JWT token

**Test Scenarios:**
- Valid registration with all fields
- Duplicate email (422)
- Invalid email format
- Missing fields
- Password validation
- Token format and validity
- Response structure

---

#### 1.2 POST /users/login - Login User
```
POST /api/users/login
Status: 200 OK
Auth: None (Public)
```

**Purpose:** Authenticate user and receive JWT token

**Request Schema:**
```python
LoginRequestWrapper(user: LoginRequest)
# user.email: str
# user.password: str
```

**Response Schema:**
```python
AuthResponseWrapper(user: AuthResponse)
# Same as register response
```

**Use Case:** `LoginUser`
- Dependency: `IUserRepository`, `JWTService`
- Validates credentials
- Generates JWT token

**Test Scenarios:**
- Valid login
- User not found (400/404)
- Wrong password (400)
- Missing fields
- Token validity
- Token usable for subsequent requests

---

#### 1.3 GET /user - Get Current User
```
GET /api/user
Status: 200 OK
Auth: Required (JWT Token)
Header: Authorization: Token {jwt}
```

**Purpose:** Retrieve current authenticated user's profile

**Response Schema:**
```python
UserResponseWrapper(user: UserResponse)
# user.id: int
# user.email: str
# user.name: str
# user.bio: str | None
# user.image: str | None
# user.created_at: datetime
# user.updated_at: datetime
```

**Dependency:** `get_current_user_id`, `IUserRepository`

**Test Scenarios:**
- Retrieve authenticated user
- Invalid token (401)
- Missing header (401)
- Malformed header (401)
- Expired token (401)
- User not found after auth (404)
- Response completeness

---

## Module 2: Profiles Module

**Location:** `src/modules/profiles/presentation/routes.py`  
**Base Path:** `/api`  
**Tag:** `profiles`

### Endpoints

#### 2.1 GET /profiles/{name} - Get User Profile
```
GET /api/profiles/{name}
Status: 200 OK
Auth: Optional
Path Param: name (string) - username
```

**Purpose:** Retrieve a user's public profile

**Response Schema:**
```python
ProfileResponseWrapper(profile: ProfileResponse)
# profile.name: str
# profile.bio: str | None
# profile.image: str | None
# profile.following: bool
```

**Behavior:**
- `following=false` if not authenticated
- `following=true/false` based on current user's follow status if authenticated

**Use Case:** `GetProfile`
- Dependency: `ProfileRepository`
- Request: `GetProfileRequest(name: str, current_user_id: int | None)`

**Test Scenarios:**
- Get profile without auth (following=false)
- Get profile with auth (following varies)
- User not found (404)
- Profile data completeness
- Following status accuracy

---

#### 2.2 POST /profiles/{name}/follow - Follow User
```
POST /api/profiles/{name}/follow
Status: 200 OK
Auth: Required
Path Param: name (string) - username to follow
```

**Purpose:** Follow another user

**Response Schema:**
```python
ProfileResponseWrapper(profile: ProfileResponse)
# profile.following: true
```

**Use Case:** `FollowUser`
- Dependency: `ProfileRepository`
- Request: `FollowUserRequest(follower_id: int, followee_name: str)`
- Cannot follow yourself
- Idempotent - following again has no additional effect

**Test Scenarios:**
- Follow existing user
- Follow non-existent user (404)
- Cannot follow self (validation error)
- Already following (idempotent)
- Missing auth (401)
- Response shows following=true

---

#### 2.3 DELETE /profiles/{name}/follow - Unfollow User
```
DELETE /api/profiles/{name}/follow
Status: 200 OK
Auth: Required
Path Param: name (string) - username to unfollow
```

**Purpose:** Unfollow a user

**Response Schema:**
```python
ProfileResponseWrapper(profile: ProfileResponse)
# profile.following: false
```

**Use Case:** `UnfollowUser`
- Dependency: `ProfileRepository`
- Request: `UnfollowUserRequest(follower_id: int, followee_name: str)`
- Idempotent - unfollowing when not following has no effect

**Test Scenarios:**
- Unfollow currently followed user
- Unfollow non-existent user (404)
- Unfollow when not following (idempotent)
- Missing auth (401)
- Response shows following=false

---

## Module 3: Articles Module

**Location:** `src/modules/articles/presentation/routes.py`  
**Base Path:** `/api`  
**Tags:** `articles`, `tags`

### Article Endpoints

#### 3.1 POST /articles - Create Article
```
POST /api/articles
Status: 201 Created
Auth: Required
```

**Purpose:** Create a new article

**Request Schema:**
```python
CreateArticleSchema(article: CreateArticleRequest)
# article.title: str
# article.description: str
# article.body: str
# article.tagList: list[str]
```

**Response Schema:**
```python
ArticleResponseSchema(article: ArticleSchema)
# article.slug: str (generated, unique)
# article.title: str
# article.description: str
# article.body: str
# article.tagList: list[str]
# article.createdAt: datetime
# article.updatedAt: datetime
# article.favorited: bool (false for own articles)
# article.favoritesCount: int (0)
# article.author: ProfileSchema
#   - username: str
#   - bio: str | None
#   - image: str | None
#   - following: bool (false for own articles)
```

**Use Case:** `CreateArticle`
- Dependency: `ArticleRepository`, `UserRepository`, `ProfileRepository`
- Author automatically set to current user
- Slug generated from title (must be unique)
- Tags associated with article

**Test Scenarios:**
- Create with all fields
- Create with tags
- Create without tags
- Missing required fields
- Slug generation and uniqueness
- Author set correctly
- Timestamps set correctly
- Missing auth (401)

---

#### 3.2 GET /articles/{slug} - Get Article by Slug
```
GET /api/articles/{slug}
Status: 200 OK
Auth: Optional
Path Param: slug (string)
```

**Purpose:** Retrieve a specific article

**Response Schema:**
```python
ArticleResponseSchema(article: ArticleSchema)
```

**Behavior:**
- `favorited=false` if not authenticated
- `favorited=true/false` based on user's favorites if authenticated
- `author.following=false` if not authenticated
- `author.following=true/false` based on follow status if authenticated

**Use Case:** `GetArticle`
- Dependency: `ArticleRepository`, `UserRepository`, `ProfileRepository`

**Test Scenarios:**
- Get existing article
- Get non-existent article (404)
- Without auth (favorited=false)
- With auth (favorited and following status vary)
- Article data completeness

---

#### 3.3 PUT /articles/{slug} - Update Article
```
PUT /api/articles/{slug}
Status: 200 OK
Auth: Required
Path Param: slug (string)
```

**Purpose:** Update an existing article

**Request Schema:**
```python
UpdateArticleSchema(article: UpdateArticleRequest)
# article.title: str (optional)
# article.description: str (optional)
# article.body: str (optional)
```

**Response Schema:**
```python
ArticleResponseSchema(article: ArticleSchema)
```

**Use Case:** `UpdateArticle`
- Only author can update
- Slug remains unchanged
- Tags cannot be updated via this endpoint
- Updated timestamp reflects change

**Authorization:** Only article author can update (403 if not author)

**Test Scenarios:**
- Update by author
- Update non-existent article (404)
- Update by non-author (403)
- Partial updates
- Slug immutability
- Timestamp update
- Missing auth (401)

---

#### 3.4 DELETE /articles/{slug} - Delete Article
```
DELETE /api/articles/{slug}
Status: 204 No Content
Auth: Required
Path Param: slug (string)
```

**Purpose:** Delete an article

**Use Case:** `DeleteArticle`
- Only author can delete
- Associated comments should be deleted (cascade)

**Authorization:** Only article author can delete (403 if not author)

**Test Scenarios:**
- Delete by author
- Delete non-existent article (404)
- Delete by non-author (403)
- Article no longer retrievable after delete
- Comments deleted with article
- Missing auth (401)

---

#### 3.5 POST /articles/{slug}/favorite - Favorite Article
```
POST /api/articles/{slug}/favorite
Status: 200 OK
Auth: Required
Path Param: slug (string)
```

**Purpose:** Mark an article as favorite

**Response Schema:**
```python
ArticleResponseSchema(article: ArticleSchema)
# article.favorited: true
# article.favoritesCount: incremented
```

**Use Case:** `FavoriteArticle`
- Idempotent - favoriting twice has no additional effect
- Cannot favorite own article (business logic check)

**Test Scenarios:**
- Favorite existing article
- Favorite non-existent article (404)
- Favorite already favorited article (idempotent)
- Favorites count increments
- Response shows favorited=true
- Missing auth (401)

---

#### 3.6 DELETE /articles/{slug}/favorite - Unfavorite Article
```
DELETE /api/articles/{slug}/favorite
Status: 200 OK
Auth: Required
Path Param: slug (string)
```

**Purpose:** Remove article from favorites

**Response Schema:**
```python
ArticleResponseSchema(article: ArticleSchema)
# article.favorited: false
# article.favoritesCount: decremented
```

**Use Case:** `UnfavoriteArticle`
- Idempotent - unfavoriting when not favorited has no effect

**Test Scenarios:**
- Unfavorite favorited article
- Unfavorite non-existent article (404)
- Unfavorite when not favorited (idempotent)
- Favorites count decrements
- Response shows favorited=false
- Missing auth (401)

---

#### 3.7 GET /articles - List Articles with Filters
```
GET /api/articles
Status: 200 OK
Auth: Optional
Query Params:
  - tag: string (optional)
  - author: string (optional)
  - favorited: string (optional)
  - limit: int (1-100, default 20)
  - offset: int (default 0)
```

**Purpose:** Retrieve articles with filtering and pagination

**Response Schema:**
```python
MultipleArticlesResponseSchema
# articles: list[ArticleSchema]
# articlesCount: int
```

**Filter Logic:**
- Multiple filters handled with OR/AND logic (if multiple specified, may have precedence)
- `tag` filters articles by tag name
- `author` filters articles by author username
- `favorited` filters articles favorited by specified username

**Pagination:**
- Default limit: 20 articles
- Limit range: 1-100
- Offset: number of articles to skip

**Use Case:** Batch article retrieval from `ArticleRepository`

**Test Scenarios:**
- List all articles (default pagination)
- Filter by tag
- Filter by author
- Filter by favorited
- Combined filters
- Pagination with various limits and offsets
- Limit validation (1-100)
- Empty results
- Without auth (all favorited=false)
- With auth (favorited status varies)
- Article count accuracy

---

#### 3.8 GET /articles/feed - Get User Feed
```
GET /api/articles/feed
Status: 200 OK
Auth: Required
Query Params:
  - limit: int (1-100, default 20)
  - offset: int (default 0)
```

**Purpose:** Get articles from authors the user follows

**Response Schema:**
```python
MultipleArticlesResponseSchema
# articles: list[ArticleSchema]
# articlesCount: int
```

**Behavior:**
- Only includes articles from followed users
- `following=true` for all articles in feed
- `favorited` status reflects current user's favorites
- Uses same pagination as list_articles

**Use Case:** `ArticleRepository.get_feed(user_id, limit, offset)`

**Test Scenarios:**
- Get feed for user following others
- Empty feed when user follows no one
- New articles from followed users appear
- Unfollow removes articles from feed
- Pagination works correctly
- Articles marked favorited if applicable
- Missing auth (401)

---

### Tag Endpoints

#### 3.9 GET /tags - Get All Tags
```
GET /api/tags
Status: 200 OK
Auth: None (Public)
```

**Purpose:** Retrieve all tags used in articles

**Response Schema:**
```python
TagsResponseSchema(tags: list[str])
```

**Behavior:**
- Returns unique tag names
- Likely sorted alphabetically
- Empty list if no articles/tags exist

**Test Scenarios:**
- Retrieve all tags
- Tag uniqueness
- Tag sorting
- Empty tags list
- Tags reflect current system state

---

## Module 4: Comments Module

**Location:** `src/modules/comments/presentation/routes.py`  
**Base Path:** `/api/articles/{slug}/comments`  
**Tag:** `comments`

### Endpoints

#### 4.1 POST /articles/{slug}/comments - Create Comment
```
POST /api/articles/{slug}/comments
Status: 201 Created
Auth: Required
Path Param: slug (string) - article slug
```

**Purpose:** Add a comment to an article

**Request Schema:**
```python
CreateCommentSchema(comment: CreateCommentRequest)
# comment.body: str
```

**Response Schema:**
```python
CommentResponseSchema(comment: CommentSchema)
# comment.id: int
# comment.body: str
# comment.createdAt: datetime
# comment.updatedAt: datetime
# comment.author: ProfileSchema
#   - username: str
#   - bio: str | None
#   - image: str | None
#   - following: bool (false for own comments)
```

**Use Case:** `CreateComment`
- Dependency: `CommentRepository`, `UserRepository`, `ArticleRepository`
- Article must exist (404 if not)
- Author automatically set to current user
- ID auto-generated

**Test Scenarios:**
- Create comment on existing article
- Create on non-existent article (404)
- Empty body rejection
- Author set correctly
- Timestamps set correctly
- ID generation
- Missing auth (401)

---

#### 4.2 GET /articles/{slug}/comments - List Comments
```
GET /api/articles/{slug}/comments
Status: 200 OK
Auth: Optional
Path Param: slug (string) - article slug
```

**Purpose:** Retrieve all comments for an article

**Response Schema:**
```python
MultipleCommentsResponseSchema(comments: list[CommentSchema])
```

**Behavior:**
- Comments ordered by creation time (likely ascending)
- `author.following=false` if not authenticated
- `author.following=true/false` based on follow status if authenticated
- Returns empty list if article has no comments

**Use Case:** `ListComments`
- Dependency: `CommentRepository`, `UserRepository`, `ProfileRepository`

**Test Scenarios:**
- List comments for article with comments
- List for article with no comments (empty list)
- List for non-existent article (404)
- Comment ordering
- Author information included
- Without auth (following=false)
- With auth (following status varies)

---

#### 4.3 DELETE /articles/{slug}/comments/{comment_id} - Delete Comment
```
DELETE /api/articles/{slug}/comments/{comment_id}
Status: 204 No Content
Auth: Required
Path Params:
  - slug: string - article slug
  - comment_id: int - comment ID
```

**Purpose:** Delete a comment

**Use Case:** `DeleteComment`
- Only comment author can delete
- Article must exist (404 if not)
- Comment must exist (404 if not)

**Authorization:** Only comment author can delete (403 if not author)

**Test Scenarios:**
- Delete by comment author
- Delete on non-existent article (404)
- Delete non-existent comment (404)
- Delete by non-author (403)
- Comment no longer retrievable after delete
- Missing auth (401)

---

## Inter-Module Dependencies

### Module Relationships

```
Auth Module
    └── Provides: User identification, JWT tokens
        Used by: All other modules

Profiles Module
    ├── Depends on: User data (Auth)
    ├── Provides: Follow relationships
    └── Used by: Articles, Comments (for author following status)

Articles Module
    ├── Depends on: User data (Auth), Follow data (Profiles)
    ├── Provides: Article CRUD, Favorites
    └── Used by: Feed queries, Comments

Comments Module
    ├── Depends on: User data (Auth), Article existence (Articles)
    ├── Provides: Comments on articles
    └── Reads: Follow status (Profiles)

Tags Module
    ├── Depends on: Article data (Articles)
    └── Provides: Tag listings
```

### Data Flow Examples

**Creating an Article:**
1. User authenticates (Auth module) → receives JWT
2. User creates article (Articles module) → author_id from JWT
3. Author info loaded (Auth module) → profile with bio, image
4. Follow status loaded (Profiles module) → following status

**Getting Article with Feed:**
1. User authenticates (Auth module) → receives JWT
2. Get current user (Auth module) → user ID from JWT
3. Get user's following list (Profiles module) → list of followed user IDs
4. Get articles from followed users (Articles module) → articles by those users
5. Check favorites (Articles module) → favorite status for current user

**Listing Comments:**
1. Get article by slug (Articles module) → verify exists
2. Get comments for article (Comments module) → comment list
3. For each comment author, check if current user follows (Profiles module)

---

## Error Handling by Module

### Common Error Patterns

**Authentication Errors (401):**
- Missing Authorization header
- Invalid token format ("Token {jwt}" expected)
- Expired token
- Invalid token signature

**Authorization Errors (403):**
- Non-owner updating/deleting resource
- Non-author deleting comment
- Business logic restrictions (e.g., cannot follow self)

**Validation Errors (422):**
- Missing required fields
- Duplicate email on registration
- Invalid field formats

**Not Found Errors (404):**
- Article doesn't exist
- User/profile doesn't exist
- Comment doesn't exist
- Article slug not found

**Business Logic Errors (400):**
- Invalid operations (e.g., cannot favorite own article)
- Integrity violations

---

## Authentication Flow Diagram

```
User Registration/Login
    ↓
[Auth Module] → Generate JWT Token
    ↓
User makes authenticated request with JWT
    ↓
[Auth Module] → Validate JWT
    ↓
Extract user_id from token
    ↓
Load user data from database
    ↓
Pass user context to endpoint handler
    ↓
Handler accesses current_user["id"], current_user["email"], etc.
```

---

## Test Execution Order Recommendation

1. **Health Check** (sanity test)
2. **Auth Module** (setup authentication)
3. **Profiles Module** (basic profile operations)
4. **Articles Module** (complex operations with auth)
5. **Comments Module** (depends on articles)
6. **Tags Module** (simple read operation)
7. **Integration Tests** (cross-module interactions)

