# Conduit Frontend - Lit PWA

A modern Progressive Web App (PWA) implementation of the RealWorld Conduit frontend built with Lit web components, Vite, and Bun.

## Tech Stack

- **Lit 3.x** - Fast, lightweight web components
- **Vite 5.x** - Lightning-fast dev server and build tool
- **Bun 1.x** - Fast package manager and runtime
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **@vaadin/router** - Client-side routing for web components
- **Workbox** - PWA service worker support

## Features

- ⚡ Lightning-fast development with Vite HMR
- 📱 Progressive Web App (PWA) with offline support
- 🎨 Modern UI with Tailwind CSS
- 🔐 JWT authentication
- 📝 Article CRUD operations
- 👤 User profiles and following
- 💬 Real-time comments
- 🏷️ Article tagging and filtering
- ♥️ Article favorites
- 🌐 Web Components standard
- 🎯 TypeScript for type safety
- 🧪 Unit and component testing setup

## Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable Lit components
│   ├── views/            # Page-level components
│   ├── services/         # API clients and business logic
│   ├── types/            # TypeScript type definitions
│   ├── styles/           # Global styles and Tailwind
│   ├── app.ts            # Root application component
│   └── main.ts           # Application entry point
├── public/               # Static assets
├── index.html            # HTML entry point
├── vite.config.ts        # Vite configuration
├── tailwind.config.js    # Tailwind configuration
└── tsconfig.json         # TypeScript configuration
```

## Getting Started

### Prerequisites

- [Bun](https://bun.sh/) 1.0+ (or Node.js 18+)
- Backend API running on http://localhost:8000

### Installation

```bash
# Install dependencies
bun install

# or with npm
npm install
```

### Development

```bash
# Start dev server
bun run dev

# Server will run on http://localhost:3000
```

The dev server includes:
- Hot Module Replacement (HMR)
- API proxy to backend
- WebSocket proxy for real-time features

### Building

```bash
# Build for production
bun run build

# Output will be in dist/
```

### Preview Production Build

```bash
# Preview production build
bun run preview
```

### Testing

```bash
# Run tests
bun run test

# Run tests with UI
bun run test:ui

# Run tests with coverage
bun run coverage
```

### Linting & Formatting

```bash
# Lint code
bun run lint

# Format code
bun run format

# Type check
bun run type-check
```

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
```

## API Integration

The frontend communicates with the FastAPI backend through a type-safe API client:

- **Base URL**: `/api` (proxied to backend in dev)
- **Authentication**: JWT tokens in Authorization header
- **WebSocket**: Real-time comment updates

## PWA Features

- **Installable**: Can be installed as a standalone app
- **Offline Support**: Works offline with cached data
- **Service Worker**: Automatic caching and background sync
- **App Manifest**: Configurable app metadata and icons

### Generating PWA Icons

Before deploying, you need to generate the PWA icons:

```bash
cd public/icons

# Option 1: Using ImageMagick
./generate-icons.sh

# Option 2: Using Node.js sharp
npm install sharp
./generate-icons.js

# Option 3: Use online tools (see public/icons/README.md)
```

The icon generation process creates PNG files in all required sizes (72x72 to 512x512) from the source SVG file. See `public/icons/README.md` for detailed instructions.

## Browser Support

- Chrome/Edge: last 2 versions
- Firefox: last 2 versions
- Safari: last 2 versions
- Mobile Safari: iOS 14+
- Chrome Android: last 2 versions

## Development Status

### Phase 1: Foundation ✅
- Project setup with Vite and Bun
- TypeScript configuration
- Tailwind CSS integration
- Base styles and theme

### Phase 2: Core Architecture ✅
- API client with interceptors
- Auth service with state management
- Router setup with lazy loading
- Type definitions

### Phase 3-11: In Progress 🚧
- Authentication UI
- Article components
- Profile components
- Comments with WebSocket
- Shared components
- PWA features
- Testing
- Optimization

## Contributing

1. Create feature branch
2. Make changes
3. Run tests and linting
4. Create pull request

## Performance Targets

- Lighthouse Score: > 90
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3.5s
- Bundle Size: < 150KB gzipped

## Documentation

- [Migration Plan](../docs/Plan.md) - Detailed migration plan
- [Lit Documentation](https://lit.dev/) - Lit framework docs
- [Vite Guide](https://vitejs.dev/guide/) - Vite build tool docs

## License

MIT
