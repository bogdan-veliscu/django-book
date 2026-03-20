import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';

@customElement('loading-spinner')
export class LoadingSpinner extends LitElement {
  static styles = css`
    :host {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 2rem;
    }

    .spinner {
      width: 50px;
      height: 50px;
      border: 4px solid #f3f3f3;
      border-top: 4px solid #5cb85c;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }

    @keyframes spin {
      0% {
        transform: rotate(0deg);
      }
      100% {
        transform: rotate(360deg);
      }
    }

    .message {
      margin-top: 1rem;
      color: #666;
      font-size: 1rem;
      text-align: center;
    }

    .small .spinner {
      width: 30px;
      height: 30px;
      border-width: 3px;
    }

    .small .message {
      font-size: 0.875rem;
      margin-top: 0.5rem;
    }

    .large .spinner {
      width: 70px;
      height: 70px;
      border-width: 5px;
    }

    .large .message {
      font-size: 1.25rem;
      margin-top: 1.5rem;
    }

    .inline {
      display: inline-flex;
      padding: 0;
    }

    .inline .spinner {
      width: 20px;
      height: 20px;
      border-width: 2px;
    }

    .inline .message {
      margin-top: 0;
      margin-left: 0.5rem;
      font-size: 0.875rem;
    }
  `;

  @property({ type: String })
  message?: string;

  @property({ type: String })
  size: 'small' | 'medium' | 'large' = 'medium';

  @property({ type: Boolean })
  inline = false;

  render() {
    const classes = [
      this.size !== 'medium' ? this.size : '',
      this.inline ? 'inline' : '',
    ]
      .filter(Boolean)
      .join(' ');

    return html`
      <div class="${classes}">
        <div class="spinner"></div>
        ${this.message ? html`<div class="message">${this.message}</div>` : ''}
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'loading-spinner': LoadingSpinner;
  }
}
