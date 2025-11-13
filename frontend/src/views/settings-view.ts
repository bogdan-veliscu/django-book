import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { authService } from '../services/auth-service';
import '../components/auth/user-settings';

@customElement('settings-view')
export class SettingsView extends LitElement {
  static styles = css`
    :host {
      display: block;
      max-width: 540px;
      margin: 2rem auto;
      padding: 0 1rem;
    }

    h1 {
      text-align: center;
      margin-bottom: 1.5rem;
    }
  `;

  @state()
  private isAuthenticated = false;

  connectedCallback() {
    super.connectedCallback();

    // Check if user is authenticated
    this.isAuthenticated = authService.isAuthenticated();

    // Redirect to login if not authenticated
    if (!this.isAuthenticated) {
      window.location.href = '/login';
      return;
    }

    // Subscribe to auth changes
    this.unsubscribe = authService.subscribe((user) => {
      this.isAuthenticated = user !== null;
      if (!this.isAuthenticated) {
        window.location.href = '/login';
      }
    });
  }

  private unsubscribe?: () => void;

  disconnectedCallback() {
    super.disconnectedCallback();
    if (this.unsubscribe) {
      this.unsubscribe();
    }
  }

  render() {
    if (!this.isAuthenticated) {
      return html`<div>Redirecting to login...</div>`;
    }

    return html`
      <h1>Your Settings</h1>
      <user-settings></user-settings>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'settings-view': SettingsView;
  }
}
