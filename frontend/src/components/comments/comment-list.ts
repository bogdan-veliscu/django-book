import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { Router } from '@vaadin/router';
import type { Comment } from '@/types/models';
import { commentsApi } from '@services/api/comments';
import { authService } from '@services/auth-service';
import './comment-item';
import './comment-form';

@customElement('comment-list')
export class CommentList extends LitElement {
  @property({ type: String }) slug!: string;
  @state() private comments: Comment[] = [];
  @state() private loading = true;
  @state() private error: string | null = null;

  static styles = css`
    :host {
      display: block;
    }

    .comments-container {
      max-width: 1140px;
      margin: 0 auto 2rem;
      padding: 0 1rem;
    }

    .comments-header {
      font-size: 1.25rem;
      font-weight: 600;
      margin: 0 0 1.5rem 0;
      color: #373a3c;
    }

    .loading-message {
      text-align: center;
      padding: 2rem;
      color: #5cb85c;
      font-size: 1rem;
    }

    .error-message {
      background: #f8d7da;
      color: #721c24;
      padding: 1rem;
      margin-bottom: 1rem;
      border-radius: 0.25rem;
      text-align: center;
    }

    .sign-in-message {
      text-align: center;
      padding: 2rem;
      background: #f5f5f5;
      border: 1px solid #e5e5e5;
      border-radius: 0.25rem;
      margin-bottom: 1rem;
      color: #999;
    }

    .sign-in-link {
      color: #5cb85c;
      text-decoration: none;
      font-weight: 500;
      margin: 0 0.25rem;
    }

    .sign-in-link:hover {
      text-decoration: underline;
    }

    .empty-message {
      text-align: center;
      padding: 2rem;
      color: #999;
      font-size: 1rem;
    }

    .comments-list {
      margin-top: 1rem;
    }
  `;

  connectedCallback(): void {
    super.connectedCallback();
    this.loadComments();
  }

  private async loadComments(): Promise<void> {
    if (!this.slug) {
      this.error = 'No article slug provided';
      this.loading = false;
      return;
    }

    this.loading = true;
    this.error = null;

    try {
      const response = await commentsApi.getComments(this.slug);
      this.comments = response.comments;
    } catch (error: any) {
      console.error('Error loading comments:', error);
      this.error = error?.errors?.body?.[0] || 'Failed to load comments';
    } finally {
      this.loading = false;
    }
  }

  private async handleCommentSubmit(e: CustomEvent): Promise<void> {
    const { body } = e.detail;

    try {
      const response = await commentsApi.createComment(this.slug, body);

      // Add the new comment to the beginning of the list
      this.comments = [response.comment, ...this.comments];

      // Dispatch event to notify parent
      this.dispatchEvent(
        new CustomEvent('comment-created', {
          detail: { comment: response.comment },
          bubbles: true,
          composed: true,
        })
      );
    } catch (error: any) {
      console.error('Error creating comment:', error);
      // The form component will handle error display
    }
  }

  private async handleCommentDeleted(e: CustomEvent): Promise<void> {
    const { commentId } = e.detail;

    try {
      await commentsApi.deleteComment(this.slug, commentId);

      // Remove the comment from the list
      this.comments = this.comments.filter((comment) => comment.id !== commentId);

      // Dispatch event to notify parent
      this.dispatchEvent(
        new CustomEvent('comment-deleted', {
          detail: { commentId },
          bubbles: true,
          composed: true,
        })
      );
    } catch (error: any) {
      console.error('Error deleting comment:', error);
      this.error = error?.errors?.body?.[0] || 'Failed to delete comment';
      // Reload comments to ensure consistency
      await this.loadComments();
    }
  }

  private handleSignInClick(e: Event): void {
    e.preventDefault();
    Router.go('/login');
  }

  private handleSignUpClick(e: Event): void {
    e.preventDefault();
    Router.go('/register');
  }

  render() {
    const isAuthenticated = authService.isAuthenticated();

    return html`
      <div class="comments-container">
        ${this.error
          ? html`<div class="error-message">${this.error}</div>`
          : null}

        ${isAuthenticated
          ? html`
              <comment-form
                @comment-submit=${this.handleCommentSubmit}
              ></comment-form>
            `
          : html`
              <div class="sign-in-message">
                <a href="/login" class="sign-in-link" @click=${this.handleSignInClick}>Sign in</a>
                or
                <a href="/register" class="sign-in-link" @click=${this.handleSignUpClick}>sign up</a>
                to add comments on this article.
              </div>
            `}

        ${this.loading
          ? html`<div class="loading-message">Loading comments...</div>`
          : this.comments.length === 0
          ? html`<div class="empty-message">No comments yet.</div>`
          : html`
              <div class="comments-list">
                ${this.comments.map(
                  (comment) => html`
                    <comment-item
                      .comment=${comment}
                      @comment-deleted=${this.handleCommentDeleted}
                    ></comment-item>
                  `
                )}
              </div>
            `}
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'comment-list': CommentList;
  }
}
