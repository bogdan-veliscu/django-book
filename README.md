# RealWorld Conduit - FastAPI + Lit

A modern, production-ready implementation of the [RealWorld](https://github.com/gothinkster/realworld) Conduit application, migrated from Django to **FastAPI** (backend) and **Lit** web components (frontend).

[![CI/CD Pipeline](https://github.com/yourusername/django-book/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/yourusername/django-book/actions)

## 🚀 Features

- **Modern Tech Stack**: FastAPI + Lit + PostgreSQL + Redis
- **DDD Architecture**: Clean, maintainable domain-driven design
- **Comprehensive Testing**: 206 tests (82 unit + 124 integration)
- **PWA Support**: Progressive Web App with service worker
- **Production Ready**: Docker Compose setup with health checks
- **Type Safe**: Full TypeScript and Python type hints
- **Fast**: Optimized builds (~129 KB gzipped frontend)

## 📋 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.13+ (for local development)
- Node.js 20+ (for frontend development)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/django-book.git
   cd django-book
   ```

2. **Start development environment**
   ```bash
   docker-compose up -d
   ```

3. **Run migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Production Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for comprehensive deployment guide.

```bash
# 1. Configure environment
cp .env.example .env
nano .env  # Set production values

# 2. Build and start services
docker-compose -f docker-compose.prod.yml up -d

# 3. Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 4. Access application
# Frontend: http://localhost
# Backend API: http://localhost/api
```

## 🏗️ Architecture

### Backend (FastAPI)

```
src/
├── core/                   # Shared infrastructure
│   ├── domain/            # Base entities, value objects
│   ├── application/       # Base DTOs, use cases
│   ├── infrastructure/    # Database, cache, repository
│   └── presentation/      # FastAPI dependencies
└── modules/               # Bounded contexts (DDD)
    ├── auth/              # Authentication & users
    ├── profiles/          # User profiles & following
    ├── articles/          # Articles & tags
    └── comments/          # Article comments
```

**Tech Stack:**
- **Framework**: FastAPI 0.115+
- **ORM**: SQLAlchemy 2.0 (async)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Testing**: pytest + pytest-asyncio
- **Validation**: Pydantic V2
- **Migrations**: Alembic

### Frontend (Lit)

```
frontend/src/
├── components/            # Lit web components
│   ├── articles/         # Article components
│   ├── auth/             # Authentication forms
│   ├── comments/         # Comment components
│   ├── profiles/         # Profile components
│   └── common/           # Shared components
├── services/             # API clients & business logic
├── views/                # Page-level components
├── types/                # TypeScript types
└── styles/               # Global styles
```

**Tech Stack:**
- **Framework**: Lit 3.x
- **Build Tool**: Vite 5.x
- **Language**: TypeScript
- **Router**: @vaadin/router
- **PWA**: Workbox
- **Styling**: Shadow DOM CSS

## 🧪 Testing

### Backend Tests

```bash
# Unit tests only
uv run pytest tests/unit -v

# Integration tests (requires DB)
docker-compose up -d db redis
uv run pytest tests/integration -v

# All tests with coverage
uv run pytest tests/ -v --cov=src --cov-report=html
```

**Coverage**: 206 tests, 80%+ code coverage

### Frontend Tests

```bash
cd frontend

# Type checking
npm run type-check

# Linting
npm run lint

# Build (production)
npm run build
```

## 📦 Key Features Implemented

### User Management
- ✅ User registration and login (JWT authentication)
- ✅ User profiles with bio and avatar
- ✅ Follow/unfollow users
- ✅ Update user settings

### Article Features
- ✅ Create, read, update, delete articles
- ✅ Markdown support for article body
- ✅ Tag-based filtering
- ✅ Favorite/unfavorite articles
- ✅ Global feed and personal feed
- ✅ Pagination

### Social Features
- ✅ Comment on articles
- ✅ Delete own comments
- ✅ View user profiles
- ✅ See user's articles and favorites
- ✅ Follow other users

### UI/UX
- ✅ Responsive design
- ✅ Loading states
- ✅ Error handling
- ✅ Form validation
- ✅ Route protection
- ✅ PWA with service worker

## 🛠️ Development

### Backend Development

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn src.main:app --reload

# Run linter
uv run ruff check .

# Run type checker
uv run mypy src

# Create migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📊 Performance

### Frontend Bundle Sizes
- **Total**: ~129 KB (precached)
- **Main bundle**: 15.08 KB (gzipped: 4.55 KB)
- **Lit core**: 15.46 KB (gzipped: 5.89 KB)
- **Router**: 23.02 KB (gzipped: 8.38 KB)

### Backend Performance
- **Response time**: < 50ms average (cached)
- **Database queries**: Optimized with eager loading (no N+1)

## 🔒 Security

- ✅ JWT token authentication
- ✅ Password hashing with bcrypt
- ✅ CORS configuration
- ✅ SQL injection prevention (ORM)
- ✅ XSS protection (CSP headers)
- ✅ Secure secret key validation (32+ chars)
- ✅ Environment-based configuration
- ✅ Input validation (Pydantic)

## 📚 Documentation

- [DEPLOYMENT.md](./DEPLOYMENT.md) - Production deployment guide
- [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) - Django to FastAPI migration notes
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (Swagger UI)
- [Frontend README](./frontend/README.md) - Frontend-specific documentation
- [Test Documentation](./tests/integration/README.md) - Testing guide
- [Technical Debt Plan](./docs/Plan.md) - Development roadmap and technical debt

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Quality

- Run tests before committing
- Follow existing code patterns
- Add tests for new features
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [RealWorld](https://github.com/gothinkster/realworld) - Specification and requirements
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Lit](https://lit.dev/) - Simple, fast web components
- [Thinkster](https://thinkster.io/) - Original RealWorld Conduit design

---

**Built with ❤️ using FastAPI and Lit**
