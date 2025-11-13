import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { authService } from '../../services/auth-service';
import type { User } from '@/types/models';

@customElement('app-header')
export class AppHeader extends LitElement {
  static styles = css`
    :host {
      display: block;
      background: white;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    nav {
      max-width: 1140px;
      margin: 0 auto;
      padding: 0.5rem 1rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .brand {
      font-size: 1.5rem;
      font-weight: bold;
      color: #5cb85c;
      text-decoration: none;
      font-family: 'Titillium Web', serif;
      transition: color 0.2s;
    }

    .brand:hover {
      color: #449d44;
    }

    .nav-links {
      display: flex;
      gap: 1rem;
      align-items: center;
      list-style: none;
      margin: 0;
      padding: 0;
    }

    .nav-link {
      color: rgba(0, 0, 0, 0.5);
      text-decoration: none;
      padding: 0.5rem 0.75rem;
      transition: color 0.2s;
      font-size: 1rem;
      display: flex;
      align-items: center;
      gap: 0.25rem;
    }

    .nav-link:hover {
      color: rgba(0, 0, 0, 0.8);
    }

    .nav-link.active {
      color: rgba(0, 0, 0, 0.8);
    }

    .nav-link ion-icon {
      font-size: 1.25rem;
    }

    .user-pic {
      width: 26px;
      height: 26px;
      border-radius: 50%;
      object-fit: cover;
    }

    @media (max-width: 768px) {
      nav {
        padding: 0.5rem;
      }

      .nav-links {
        gap: 0.5rem;
      }

      .nav-link {
        padding: 0.5rem;
        font-size: 0.9rem;
      }

      .brand {
        font-size: 1.25rem;
      }
    }

    @media (max-width: 480px) {
      .nav-link span:not(.icon) {
        display: none;
      }

      .nav-link ion-icon {
        font-size: 1.5rem;
      }

      .nav-links {
        gap: 0.25rem;
      }

      .nav-link {
        padding: 0.25rem 0.5rem;
      }
    }
  `;

  @state()
  private currentUser: User | null = null;

  @state()
  private currentPath: string = window.location.pathname;

  private unsubscribe?: () => void;

  connectedCallback(): void {
    super.connectedCallback();
    this.currentUser = authService.getUser();

    // Subscribe to auth changes
    this.unsubscribe = authService.subscribe((user) => {
      this.currentUser = user;
    });

    // Listen for route changes
    window.addEventListener('vaadin-router-location-changed', this.handleRouteChange);
    window.addEventListener('popstate', this.handleRouteChange);
  }

  disconnectedCallback(): void {
    super.disconnectedCallback();
    if (this.unsubscribe) {
      this.unsubscribe();
    }
    window.removeEventListener('vaadin-router-location-changed', this.handleRouteChange);
    window.removeEventListener('popstate', this.handleRouteChange);
  }

  private handleRouteChange = (): void => {
    this.currentPath = window.location.pathname;
  };

  private isActive(path: string): boolean {
    if (path === '/') {
      return this.currentPath === '/';
    }
    return this.currentPath.startsWith(path);
  }

  private renderAuthenticatedLinks() {
    const username = this.currentUser?.username || '';
    const image = this.currentUser?.image;

    return html`
      <li>
        <a
          href="/editor"
          class="nav-link ${this.isActive('/editor') ? 'active' : ''}"
        >
          <ion-icon name="create-outline"></ion-icon>
          <span>New Article</span>
        </a>
      </li>
      <li>
        <a
          href="/settings"
          class="nav-link ${this.isActive('/settings') ? 'active' : ''}"
        >
          <ion-icon name="settings-outline"></ion-icon>
          <span>Settings</span>
        </a>
      </li>
      <li>
        <a
          href="/profile/${username}"
          class="nav-link ${this.isActive('/profile') ? 'active' : ''}"
        >
          ${image
            ? html`<img src="${image}" alt="${username}" class="user-pic" />`
            : html`<ion-icon name="person-outline"></ion-icon>`}
          <span>${username}</span>
        </a>
      </li>
    `;
  }

  private renderUnauthenticatedLinks() {
    return html`
      <li>
        <a
          href="/login"
          class="nav-link ${this.isActive('/login') ? 'active' : ''}"
        >
          <span>Sign in</span>
        </a>
      </li>
      <li>
        <a
          href="/register"
          class="nav-link ${this.isActive('/register') ? 'active' : ''}"
        >
          <span>Sign up</span>
        </a>
      </li>
    `;
  }

  render() {
    const isAuthenticated = this.currentUser !== null;

    return html`
      <nav>
        <a href="/" class="brand">conduit</a>
        <ul class="nav-links">
          <li>
            <a
              href="/"
              class="nav-link ${this.isActive('/') ? 'active' : ''}"
            >
              <span>Home</span>
            </a>
          </li>
          ${isAuthenticated
            ? this.renderAuthenticatedLinks()
            : this.renderUnauthenticatedLinks()}
        </ul>
      </nav>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'app-header': AppHeader;
  }
}
