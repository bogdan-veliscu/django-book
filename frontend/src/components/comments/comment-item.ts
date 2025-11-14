import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { Router } from '@vaadin/router';
import type { Comment } from '@/types/models';
import { authService } from '@services/auth-service';

@customElement('comment-item')
export class CommentItem extends LitElement {
  @property({ type: Object }) comment!: Comment;

  static styles = css`
    :host {
      display: block;
    }

    .comment-card {
      border: 1px solid #e5e5e5;
      border-radius: 0.25rem;
      margin-bottom: 1rem;
    }

    .comment-body {
      padding: 1.25rem;
      font-size: 1rem;
      line-height: 1.5;
      color: #373a3c;
      white-space: pre-wrap;
      word-wrap: break-word;
    }

    .comment-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0.75rem 1.25rem;
      background: #f5f5f5;
      border-top: 1px solid #e5e5e5;
    }

    .comment-author {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .author-image {
      width: 20px;
      height: 20px;
      border-radius: 50%;
      object-fit: cover;
      background: #bbb;
    }

    .author-name {
      color: #5cb85c;
      font-size: 0.875rem;
      cursor: pointer;
      text-decoration: none;
    }

    .author-name:hover {
      text-decoration: underline;
    }

    .comment-date {
      color: #bbb;
      font-size: 0.75rem;
      margin-left: 0.5rem;
    }

    .delete-button {
      background: transparent;
      border: none;
      color: #b85c5c;
      cursor: pointer;
      font-size: 0.875rem;
      padding: 0.25rem 0.5rem;
      transition: opacity 0.2s;
    }

    .delete-button:hover {
      opacity: 0.7;
    }

    .delete-button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  `;

  private formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  }

  private handleAuthorClick(): void {
    Router.go(`/profile/${this.comment.author.username}`);
  }

  private handleDelete(): void {
    this.dispatchEvent(
      new CustomEvent('comment-deleted', {
        detail: { commentId: this.comment.id },
        bubbles: true,
        composed: true,
      })
    );
  }

  private canDelete(): boolean {
    const currentUser = authService.getUser();
    return currentUser?.username === this.comment.author.username;
  }

  render() {
    const imageUrl = this.comment.author.image || 'https://api.realworld.io/images/smiley-cyrus.jpeg';

    return html`
      <div class="comment-card">
        <div class="comment-body">${this.comment.body}</div>
        <div class="comment-footer">
          <div class="comment-author">
            <img
              src="${imageUrl}"
              alt="${this.comment.author.username}"
              class="author-image"
            />
            <span
              class="author-name"
              @click=${this.handleAuthorClick}
            >
              ${this.comment.author.username}
            </span>
            <span class="comment-date">
              ${this.formatDate(this.comment.createdAt)}
            </span>
          </div>
          ${this.canDelete()
            ? html`
                <button
                  class="delete-button"
                  @click=${this.handleDelete}
                  title="Delete comment"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                  </svg>
                </button>
              `
            : null}
        </div>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'comment-item': CommentItem;
  }
}
