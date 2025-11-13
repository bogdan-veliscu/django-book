# Frontend Migration Plan: Django/HTMX → Lit PWA

## Executive Summary

This document outlines the comprehensive plan to migrate the RealWorld Conduit frontend from a Django server-side rendered application with HTMX to a modern Progressive Web App (PWA) using Lit web components, Vite build tool, and Bun runtime.

## Current State Analysis

### Technology Stack (Before)
- **Framework**: Django 5.0.4 server-side rendering
- **Enhancement**: HTMX 2.0.1 for progressive enhancement
- **Styling**: Bootstrap 4 ProductionReady theme
- **Real-time**: Django Channels + WebSocket
- **State**: Django sessions + Redis cache
- **Build**: None (pure Django)

### Views & Templates
- 16 Django templates (~600 lines)
- 3 main view modules (articles, profiles, comments)
- HTMX infinite scroll pagination
- Real-time comments via WebSocket

## Target State Architecture

### Technology Stack (After)
- **Framework**: Lit 3.x (web components)
- **Build Tool**: Vite 5.x (fast dev server, optimized builds)
- **Runtime**: Bun 1.x (fast package manager & runtime)
- **Router**: @vaadin/router (web component routing)
- **State**: Lit Context API + local storage
- **Styling**: CSS Modules + Tailwind CSS
- **PWA**: Workbox for service worker
- **API Client**: fetch API with interceptors
- **Real-time**: WebSocket with auto-reconnect

## Project Structure

```
frontend/
├── src/
│   ├── components/              # Lit web components
│   │   ├── common/              # Shared components
│   │   │   ├── app-header.ts    # Navigation header
│   │   │   ├── app-footer.ts    # Footer
│   │   │   ├── loading-spinner.ts
│   │   │   ├── error-message.ts
│   │   │   └── pagination.ts
│   │   ├── auth/                # Authentication components
│   │   │   ├── login-form.ts
│   │   │   ├── register-form.ts
│   │   │   └── user-settings.ts
│   │   ├── articles/            # Article components
│   │   │   ├── article-list.ts
│   │   │   ├── article-preview.ts
│   │   │   ├── article-detail.ts
│   │   │   ├── article-editor.ts
│   │   │   ├── article-meta.ts
│   │   │   └── tag-list.ts
│   │   ├── profiles/            # Profile components
│   │   │   ├── profile-page.ts
│   │   │   ├── profile-articles.ts
│   │   │   └── follow-button.ts
│   │   └── comments/            # Comment components
│   │       ├── comment-list.ts
│   │       ├── comment-form.ts
│   │       └── comment-item.ts
│   ├── views/                   # Page-level components
│   │   ├── home-view.ts         # Landing page
│   │   ├── article-view.ts      # Article detail page
│   │   ├── editor-view.ts       # Article editor
│   │   ├── profile-view.ts      # User profile
│   │   ├── settings-view.ts     # User settings
│   │   └── auth-view.ts         # Login/register
│   ├── services/                # Business logic & API
│   │   ├── api/                 # API client
│   │   │   ├── client.ts        # Base fetch client
│   │   │   ├── articles.ts      # Article API
│   │   │   ├── auth.ts          # Auth API
│   │   │   ├── profiles.ts      # Profile API
│   │   │   ├── comments.ts      # Comment API
│   │   │   └── tags.ts          # Tags API
│   │   ├── websocket.ts         # WebSocket service
│   │   ├── storage.ts           # LocalStorage wrapper
│   │   └── auth-service.ts      # Auth state management
│   ├── contexts/                # Lit Context providers
│   │   ├── auth-context.ts      # User auth state
│   │   └── theme-context.ts     # Theme state
│   ├── router/                  # Routing configuration
│   │   ├── index.ts             # Router setup
│   │   ├── routes.ts            # Route definitions
│   │   └── guards.ts            # Auth guards
│   ├── styles/                  # Global styles
│   │   ├── global.css           # Global CSS
│   │   ├── variables.css        # CSS variables
│   │   └── tailwind.css         # Tailwind imports
│   ├── utils/                   # Utility functions
│   │   ├── validators.ts        # Form validation
│   │   ├── formatters.ts        # Date/text formatting
│   │   └── slugify.ts           # Slug generation
│   ├── types/                   # TypeScript types
│   │   ├── api.ts               # API response types
│   │   ├── models.ts            # Domain models
│   │   └── router.ts            # Router types
│   ├── app.ts                   # Root app component
│   ├── main.ts                  # Application entry point
│   └── vite-env.d.ts            # Vite type declarations
├── public/                      # Static assets
│   ├── manifest.json            # PWA manifest
│   ├── icons/                   # PWA icons
│   ├── favicon.ico
│   └── robots.txt
├── index.html                   # HTML entry point
├── vite.config.ts               # Vite configuration
├── tailwind.config.js           # Tailwind configuration
├── tsconfig.json                # TypeScript configuration
├── bunfig.toml                  # Bun configuration
└── package.json                 # Dependencies
```

## Migration Phases

### Phase 1: Project Setup & Infrastructure ✅ (Target)
**Goal**: Bootstrap Lit PWA project with Vite and Bun

**Tasks**:
1. Initialize Bun project with Lit template
2. Configure Vite for optimal development and production builds
3. Set up TypeScript with strict mode
4. Configure Tailwind CSS with custom theme
5. Set up ESLint + Prettier for code quality
6. Create base HTML template with PWA meta tags
7. Set up development environment

**Deliverables**:
- Working Vite dev server
- TypeScript compilation
- Tailwind CSS processing
- Hot module replacement (HMR)
- Basic project structure

**Configuration Files**:
- `package.json` - Dependencies and scripts
- `vite.config.ts` - Build configuration
- `tsconfig.json` - TypeScript settings
- `tailwind.config.js` - Tailwind theme
- `bunfig.toml` - Bun settings

### Phase 2: Core Architecture & Routing ✅ (Target)
**Goal**: Establish application foundation with routing and state

**Tasks**:
1. Create root app component (`app.ts`)
2. Set up @vaadin/router with route definitions
3. Implement auth guards for protected routes
4. Create Lit Context for auth state
5. Build API client with interceptors
6. Set up localStorage service for persistence
7. Create base page components (views)

**Deliverables**:
- Working client-side routing
- Auth state management
- API client foundation
- Navigation between views
- Protected routes

**Key Components**:
- `src/app.ts` - Root component
- `src/router/index.ts` - Router setup
- `src/contexts/auth-context.ts` - Auth state
- `src/services/api/client.ts` - API client

### Phase 3: Authentication Module ✅ (Target)
**Goal**: Implement user authentication and registration

**Tasks**:
1. Build login form component
2. Build register form component
3. Build user settings component
4. Implement JWT token management
5. Create auth service with login/logout
6. Add form validation
7. Handle auth errors and feedback
8. Persist user state

**Deliverables**:
- Login page functional
- Register page functional
- Settings page functional
- Token refresh logic
- Form validation
- Error handling

**Components**:
- `auth/login-form.ts`
- `auth/register-form.ts`
- `auth/user-settings.ts`
- `services/auth-service.ts`

### Phase 4: Article Components ✅ (Target)
**Goal**: Build article listing and viewing functionality

**Tasks**:
1. Create article preview component
2. Build article list with pagination
3. Implement article detail view
4. Add favorite/unfavorite button
5. Build tag filtering
6. Create article meta component (author, date, actions)
7. Implement infinite scroll or pagination
8. Add feed/global toggle

**Deliverables**:
- Home page with article feed
- Article detail page
- Tag filtering working
- Favorite functionality
- Pagination/infinite scroll

**Components**:
- `articles/article-list.ts`
- `articles/article-preview.ts`
- `articles/article-detail.ts`
- `articles/article-meta.ts`
- `articles/tag-list.ts`
- `views/home-view.ts`
- `views/article-view.ts`

### Phase 5: Article Editor ✅ (Target)
**Goal**: Enable article creation and editing

**Tasks**:
1. Build article editor component
2. Implement markdown editor (or rich text)
3. Add tag input with autocomplete
4. Form validation for article fields
5. Create article API integration
6. Update article API integration
7. Handle image uploads (if applicable)
8. Preview functionality

**Deliverables**:
- Article creation working
- Article editing working
- Tag management
- Form validation
- Draft saving (optional)

**Components**:
- `articles/article-editor.ts`
- `views/editor-view.ts`
- `services/api/articles.ts`

### Phase 6: Profile Module ✅ (Target)
**Goal**: Implement user profiles and following

**Tasks**:
1. Build profile page component
2. Create follow/unfollow button
3. Display user's articles
4. Display favorited articles
5. Show follower/following counts
6. Implement profile API integration
7. Add profile image display

**Deliverables**:
- Profile pages functional
- Follow/unfollow working
- User articles displayed
- Favorited articles shown

**Components**:
- `profiles/profile-page.ts`
- `profiles/profile-articles.ts`
- `profiles/follow-button.ts`
- `views/profile-view.ts`
- `services/api/profiles.ts`

### Phase 7: Comments Module ✅ (Target)
**Goal**: Add commenting functionality

**Tasks**:
1. Build comment list component
2. Create comment form
3. Build individual comment item
4. Implement comment API integration
5. Add delete comment (with auth check)
6. Real-time updates via WebSocket
7. Optimistic UI updates

**Deliverables**:
- Comment display working
- Comment creation working
- Comment deletion working
- Real-time updates (if WebSocket ready)

**Components**:
- `comments/comment-list.ts`
- `comments/comment-form.ts`
- `comments/comment-item.ts`
- `services/api/comments.ts`
- `services/websocket.ts`

### Phase 8: Shared Components & UX ✅ (Target)
**Goal**: Polish UI and add common components

**Tasks**:
1. Build app header with navigation
2. Create app footer
3. Add loading spinner component
4. Build error message component
5. Create pagination component
6. Add toast notifications
7. Implement modal dialogs
8. Add empty states

**Deliverables**:
- Consistent navigation
- Loading states
- Error handling UI
- Notifications
- Better UX overall

**Components**:
- `common/app-header.ts`
- `common/app-footer.ts`
- `common/loading-spinner.ts`
- `common/error-message.ts`
- `common/pagination.ts`
- `common/toast.ts`
- `common/modal.ts`

### Phase 9: PWA Features ✅ (Target)
**Goal**: Transform into a Progressive Web App

**Tasks**:
1. Create PWA manifest.json
2. Generate PWA icons (multiple sizes)
3. Set up Workbox service worker
4. Implement offline caching strategy
5. Add offline page
6. Implement background sync
7. Add install prompt
8. Test PWA features

**Deliverables**:
- PWA manifest configured
- Service worker functional
- Offline support
- Installable app
- Passes Lighthouse PWA audit

**Files**:
- `public/manifest.json`
- `public/icons/` (multiple sizes)
- `src/sw.ts` - Service worker
- Vite PWA plugin config

### Phase 10: Testing & Optimization ✅ (Target)
**Goal**: Ensure quality and performance

**Tasks**:
1. Set up Vitest for unit tests
2. Add Web Test Runner for component tests
3. Test critical user flows
4. Run Lighthouse audits
5. Optimize bundle size
6. Implement code splitting
7. Add lazy loading for routes
8. Optimize images
9. Performance monitoring

**Deliverables**:
- Unit tests for services
- Component tests for key components
- Lighthouse score > 90
- Optimized bundle sizes
- Fast page loads

**Testing Tools**:
- Vitest for unit tests
- @web/test-runner for component tests
- Lighthouse CI

### Phase 11: Deployment & Documentation ✅ (Target)
**Goal**: Deploy and document the application

**Tasks**:
1. Build production bundle
2. Configure Docker for frontend
3. Update docker-compose.yml
4. Set up environment variables
5. Configure CORS for API
6. Write user documentation
7. Write developer documentation
8. Create README with setup instructions

**Deliverables**:
- Production-ready build
- Docker configuration
- Updated docker-compose
- Complete documentation
- Deployment guide

**Documentation**:
- `frontend/README.md`
- `frontend/DEVELOPER.md`
- Updated root `README.md`

## Technology Decisions

### Why Lit?
1. **Web Standards**: Built on Web Components standard
2. **Performance**: Lightweight (~5KB), fast rendering
3. **Simplicity**: Easy to learn, minimal API surface
4. **Interoperability**: Works with any framework or vanilla JS
5. **Future-proof**: Based on web standards, not framework-specific
6. **TypeScript**: First-class TypeScript support
7. **No Virtual DOM**: Direct DOM manipulation is faster

### Why Vite?
1. **Speed**: Lightning-fast dev server with HMR
2. **Modern**: ESM-first, optimized for modern browsers
3. **Plugin Ecosystem**: Rich plugin ecosystem
4. **Build Optimization**: Rollup-based production builds
5. **TypeScript**: Built-in TypeScript support
6. **Developer Experience**: Great DX with instant server start

### Why Bun?
1. **Performance**: 3x faster than npm, 25x faster than yarn
2. **All-in-one**: Runtime, package manager, bundler, test runner
3. **TypeScript**: Native TypeScript execution
4. **Compatibility**: Drop-in replacement for Node.js
5. **Modern**: Built for modern JavaScript
6. **Developer Experience**: Fast installs, hot reloading

### Why @vaadin/router?
1. **Web Components**: Designed for web components
2. **Lightweight**: Small footprint
3. **Features**: Lazy loading, guards, nested routes
4. **TypeScript**: Good TypeScript support
5. **Mature**: Battle-tested in production

### Why Tailwind CSS?
1. **Utility-first**: Rapid development
2. **Customization**: Fully customizable
3. **Consistency**: Design system built-in
4. **Performance**: Purged CSS in production
5. **Developer Experience**: Great DX with IntelliSense

## API Integration Strategy

### REST API Client
- Base client with interceptors for:
  - JWT token injection
  - Error handling
  - Loading state management
  - Request/response transformation
- Type-safe API calls with TypeScript
- Automatic token refresh
- Request cancellation for component unmount

### WebSocket Integration
- Auto-reconnecting WebSocket client
- Event-based message handling
- Connection state management
- Heartbeat/ping-pong for keep-alive
- Message queue for offline messages
- Integration with Lit components via events

### State Management
- Lit Context API for global state (auth, theme)
- Component local state for UI state
- LocalStorage for persistence
- No heavy state management library needed

## Styling Strategy

### Approach
1. **Tailwind CSS**: Primary styling method
2. **CSS Modules**: Component-scoped styles when needed
3. **CSS Custom Properties**: Theme variables
4. **Shadow DOM**: Encapsulated component styles

### Theme System
- Light/dark mode support
- CSS custom properties for theming
- Tailwind theme configuration
- Smooth theme transitions

### Responsive Design
- Mobile-first approach
- Tailwind breakpoints (sm, md, lg, xl, 2xl)
- Fluid typography
- Responsive images

## PWA Features

### Manifest
- App name, description, icons
- Start URL and scope
- Display mode (standalone)
- Theme and background colors
- Orientation preferences

### Service Worker (Workbox)
- **Caching Strategy**:
  - App shell: Cache-first
  - API calls: Network-first with fallback
  - Images: Cache-first with expiration
  - Static assets: Precache
- **Offline Support**:
  - Offline page for navigation
  - Cached API responses
  - Queue failed requests
- **Background Sync**:
  - Retry failed requests when online
  - Update articles in background

### Install Experience
- Install prompt component
- Dismiss and remember choice
- iOS Safari install instructions

## Performance Targets

### Metrics
- **Lighthouse Score**: > 90 in all categories
- **First Contentful Paint (FCP)**: < 1.5s
- **Time to Interactive (TTI)**: < 3.5s
- **Total Bundle Size**: < 150KB (gzipped)
- **Code Coverage**: > 70%

### Optimizations
1. **Code Splitting**: Lazy load routes
2. **Tree Shaking**: Remove unused code
3. **Minification**: Terser for JS, cssnano for CSS
4. **Compression**: Brotli/Gzip
5. **Image Optimization**: WebP format, lazy loading
6. **Font Optimization**: Font subsetting, font-display: swap
7. **Caching**: Service worker + HTTP caching
8. **Preloading**: Critical resources

## Development Workflow

### Commands
```bash
# Install dependencies
bun install

# Start dev server
bun run dev

# Build for production
bun run build

# Preview production build
bun run preview

# Run tests
bun run test

# Run linter
bun run lint

# Format code
bun run format

# Type check
bun run type-check
```

### Git Workflow
1. Create feature branch from main
2. Develop with commits per logical change
3. Run tests and lint before commit
4. Push to remote branch
5. Create pull request
6. Review and merge

## Testing Strategy

### Unit Tests (Vitest)
- Services (API clients, utilities)
- Business logic functions
- Validation functions
- Helper functions
- Target: > 80% coverage

### Component Tests (@web/test-runner)
- Render tests
- User interaction tests
- State changes
- Event handling
- Accessibility tests
- Target: Critical components tested

### E2E Tests (Optional - Playwright)
- User flows (login, create article, comment)
- Cross-browser testing
- Mobile testing
- Target: Happy paths covered

## Migration Risks & Mitigation

### Risks
1. **WebSocket Compatibility**: Django Channels → Native WebSocket
   - Mitigation: Test early, create adapter layer
2. **API Response Format**: Django Rest Framework → FastAPI
   - Mitigation: Update API client types, add transformation layer
3. **Authentication**: Session-based → JWT-only
   - Mitigation: Implement token refresh, handle edge cases
4. **SEO**: SSR → SPA
   - Mitigation: Use meta tags, consider prerendering
5. **Browser Support**: Web Components compatibility
   - Mitigation: Polyfills for older browsers, graceful degradation

### Backward Compatibility
- Keep Django frontend running during migration
- Use feature flags for gradual rollout
- A/B test new frontend
- Monitor errors and user feedback

## Environment Variables

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws

# Feature Flags
VITE_ENABLE_WEBSOCKET=true
VITE_ENABLE_PWA=true
VITE_ENABLE_ANALYTICS=false

# Environment
VITE_ENV=development
```

## Browser Support

### Target Browsers
- Chrome/Edge: last 2 versions
- Firefox: last 2 versions
- Safari: last 2 versions
- Mobile Safari: iOS 14+
- Chrome Android: last 2 versions

### Polyfills (if needed)
- Web Components polyfills for Safari < 14
- IntersectionObserver for lazy loading
- ResizeObserver for responsive components

## Success Criteria

### Functional
- ✅ All features from Django frontend implemented
- ✅ User can perform all CRUD operations
- ✅ Real-time comments working
- ✅ Authentication and authorization working
- ✅ Profile management working
- ✅ Article favorites and tags working

### Non-Functional
- ✅ Lighthouse score > 90
- ✅ Bundle size < 150KB gzipped
- ✅ Page load < 2s on 3G
- ✅ Works offline (basic functionality)
- ✅ Installable as PWA
- ✅ Accessible (WCAG 2.1 AA)
- ✅ Cross-browser compatible
- ✅ Mobile responsive

### Developer Experience
- ✅ Fast dev server (< 1s cold start)
- ✅ Hot module replacement working
- ✅ Type-safe codebase
- ✅ Well-documented code
- ✅ Easy to onboard new developers

## Timeline Estimate

**Total Duration**: 2-3 days of development

- **Phase 1**: Setup & Infrastructure - 2 hours
- **Phase 2**: Core Architecture - 2 hours
- **Phase 3**: Authentication - 3 hours
- **Phase 4**: Article Components - 4 hours
- **Phase 5**: Article Editor - 2 hours
- **Phase 6**: Profile Module - 2 hours
- **Phase 7**: Comments Module - 2 hours
- **Phase 8**: Shared Components - 2 hours
- **Phase 9**: PWA Features - 2 hours
- **Phase 10**: Testing & Optimization - 3 hours
- **Phase 11**: Deployment & Documentation - 2 hours

## Next Steps

1. **Review and Approve Plan**: Stakeholder sign-off
2. **Set Up Project**: Initialize Lit PWA with Vite and Bun
3. **Phase 1-2**: Build foundation (routing, API client, auth)
4. **Phase 3-7**: Implement features module by module
5. **Phase 8-9**: Polish and add PWA features
6. **Phase 10-11**: Test, optimize, document, deploy

## Appendix

### Key Dependencies

```json
{
  "dependencies": {
    "lit": "^3.1.0",
    "@vaadin/router": "^1.7.5",
    "@lit/context": "^1.1.0",
    "@lit/task": "^1.0.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "typescript": "^5.3.0",
    "tailwindcss": "^3.4.0",
    "@types/node": "^20.10.0",
    "vite-plugin-pwa": "^0.17.0",
    "workbox-window": "^7.0.0",
    "vitest": "^1.0.0",
    "@web/test-runner": "^0.18.0",
    "eslint": "^8.55.0",
    "prettier": "^3.1.0"
  }
}
```

### Useful Resources
- **Lit Documentation**: https://lit.dev/
- **Vite Guide**: https://vitejs.dev/guide/
- **Bun Documentation**: https://bun.sh/docs
- **Vaadin Router**: https://github.com/vaadin/router
- **Workbox**: https://developer.chrome.com/docs/workbox/
- **Web Components**: https://developer.mozilla.org/en-US/docs/Web/Web_Components

---

**Document Version**: 1.0
**Last Updated**: 2025-01-12
**Author**: Claude AI Assistant
**Status**: Ready for Implementation
