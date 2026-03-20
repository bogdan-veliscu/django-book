import { LitElement, html, css } from 'lit';
import { customElement, state, query } from 'lit/decorators.js';
import { authService } from '../../services/auth-service';
import type { ApiError } from '@/types/api';

@customElement('login-form')
export class LoginForm extends LitElement {
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

    input {
      padding: 0.75rem 1rem;
      font-size: 1.25rem;
      border: 1px solid #ccc;
      border-radius: 0.25rem;
      width: 100%;
      box-sizing: border-box;
    }

    input:focus {
      outline: none;
      border-color: #5cb85c;
    }

    button {
      padding: 0.75rem 1.5rem;
      font-size: 1.25rem;
      color: white;
      background-color: #5cb85c;
      border: 1px solid #5cb85c;
      border-radius: 0.3rem;
      cursor: pointer;
      align-self: flex-end;
    }

    button:hover:not(:disabled) {
      background-color: #449d44;
      border-color: #419641;
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

  @query('form')
  private form!: HTMLFormElement;

  private async handleSubmit(e: Event) {
    e.preventDefault();
    this.errors = [];

    const formData = new FormData(this.form);
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;

    // Client-side validation
    const validationErrors: string[] = [];

    if (!email || !email.trim()) {
      validationErrors.push('Email is required');
    } else if (!this.isValidEmail(email)) {
      validationErrors.push('Email must be a valid email address');
    }

    if (!password || !password.trim()) {
      validationErrors.push('Password is required');
    }

    if (validationErrors.length > 0) {
      this.errors = validationErrors;
      return;
    }

    this.loading = true;

    try {
      await authService.login({ email, password });

      // Dispatch custom event for successful login
      this.dispatchEvent(
        new CustomEvent('login-success', {
          bubbles: true,
          composed: true,
        })
      );

      // Redirect to home page
      window.location.href = '/';
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
        this.errors = [error.message || 'Login failed. Please try again.'];
      }
    }
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  render() {
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
          type="email"
          name="email"
          placeholder="Email"
          ?disabled=${this.loading}
          required
        />
        <input
          type="password"
          name="password"
          placeholder="Password"
          ?disabled=${this.loading}
          required
        />
        <button type="submit" ?disabled=${this.loading}>
          ${this.loading ? 'Signing in...' : 'Sign in'}
        </button>
      </form>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'login-form': LoginForm;
  }
}
