import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { Router } from '@vaadin/router';
import type { Article } from '@/types/models';
import { articlesApi } from '@services/api/articles';
import { authService } from '@services/auth-service';

@customElement('article-meta')
export class ArticleMeta extends LitElement {
  @property({ type: Object }) article!: Article;
  @property({ type: Boolean }) canModify = false;

  static styles = css`
    :host {
      display: block;
    }

    .article-meta {
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .author-info {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      cursor: pointer;
      text-decoration: none;
      flex: 1;
    }

    .author-image {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      object-fit: cover;
    }

    .info {
      display: flex;
      flex-direction: column;
    }

    .author-name {
      color: #5cb85c;
      font-weight: 500;
      font-size: 0.9rem;
    }

    .date {
      color: #bbb;
      font-size: 0.8rem;
    }

    .actions {
      display: flex;
      gap: 0.5rem;
    }

    button {
      border: 1px solid;
      background: transparent;
      padding: 0.25rem 0.75rem;
      font-size: 0.85rem;
      border-radius: 0.2rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transition: all 0.2s;
      font-family: inherit;
    }

    button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .follow-btn {
      border-color: #ccc;
      color: #999;
    }

    .follow-btn:hover:not(:disabled) {
      background: #999;
      color: white;
    }

    .follow-btn.following {
      background: #999;
      color: white;
    }

    .favorite-btn {
      border-color: #5cb85c;
      color: #5cb85c;
    }

    .favorite-btn:hover:not(:disabled) {
      background: #5cb85c;
      color: white;
    }

    .favorite-btn.favorited {
      background: #5cb85c;
      color: white;
    }

    .edit-btn {
      border-color: #999;
      color: #999;
    }

    .edit-btn:hover:not(:disabled) {
      background: #999;
      color: white;
    }

    .delete-btn {
      border-color: #b85c5c;
      color: #b85c5c;
    }

    .delete-btn:hover:not(:disabled) {
      background: #b85c5c;
      color: white;
    }
  `;

  connectedCallback(): void {
    super.connectedCallback();
    this.updateCanModify();
  }

  updated(changedProperties: Map<string, any>): void {
    if (changedProperties.has('article')) {
      this.updateCanModify();
    }
  }

  private updateCanModify(): void {
    const currentUser = authService.getUser();
    this.canModify =
      currentUser !== null && currentUser.username === this.article.author.username;
  }

  private formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  }

  private handleAuthorClick(): void {
    Router.go(`/profile/${this.article.author.username}`);
  }

  private async handleFollow(): Promise<void> {
    if (!authService.isAuthenticated()) {
      Router.go('/login');
      return;
    }

    // Dispatch event to parent component to handle follow/unfollow
    this.dispatchEvent(
      new CustomEvent('follow-author', {
        detail: { username: this.article.author.username, following: this.article.author.following },
        bubbles: true,
        composed: true,
      })
    );
  }

  private async handleFavorite(): Promise<void> {
    if (!authService.isAuthenticated()) {
      Router.go('/login');
      return;
    }

    try {
      const response = this.article.favorited
        ? await articlesApi.unfavoriteArticle(this.article.slug)
        : await articlesApi.favoriteArticle(this.article.slug);

      this.article = response.article;
      this.requestUpdate();

      this.dispatchEvent(
        new CustomEvent('article-updated', {
          detail: { article: this.article },
          bubbles: true,
          composed: true,
        })
      );
    } catch (error) {
      console.error('Error toggling favorite:', error);
    }
  }

  private handleEdit(): void {
    Router.go(`/editor/${this.article.slug}`);
  }

  private async handleDelete(): Promise<void> {
    if (!confirm('Are you sure you want to delete this article?')) {
      return;
    }

    try {
      await articlesApi.deleteArticle(this.article.slug);
      this.dispatchEvent(
        new CustomEvent('article-deleted', {
          detail: { slug: this.article.slug },
          bubbles: true,
          composed: true,
        })
      );
      Router.go('/');
    } catch (error) {
      console.error('Error deleting article:', error);
    }
  }

  render() {
    const isAuthenticated = authService.isAuthenticated();

    return html`
      <div class="article-meta">
        <div class="author-info" @click=${this.handleAuthorClick}>
          <img
            class="author-image"
            src=${this.article.author.image || 'https://api.realworld.io/images/smiley-cyrus.jpeg'}
            alt=${this.article.author.username}
          />
          <div class="info">
            <span class="author-name">${this.article.author.username}</span>
            <span class="date">${this.formatDate(this.article.createdAt)}</span>
          </div>
        </div>

        <div class="actions">
          ${this.canModify
            ? html`
                <button class="edit-btn" @click=${this.handleEdit}>
                  <span>✎</span>
                  <span>Edit Article</span>
                </button>
                <button class="delete-btn" @click=${this.handleDelete}>
                  <span>🗑</span>
                  <span>Delete Article</span>
                </button>
              `
            : html`
                <button
                  class="follow-btn ${this.article.author.following ? 'following' : ''}"
                  @click=${this.handleFollow}
                  ?disabled=${!isAuthenticated}
                >
                  <span>+</span>
                  <span
                    >${this.article.author.following ? 'Unfollow' : 'Follow'}
                    ${this.article.author.username}</span
                  >
                </button>
                <button
                  class="favorite-btn ${this.article.favorited ? 'favorited' : ''}"
                  @click=${this.handleFavorite}
                  ?disabled=${!isAuthenticated}
                >
                  <span>${this.article.favorited ? '♥' : '♡'}</span>
                  <span
                    >${this.article.favorited ? 'Unfavorite' : 'Favorite'} Article
                    (${this.article.favoritesCount})</span
                  >
                </button>
              `}
        </div>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'article-meta': ArticleMeta;
  }
}
