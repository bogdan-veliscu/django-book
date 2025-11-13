# FastAPI Application - API Endpoints Integration Test Plan

## Overview
This document outlines all API endpoints in the FastAPI application that require integration tests, organized by module. Each endpoint is documented with its HTTP method, URL path, authentication requirements, and key test scenarios.

---

## 1. Health Check Endpoint

### GET /health
- **HTTP Method:** GET
- **Authentication:** None
- **Status Code:** 200 OK
- **Response Model:** `{"status": "healthy"}`
- **Key Test Scenarios:**
  - Verify endpoint returns healthy status
  - Verify response format and structure
  - Test endpoint availability during application startup

---

## 2. Auth Module

**Base Path:** `/api`

### POST /users - Register User
- **HTTP Method:** POST
- **Full URL Path:** `/api/users`
- **Authentication:** None (Public)
- **Status Code:** 201 Created
- **Request Body:** 
  ```json
  {
    "user": {
      "email": "string",
      "name": "string",
      "password": "string"
    }
  }
  ```
- **Response Model:** `AuthResponseWrapper`
  ```json
  {
    "user": {
      "email": "string",
      "token": "string",
      "name": "string",
      "bio": "string",
      "image": "string"
    }
  }
  ```
- **Key Test Scenarios:**
  - Valid registration with all required fields
  - Duplicate email rejection (already exists)
  - Invalid email format
  - Missing required fields
  - Password validation (length, complexity)
  - Token generation and format
  - Response includes user data and JWT token

### POST /users/login - Login User
- **HTTP Method:** POST
- **Full URL Path:** `/api/users/login`
- **Authentication:** None (Public)
- **Status Code:** 200 OK
- **Request Body:**
  ```json
  {
    "user": {
      "email": "string",
      "password": "string"
    }
  }
  ```
- **Response Model:** `AuthResponseWrapper`
- **Key Test Scenarios:**
  - Valid login with correct credentials
  - Invalid email (user not found)
  - Invalid password
  - Missing required fields
  - Token generation and validity
  - User profile data in response
  - Token format matches expected JWT format

### GET /user - Get Current User
- **HTTP Method:** GET
- **Full URL Path:** `/api/user`
- **Authentication:** Required (JWT Token)
- **Status Code:** 200 OK
- **Response Model:** `UserResponseWrapper`
  ```json
  {
    "user": {
      "id": "integer",
      "email": "string",
      "name": "string",
      "bio": "string",
      "image": "string",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  }
  ```
- **Key Test Scenarios:**
  - Retrieve authenticated user's information
  - Invalid token rejection (401 Unauthorized)
  - Missing authorization header (401 Unauthorized)
  - Malformed authorization header format
  - Expired token rejection
  - Verify all user fields returned correctly
  - User not found (404 Not Found)

---

## 3. Profiles Module

**Base Path:** `/api`

### GET /profiles/{name} - Get User Profile
- **HTTP Method:** GET
- **Full URL Path:** `/api/profiles/{name}`
- **Authentication:** Optional (JWT Token)
- **Status Code:** 200 OK
- **Path Parameters:** `name` (string) - Username
- **Response Model:** `ProfileResponseWrapper`
  ```json
  {
    "profile": {
      "name": "string",
      "bio": "string",
      "image": "string",
      "following": "boolean"
    }
  }
  ```
- **Key Test Scenarios:**
  - Get profile without authentication
  - Get profile with authentication
  - User profile not found (404 Not Found)
  - Verify following status when authenticated
  - Verify following is false when not authenticated
  - Verify profile data structure

### POST /profiles/{name}/follow - Follow User
- **HTTP Method:** POST
- **Full URL Path:** `/api/profiles/{name}/follow`
- **Authentication:** Required (JWT Token)
- **Status Code:** 200 OK
- **Path Parameters:** `name` (string) - Username to follow
- **Response Model:** `ProfileResponseWrapper`
- **Key Test Scenarios:**
  - Follow an existing user
  - Follow non-existent user (404 Not Found)
  - Cannot follow yourself (validation error)
  - Already following user (should update following status)
  - Missing authentication (401 Unauthorized)
  - Response includes updated profile with following=true

### DELETE /profiles/{name}/follow - Unfollow User
- **HTTP Method:** DELETE
- **Full URL Path:** `/api/profiles/{name}/follow`
- **Authentication:** Required (JWT Token)
- **Status Code:** 200 OK
- **Path Parameters:** `name` (string) - Username to unfollow
- **Response Model:** `ProfileResponseWrapper`
- **Key Test Scenarios:**
  - Unfollow a user you're currently following
  - Unfollow non-existent user (404 Not Found)
  - Unfollow user you're not following (should update status)
  - Missing authentication (401 Unauthorized)
  - Response includes updated profile with following=false

---

## 4. Articles Module

**Base Path:** `/api`

### POST /articles - Create Article
- **HTTP Method:** POST
- **Full URL Path:** `/api/articles`
- **Authentication:** Required (JWT Token)
- **Status Code:** 201 Created
- **Request Body:**
  ```json
  {
    "article": {
      "title": "string",
      "description": "string",
      "body": "string",
      "tagList": ["string"]
    }
  }
  ```
- **Response Model:** `ArticleResponseSchema`
- **Key Test Scenarios:**
  - Create article with all required fields
  - Create article with tags
  - Create article without tags
  - Missing required fields (title, description, body)
  - Author automatically set to current user
  - Slug generation (must be unique)
  - Author profile data included in response
  - Timestamp fields set correctly
  - Missing authentication (401 Unauthorized)

### GET /articles/{slug} - Get Article by Slug
- **HTTP Method:** GET
- **Full URL Path:** `/api/articles/{slug}`
- **Authentication:** Optional (JWT Token)
- **Status Code:** 200 OK
- **Path Parameters:** `slug` (string) - Article slug
- **Response Model:** `ArticleResponseSchema`
- **Key Test Scenarios:**
  - Get existing article without authentication
  - Get existing article with authentication
  - Get non-existent article (404 Not Found)
  - Verify article data structure
  - Verify author information in response
  - Verify tags in response
  - Verify favorited status when authenticated
  - Verify following status of author when authenticated
  - Timestamps format verification

### PUT /articles/{slug} - Update Article
- **HTTP Method:** PUT
- **Full URL Path:** `/api/articles/{slug}`
- **Authentication:** Required (JWT Token)
- **Status Code:** 200 OK
- **Path Parameters:** `slug` (string) - Article slug
- **Request Body:**
  ```json
  {
    "article": {
      "title": "string",
      "description": "string",
      "body": "string"
    }
  }
  ```
- **Response Model:** `ArticleResponseSchema`
- **Key Test Scenarios:**
  - Update article by author
  - Update non-existent article (404 Not Found)
  - Unauthorized update attempt by non-author (403 Forbidden)
  - Missing authentication (401 Unauthorized)
  - Partial update (some fields only)
  - Slug should not change on update
  - Updated timestamp should reflect change
  - Tags remain unchanged if not specified

### DELETE /articles/{slug} - Delete Article
- **HTTP Method:** DELETE
- **Full URL Path:** `/api/articles/{slug}`
- **Authentication:** Required (JWT Token)
- **Status Code:** 204 No Content
- **Path Parameters:** `slug` (string) - Article slug
- **Key Test Scenarios:**
  - Delete article by author
  - Delete non-existent article (404 Not Found)
  - Unauthorized delete attempt by non-author (403 Forbidden)
  - Missing authentication (401 Unauthorized)
  - Verify article no longer retrievable after deletion
  - Associated comments are handled correctly

### POST /articles/{slug}/favorite - Favorite Article
- **HTTP Method:** POST
- **Full URL Path:** `/api/articles/{slug}/favorite`
- **Authentication:** Required (JWT Token)
- **Status Code:** 200 OK
- **Path Parameters:** `slug` (string) - Article slug
- **Response Model:** `ArticleResponseSchema`
- **Key Test Scenarios:**
  - Favorite an existing article
  - Favorite non-existent article (404 Not Found)
  - Favorite already favorited article (idempotent)
  - Missing authentication (401 Unauthorized)
  - Favorites count increments
  - Response includes favorited=true
  - Cannot favorite own article

### DELETE /articles/{slug}/favorite - Unfavorite Article
- **HTTP Method:** DELETE
- **Full URL Path:** `/api/articles/{slug}/favorite`
- **Authentication:** Required (JWT Token)
- **Status Code:** 200 OK
- **Path Parameters:** `slug` (string) - Article slug
- **Response Model:** `ArticleResponseSchema`
- **Key Test Scenarios:**
  - Unfavorite a favorited article
  - Unfavorite non-existent article (404 Not Found)
  - Unfavorite already unfavorited article (idempotent)
  - Missing authentication (401 Unauthorized)
  - Favorites count decrements
  - Response includes favorited=false

### GET /articles - List Articles with Filters
- **HTTP Method:** GET
- **Full URL Path:** `/api/articles`
- **Authentication:** Optional (JWT Token)
- **Status Code:** 200 OK
- **Query Parameters:**
  - `tag` (string, optional) - Filter by tag
  - `author` (string, optional) - Filter by author username
  - `favorited` (string, optional) - Filter by user who favorited
  - `limit` (integer, default=20, min=1, max=100) - Results per page
  - `offset` (integer, default=0, min=0) - Pagination offset
- **Response Model:** `MultipleArticlesResponseSchema`
  ```json
  {
    "articles": [ArticleSchema],
    "articlesCount": "integer"
  }
  ```
- **Key Test Scenarios:**
  - List all articles with default pagination
  - Filter by tag
  - Filter by author
  - Filter by favorited user
  - Combined filters (ensure correct precedence)
  - Pagination with limit and offset
  - Verify limit bounds (1-100)
  - Verify offset behavior
  - Empty result sets
  - With authentication (favorited status)
  - Without authentication (favorited=false)
  - Articles count matches results

### GET /articles/feed - Get Feed of Followed Authors
- **HTTP Method:** GET
- **Full URL Path:** `/api/articles/feed`
- **Authentication:** Required (JWT Token)
- **Status Code:** 200 OK
- **Query Parameters:**
  - `limit` (integer, default=20, min=1, max=100)
  - `offset` (integer, default=0, min=0)
- **Response Model:** `MultipleArticlesResponseSchema`
- **Key Test Scenarios:**
  - Get feed for user following other users
  - Empty feed when user follows no one
  - Missing authentication (401 Unauthorized)
  - Feed only includes articles from followed users
  - Pagination works correctly in feed
  - Articles marked as favorited if favorited by user
  - Following status always true in feed
  - New articles from followed users appear in feed
  - Unfollow removes articles from feed

---

## 5. Tags Module

**Base Path:** `/api`

### GET /tags - Get All Tags
- **HTTP Method:** GET
- **Full URL Path:** `/api/tags`
- **Authentication:** None (Public)
- **Status Code:** 200 OK
- **Response Model:** `TagsResponseSchema`
  ```json
  {
    "tags": ["string"]
  }
  ```
- **Key Test Scenarios:**
  - Retrieve all tags used in articles
  - Verify tag list format
  - Tags are unique in response
  - Tags are sorted (if applicable)
  - Empty tags list when no articles exist
  - Tags reflect current articles in system

---

## 6. Comments Module

**Base Path:** `/api/articles/{slug}/comments`

### POST /articles/{slug}/comments - Create Comment
- **HTTP Method:** POST
- **Full URL Path:** `/api/articles/{slug}/comments`
- **Authentication:** Required (JWT Token)
- **Status Code:** 201 Created
- **Path Parameters:** `slug` (string) - Article slug
- **Request Body:**
  ```json
  {
    "comment": {
      "body": "string"
    }
  }
  ```
- **Response Model:** `CommentResponseSchema`
  ```json
  {
    "comment": {
      "id": "integer",
      "body": "string",
      "createdAt": "datetime",
      "updatedAt": "datetime",
      "author": {
        "username": "string",
        "bio": "string",
        "image": "string",
        "following": "boolean"
      }
    }
  }
  ```
- **Key Test Scenarios:**
  - Create comment on existing article
  - Create comment on non-existent article (404 Not Found)
  - Comment body is required
  - Empty comment body rejection
  - Author automatically set to current user
  - Missing authentication (401 Unauthorized)
  - Comment ID auto-generated
  - Timestamps set correctly
  - Author information included in response

### GET /articles/{slug}/comments - List Comments
- **HTTP Method:** GET
- **Full URL Path:** `/api/articles/{slug}/comments`
- **Authentication:** Optional (JWT Token)
- **Status Code:** 200 OK
- **Path Parameters:** `slug` (string) - Article slug
- **Response Model:** `MultipleCommentsResponseSchema`
  ```json
  {
    "comments": [CommentSchema]
  }
  ```
- **Key Test Scenarios:**
  - List comments for existing article
  - List comments for article with no comments
  - List comments for non-existent article (404 Not Found)
  - Comments ordered by creation time
  - Author information for each comment
  - Without authentication (following=false)
  - With authentication (following status verified)
  - Comment count in response

### DELETE /articles/{slug}/comments/{comment_id} - Delete Comment
- **HTTP Method:** DELETE
- **Full URL Path:** `/api/articles/{slug}/comments/{comment_id}`
- **Authentication:** Required (JWT Token)
- **Status Code:** 204 No Content
- **Path Parameters:**
  - `slug` (string) - Article slug
  - `comment_id` (integer) - Comment ID
- **Key Test Scenarios:**
  - Delete comment by author
  - Delete comment on non-existent article (404 Not Found)
  - Delete non-existent comment (404 Not Found)
  - Unauthorized delete by non-author (403 Forbidden)
  - Missing authentication (401 Unauthorized)
  - Verify comment no longer retrievable after deletion
  - Comment count decrements on deletion

---

## Error Response Handling

All endpoints should be tested for proper error handling:

### Exception Handler Mappings:
- **EntityNotFoundException** → 404 Not Found
  ```json
  {"errors": {"body": ["Entity not found"]}}
  ```

- **EntityAlreadyExistsException** → 422 Unprocessable Entity
  ```json
  {"errors": {"body": ["Entity already exists"]}}
  ```

- **ValidationException** → 422 Unprocessable Entity
  ```json
  {"errors": {"{field}": ["Validation error message"]}}
  ```

- **AuthorizationException** → 403 Forbidden
  ```json
  {"errors": {"body": ["Not authorized"]}}
  ```

- **DomainException** → 400 Bad Request
  ```json
  {"errors": {"body": ["Domain error message"]}}
  ```

### HTTP Status Codes to Test:
- 200 OK - Successful GET, POST (non-creation), DELETE (with response)
- 201 Created - Successful POST that creates a resource
- 204 No Content - Successful DELETE (no response body)
- 400 Bad Request - Domain-level business logic errors
- 401 Unauthorized - Missing or invalid authentication
- 403 Forbidden - User lacks permission to perform action
- 404 Not Found - Resource not found
- 422 Unprocessable Entity - Validation or duplicate entity errors

---

## Authentication Header Format

All protected endpoints require the authorization header in the following format:

```
Authorization: Token <jwt_token>
```

- **Token Format:** `Token {JWT_STRING}`
- **JWT Claims:** Must include user_id
- **Token Validation:** JWTService validates token signature and expiry
- **Error Code:** 401 Unauthorized if invalid/expired

---

## Summary Statistics

- **Total Endpoints:** 19
- **Public Endpoints:** 4 (Health, Register, Login, Get Tags)
- **Protected Endpoints:** 11 (require auth)
- **Optional Auth Endpoints:** 4 (behavior differs with/without auth)
- **Modules:** 5 (Auth, Profiles, Articles, Comments, Tags)

### Endpoint Breakdown by Method:
- **GET:** 8 endpoints
- **POST:** 6 endpoints
- **PUT:** 1 endpoint
- **DELETE:** 4 endpoints

---

## Testing Recommendations

1. **Setup/Teardown:** Create test fixtures for:
   - Test database with sample data
   - Multiple test users
   - Multiple test articles with tags
   - Follow relationships
   - Favorite relationships
   - Comments

2. **Authentication Tests:**
   - Test token generation consistency
   - Test token expiry
   - Test invalid token formats
   - Test missing headers

3. **Authorization Tests:**
   - Test owner operations (update/delete own resources)
   - Test non-owner operations (cannot modify others' content)
   - Test read permissions

4. **Data Validation Tests:**
   - Boundary conditions (max/min lengths)
   - Required fields
   - Invalid formats
   - Slug generation uniqueness

5. **Edge Cases:**
   - Concurrent operations
   - Bulk operations with pagination
   - Cascade operations (delete article → delete comments)
   - Race conditions on favorites/follows

6. **Performance Tests:**
   - N+1 query prevention
   - Pagination performance
   - Large dataset filtering

