import { LitElement, html, css } from 'lit';
import { customElement } from 'lit/decorators.js';
import { Router } from '@vaadin/router';
import './styles/global.css';

@customElement('app-root')
export class AppRoot extends LitElement {
  static styles = css`
    :host {
      display: block;
      min-height: 100vh;
    }
  `;

  firstUpdated() {
    const outlet = this.shadowRoot?.getElementById('outlet');
    if (outlet) {
      const router = new Router(outlet);
      router.setRoutes([
        {
          path: '/',
          component: 'home-view',
          action: async () => {
            await import('./views/home-view');
          },
        },
        {
          path: '/login',
          component: 'auth-view',
          action: async () => {
            await import('./views/auth-view');
          },
        },
        {
          path: '/register',
          component: 'auth-view',
          action: async () => {
            await import('./views/auth-view');
          },
        },
        {
          path: '/article/:slug',
          component: 'article-view',
          action: async () => {
            await import('./views/article-view');
          },
        },
        {
          path: '/editor/:slug?',
          component: 'editor-view',
          action: async () => {
            await import('./views/editor-view');
          },
        },
        {
          path: '/settings',
          component: 'settings-view',
          action: async () => {
            await import('./views/settings-view');
          },
        },
        {
          path: '/profile/:username',
          component: 'profile-view',
          action: async () => {
            await import('./views/profile-view');
          },
        },
        {
          path: '(.*)',
          redirect: '/',
        },
      ]);
    }
  }

  render() {
    return html`
      <div id="outlet"></div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'app-root': AppRoot;
  }
}
