import { LitElement, html, css } from 'lit';
import { customElement } from 'lit/decorators.js';
import { Router } from '@vaadin/router';
import './styles/global.css';
import './components/common/app-header';
import './components/common/app-footer';

@customElement('app-root')
export class AppRoot extends LitElement {
  static styles = css`
    :host {
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }

    #outlet {
      flex: 1;
      display: flex;
      flex-direction: column;
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
      <app-header></app-header>
      <div id="outlet"></div>
      <app-footer></app-footer>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'app-root': AppRoot;
  }
}
