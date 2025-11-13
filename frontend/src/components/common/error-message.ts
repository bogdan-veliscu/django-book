import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';

@customElement('error-message')
export class ErrorMessage extends LitElement {
  static styles = css`
    :host {
      display: block;
    }

    .error-container {
      background-color: #f8d7da;
      border: 1px solid #f5c6cb;
      border-radius: 0.25rem;
      color: #721c24;
      padding: 0.75rem 1rem;
      margin-bottom: 1rem;
      position: relative;
      animation: slideIn 0.3s ease-out;
    }

    @keyframes slideIn {
      from {
        opacity: 0;
        transform: translateY(-10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .error-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 1rem;
    }

    .error-content {
      flex: 1;
    }

    .error-title {
      font-weight: bold;
      margin: 0 0 0.5rem 0;
      font-size: 1rem;
    }

    .error-message {
      margin: 0;
      font-size: 0.875rem;
      line-height: 1.5;
    }

    .error-list {
      margin: 0.5rem 0 0 0;
      padding-left: 1.5rem;
    }

    .error-list li {
      margin: 0.25rem 0;
    }

    .error-actions {
      display: flex;
      gap: 0.5rem;
      margin-top: 0.75rem;
    }

    .dismiss-button,
    .retry-button {
      background: transparent;
      border: none;
      color: #721c24;
      cursor: pointer;
      padding: 0.25rem 0.5rem;
      font-size: 1rem;
      transition: opacity 0.2s;
      display: flex;
      align-items: center;
      gap: 0.25rem;
    }

    .dismiss-button:hover,
    .retry-button:hover {
      opacity: 0.7;
    }

    .dismiss-button {
      position: absolute;
      top: 0.5rem;
      right: 0.5rem;
      padding: 0;
      font-size: 1.25rem;
      line-height: 1;
    }

    .retry-button {
      background-color: #721c24;
      color: white;
      border-radius: 0.25rem;
      padding: 0.5rem 1rem;
      font-size: 0.875rem;
    }

    .retry-button:hover {
      opacity: 0.9;
      background-color: #5a161d;
    }

    .retry-button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    ion-icon {
      font-size: 1.25rem;
    }

    .warning {
      background-color: #fff3cd;
      border-color: #ffeaa7;
      color: #856404;
    }

    .warning .dismiss-button,
    .warning .retry-button {
      color: #856404;
    }

    .warning .retry-button {
      background-color: #856404;
      color: white;
    }

    .info {
      background-color: #d1ecf1;
      border-color: #bee5eb;
      color: #0c5460;
    }

    .info .dismiss-button,
    .info .retry-button {
      color: #0c5460;
    }

    .info .retry-button {
      background-color: #0c5460;
      color: white;
    }
  `;

  @property({ type: String })
  message = 'An error occurred';

  @property({ type: Array })
  errors?: string[];

  @property({ type: String })
  heading?: string;

  @property({ type: Boolean })
  dismissible = false;

  @property({ type: Boolean })
  showRetry = false;

  @property({ type: String })
  retryLabel = 'Retry';

  @property({ type: String })
  variant: 'error' | 'warning' | 'info' = 'error';

  private handleDismiss() {
    this.dispatchEvent(
      new CustomEvent('dismiss', {
        bubbles: true,
        composed: true,
      })
    );
  }

  private handleRetry() {
    this.dispatchEvent(
      new CustomEvent('retry', {
        bubbles: true,
        composed: true,
      })
    );
  }

  render() {
    const variantClass = this.variant !== 'error' ? this.variant : '';

    return html`
      <div class="error-container ${variantClass}">
        <div class="error-header">
          <div class="error-content">
            ${this.heading
              ? html`<h4 class="error-title">${this.heading}</h4>`
              : ''}
            <p class="error-message">${this.message}</p>
            ${this.errors && this.errors.length > 0
              ? html`
                  <ul class="error-list">
                    ${this.errors.map((error) => html`<li>${error}</li>`)}
                  </ul>
                `
              : ''}
            ${this.showRetry
              ? html`
                  <div class="error-actions">
                    <button
                      class="retry-button"
                      @click=${this.handleRetry}
                      aria-label="Retry"
                    >
                      <ion-icon name="refresh-outline"></ion-icon>
                      <span>${this.retryLabel}</span>
                    </button>
                  </div>
                `
              : ''}
          </div>
          ${this.dismissible
            ? html`
                <button
                  class="dismiss-button"
                  @click=${this.handleDismiss}
                  aria-label="Dismiss"
                >
                  <ion-icon name="close-outline"></ion-icon>
                </button>
              `
            : ''}
        </div>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'error-message': ErrorMessage;
  }
}
