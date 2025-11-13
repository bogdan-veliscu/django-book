import { LitElement, html, css } from 'lit';
import { customElement, state, query } from 'lit/decorators.js';
import { authService } from '../../services/auth-service';
import type { ApiError } from '@/types/api';
import type { User } from '@/types/models';

@customElement('user-settings')
export class UserSettings extends LitElement {
  static styles = css`
    :host {
      display: block;
    }

    .error-messages {
      margin-bottom: 1rem;
      padding: 0.75rem 1rem;
      background-color: #f8d7da;
      border: 1px solid #f5c6cb;
      border-radius: 0.25rem;
      color: #721c24;
    }

    .error-messages ul {
      margin: 0;
      padding-left: 1.5rem;
    }

    .error-messages li {
      margin: 0.25rem 0;
    }

    form {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    input,
    textarea {
      padding: 0.75rem 1rem;
      font-size: 1rem;
      border: 1px solid #ccc;
      border-radius: 0.25rem;
      width: 100%;
      box-sizing: border-box;
      font-family: inherit;
    }

    textarea {
      min-height: 8rem;
      resize: vertical;
    }

    input:focus,
    textarea:focus {
      outline: none;
      border-color: #5cb85c;
    }

    .button-group {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
    }

    button {
      padding: 0.75rem 1.5rem;
      font-size: 1.25rem;
      border: 1px solid;
      border-radius: 0.3rem;
      cursor: pointer;
    }

    .btn-primary {
      color: white;
      background-color: #5cb85c;
      border-color: #5cb85c;
    }

    .btn-primary:hover:not(:disabled) {
      background-color: #449d44;
      border-color: #419641;
    }

    .btn-danger {
      color: #b85c5c;
      background-color: transparent;
      border-color: #b85c5c;
    }

    .btn-danger:hover:not(:disabled) {
      color: white;
      background-color: #b85c5c;
    }

    button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  `;

  @state()
  private loading = false;

  @state()
  private errors: string[] = [];

  @state()
  private currentUser: User | null = null;

  @query('form')
  private form!: HTMLFormElement;

  connectedCallback() {
    super.connectedCallback();
    this.currentUser = authService.getUser();

    // Subscribe to auth changes
    this.unsubscribe = authService.subscribe((user) => {
      this.currentUser = user;
    });
  }

  private unsubscribe?: () => void;

  disconnectedCallback() {
    super.disconnectedCallback();
    if (this.unsubscribe) {
      this.unsubscribe();
    }
  }

  private async handleSubmit(e: Event) {
    e.preventDefault();
    this.errors = [];

    const formData = new FormData(this.form);
    const image = formData.get('image') as string;
    const username = formData.get('username') as string;
    const bio = formData.get('bio') as string;
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;

    // Client-side validation
    const validationErrors: string[] = [];

    if (email && !this.isValidEmail(email)) {
      validationErrors.push('Email must be a valid email address');
    }

    if (username && username.length < 3) {
      validationErrors.push('Username must be at least 3 characters long');
    }

    if (password && password.length > 0 && password.length < 8) {
      validationErrors.push('Password must be at least 8 characters long');
    }

    if (validationErrors.length > 0) {
      this.errors = validationErrors;
      return;
    }

    this.loading = true;

    try {
      // Only include fields that have values
      const updates: any = {};

      if (image && image.trim()) updates.image = image;
      if (username && username.trim()) updates.username = username;
      if (bio !== undefined) updates.bio = bio; // Allow empty string to clear bio
      if (email && email.trim()) updates.email = email;
      if (password && password.trim()) updates.password = password;

      await authService.updateUser(updates);

      // Clear password field after successful update
      const passwordInput = this.form.querySelector(
        'input[name="password"]'
      ) as HTMLInputElement;
      if (passwordInput) {
        passwordInput.value = '';
      }

      this.loading = false;

      // Dispatch custom event for successful update
      this.dispatchEvent(
        new CustomEvent('settings-updated', {
          bubbles: true,
          composed: true,
        })
      );
    } catch (error: any) {
      this.loading = false;

      // Handle API errors
      if (error.errors) {
        const apiError = error as ApiError;
        this.errors = Object.entries(apiError.errors).flatMap(
          ([key, messages]) =>
            messages.map((msg) => `${key}: ${msg}`)
        );
      } else {
        this.errors = [error.message || 'Update failed. Please try again.'];
      }
    }
  }

  private handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
      authService.logout();
    }
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  render() {
    if (!this.currentUser) {
      return html`<div>Loading...</div>`;
    }

    return html`
      ${this.errors.length > 0
        ? html`
            <div class="error-messages">
              <ul>
                ${this.errors.map((error) => html`<li>${error}</li>`)}
              </ul>
            </div>
          `
        : ''}

      <form @submit=${this.handleSubmit}>
        <input
          type="url"
          name="image"
          placeholder="URL of profile picture"
          .value=${this.currentUser.image || ''}
          ?disabled=${this.loading}
        />
        <input
          type="text"
          name="username"
          placeholder="Username"
          .value=${this.currentUser.username || ''}
          ?disabled=${this.loading}
          minlength="3"
        />
        <textarea
          name="bio"
          placeholder="Short bio about you"
          .value=${this.currentUser.bio || ''}
          ?disabled=${this.loading}
        ></textarea>
        <input
          type="email"
          name="email"
          placeholder="Email"
          .value=${this.currentUser.email || ''}
          ?disabled=${this.loading}
        />
        <input
          type="password"
          name="password"
          placeholder="New Password"
          ?disabled=${this.loading}
          minlength="8"
        />

        <div class="button-group">
          <button
            type="button"
            class="btn-danger"
            @click=${this.handleLogout}
            ?disabled=${this.loading}
          >
            Or click here to logout
          </button>
          <button type="submit" class="btn-primary" ?disabled=${this.loading}>
            ${this.loading ? 'Updating...' : 'Update Settings'}
          </button>
        </div>
      </form>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'user-settings': UserSettings;
  }
}
