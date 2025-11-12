import { LitElement, html, css } from 'lit';
import { customElement } from 'lit/decorators.js';

@customElement('auth-view')
export class AuthView extends LitElement {
  static styles = css`
    :host {
      display: block;
      max-width: 540px;
      margin: 2rem auto;
      padding: 0 1rem;
    }

    h1 {
      text-align: center;
      margin-bottom: 0.5rem;
    }

    .text-center {
      text-align: center;
      margin-bottom: 1rem;
    }

    a {
      color: #5cb85c;
      text-decoration: none;
    }

    a:hover {
      text-decoration: underline;
    }
  `;

  render() {
    const isLogin = window.location.pathname === '/login';

    return html`
      <h1>${isLogin ? 'Sign In' : 'Sign Up'}</h1>
      <div class="text-center">
        <a href="${isLogin ? '/register' : '/login'}">
          ${isLogin ? 'Need an account?' : 'Have an account?'}
        </a>
      </div>
      <p>Authentication form will be implemented here.</p>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'auth-view': AuthView;
  }
}
