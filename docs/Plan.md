# FastAPI + Lit PWA Migration Plan

**Document Version**: 3.0
**Last Updated**: 2025-11-15
**Status**: ✅ ALL ISSUES RESOLVED — Production Ready

---

## Current State

- **Backend**: 5 phases complete, 206+ tests (82 unit + 124+ integration), all bugs fixed
- **Frontend**: Full Lit PWA implementation complete (Phases 3–8), 18 components
- **Infrastructure**: Docker Compose, Nginx, GitHub Actions CI/CD

---

## Resolved Issues

### Backend Bugs (Fixed)

| # | Location | Bug | Fix |
|---|----------|-----|-----|
| 1 | `articles/routes.py:145` | `profile_repo.get_by_user_id(author.name)` passed string instead of int | Use `user_repo.get_by_name()` then `profile_repo.is_following()` |
| 2 | `articles/routes.py:262` | Same bug in `favorite_article` | Same fix |
| 3 | `articles/routes.py:300` | Same bug in `unfavorite_article` | Same fix |
| 4 | `comments/routes.py:148` | `profile_repo.get_by_user_id(comment_dto.id)` passed comment ID | Use `user_repo.get_by_name()` then `profile_repo.is_following()` |
| 5 | `articles/routes.py` feed | N+1 queries in `get_feed` (individual author fetch per article) | Batch-fetch all authors with `UserModel.id.in_(author_ids)` |

### Missing Endpoint (Added)

| # | Endpoint | Status |
|---|----------|--------|
| 6 | `PUT /api/user` | ✅ Added — update email, name, password, bio, image |

Files added/modified:
- `src/modules/auth/domain/entities.py` — Added `update_email()` method
- `src/modules/auth/application/dtos.py` — Added `email` field to `UpdateUserRequest`
- `src/modules/auth/application/commands/update_user.py` — New use case
- `src/modules/auth/presentation/routes.py` — Added `PUT /user` route
- `tests/integration/test_auth_api.py` — Added 9 integration tests for update endpoint

### Frontend Config (Fixed)

| # | File | Bug | Fix |
|---|------|-----|-----|
| 7 | `frontend/vite.config.ts` | Workbox cached `api.realworld.io` (external URL) | Changed to `/\/api\//i` to match actual backend path |

---

## All API Endpoints (19 total — all implemented)

| Method | Path | Auth | Status |
|--------|------|------|--------|
| POST | `/api/users` | No | ✅ |
| POST | `/api/users/login` | No | ✅ |
| GET | `/api/user` | Yes | ✅ |
| PUT | `/api/user` | Yes | ✅ |
| GET | `/api/profiles/:username` | Optional | ✅ |
| POST | `/api/profiles/:username/follow` | Yes | ✅ |
| DELETE | `/api/profiles/:username/follow` | Yes | ✅ |
| GET | `/api/articles` | Optional | ✅ |
| GET | `/api/articles/feed` | Yes | ✅ |
| POST | `/api/articles` | Yes | ✅ |
| GET | `/api/articles/:slug` | Optional | ✅ |
| PUT | `/api/articles/:slug` | Yes | ✅ |
| DELETE | `/api/articles/:slug` | Yes | ✅ |
| POST | `/api/articles/:slug/favorite` | Yes | ✅ |
| DELETE | `/api/articles/:slug/favorite` | Yes | ✅ |
| GET | `/api/articles/:slug/comments` | Optional | ✅ |
| POST | `/api/articles/:slug/comments` | Yes | ✅ |
| DELETE | `/api/articles/:slug/comments/:id` | Yes | ✅ |
| GET | `/api/tags` | No | ✅ |

---

## Optional Future Improvements

These are enhancements for future iterations (not blocking production):

1. **Frontend tests** — Vitest unit tests and Playwright E2E tests
2. **PWA icon generation** — Run `generate-icons.sh` before deployment
3. **Redis caching** — Cache article feeds and tag lists
4. **Rate limiting** — API rate limiting for production abuse prevention
5. **Monitoring** — Prometheus metrics + Grafana dashboards
6. **WebSocket** — Real-time comment updates (infrastructure proxied, not yet wired)
7. **Increase test coverage** — From 43% to 80%+
