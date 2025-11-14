import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { authService } from '@services/auth-service';

@customElement('comment-form')
export class CommentForm extends LitElement {
  @state() private body = '';
  @state() private loading = false;
  @state() private error: string | null = null;

  static styles = css`
    :host {
      display: block;
    }

    .comment-form {
      border: 1px solid #e5e5e5;
      border-radius: 0.25rem;
      margin-bottom: 1rem;
    }

    .form-textarea {
      width: 100%;
      min-height: 100px;
      padding: 1.25rem;
      border: none;
      font-family: inherit;
      font-size: 1rem;
      line-height: 1.5;
      resize: vertical;
      outline: none;
    }

    .form-textarea::placeholder {
      color: #999;
    }

    .form-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0.75rem 1.25rem;
      background: #f5f5f5;
      border-top: 1px solid #e5e5e5;
    }

    .author-image {
      width: 30px;
      height: 30px;
      border-radius: 50%;
      object-fit: cover;
      background: #bbb;
    }

    .submit-button {
      background: #5cb85c;
      color: white;
      border: none;
      padding: 0.5rem 1.25rem;
      font-size: 0.875rem;
      border-radius: 0.25rem;
      cursor: pointer;
      transition: background 0.2s;
    }

    .submit-button:hover:not(:disabled) {
      background: #449d44;
    }

    .submit-button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .error-message {
      background: #f8d7da;
      color: #721c24;
      padding: 0.75rem;
      margin-bottom: 1rem;
      border-radius: 0.25rem;
      font-size: 0.875rem;
    }
  `;

  private handleInput(e: Event): void {
    const textarea = e.target as HTMLTextAreaElement;
    this.body = textarea.value;
  }

  private handleSubmit(e: Event): void {
    e.preventDefault();

    // Validation
    if (!this.body.trim()) {
      this.error = 'Comment body cannot be empty';
      return;
    }

    this.loading = true;
    this.error = null;

    try {
      this.dispatchEvent(
        new CustomEvent('comment-submit', {
          detail: { body: this.body.trim() },
          bubbles: true,
          composed: true,
        })
      );

      // Clear form after successful submission
      this.body = '';
    } catch (error: any) {
      this.error = error?.errors?.body?.[0] || 'Failed to post comment';
    } finally {
      this.loading = false;
    }
  }

  render() {
    const currentUser = authService.getUser();
    const imageUrl = currentUser?.image || 'https://api.realworld.io/images/smiley-cyrus.jpeg';

    return html`
      ${this.error
        ? html`<div class="error-message">${this.error}</div>`
        : null}

      <form class="comment-form" @submit=${this.handleSubmit}>
        <textarea
          class="form-textarea"
          placeholder="Write a comment..."
          .value=${this.body}
          @input=${this.handleInput}
          ?disabled=${this.loading}
        ></textarea>
        <div class="form-footer">
          <img
            src="${imageUrl}"
            alt="${currentUser?.username || 'User'}"
            class="author-image"
          />
          <button
            type="submit"
            class="submit-button"
            ?disabled=${this.loading || !this.body.trim()}
          >
            ${this.loading ? 'Posting...' : 'Post Comment'}
          </button>
        </div>
      </form>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'comment-form': CommentForm;
  }
}
