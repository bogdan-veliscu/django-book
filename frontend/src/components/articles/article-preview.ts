import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { Router } from '@vaadin/router';
import type { Article } from '@/types/models';
import { articlesApi } from '@services/api/articles';
import { authService } from '@services/auth-service';

@customElement('article-preview')
export class ArticlePreview extends LitElement {
  @property({ type: Object }) article!: Article;

  static styles = css`
    :host {
      display: block;
      border-top: 1px solid rgba(0, 0, 0, 0.1);
      padding: 1.5rem 0;
    }

    .article-meta {
      display: flex;
      align-items: center;
      margin-bottom: 1rem;
    }

    .author-info {
      display: flex;
      align-items: center;
      flex: 1;
      cursor: pointer;
    }

    .author-info:hover {
      text-decoration: none;
    }

    .author-image {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      margin-right: 0.5rem;
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

    .favorite-btn {
      border: 1px solid #5cb85c;
      background: transparent;
      color: #5cb85c;
      padding: 0.25rem 0.5rem;
      font-size: 0.8rem;
      border-radius: 0.2rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.25rem;
      transition: all 0.2s;
    }

    .favorite-btn:hover {
      background: #5cb85c;
      color: white;
    }

    .favorite-btn.favorited {
      background: #5cb85c;
      color: white;
    }

    .article-content {
      cursor: pointer;
    }

    .article-content:hover h2 {
      color: #5cb85c;
    }

    h2 {
      font-size: 1.5rem;
      font-weight: 600;
      color: #373a3c;
      margin: 0 0 0.5rem 0;
      transition: color 0.2s;
    }

    .description {
      font-size: 1rem;
      color: #999;
      margin: 0 0 1rem 0;
      line-height: 1.5;
    }

    .read-more {
      color: #bbb;
      font-size: 0.85rem;
      font-weight: 300;
    }

    .tag-list {
      display: flex;
      flex-wrap: wrap;
      gap: 0.25rem;
      margin-top: 0.5rem;
    }

    .tag {
      border: 1px solid #ddd;
      background: transparent;
      color: #aaa;
      padding: 0.125rem 0.5rem;
      font-size: 0.75rem;
      border-radius: 0.75rem;
      cursor: pointer;
      transition: background 0.2s;
    }

    .tag:hover {
      background: #818a91;
      color: white;
      border-color: #818a91;
    }
  `;

  private formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  }

  private async handleFavorite(e: Event): Promise<void> {
    e.stopPropagation();

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

      // Dispatch event to notify parent components
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

  private handleAuthorClick(e: Event): void {
    e.stopPropagation();
    Router.go(`/profile/${this.article.author.username}`);
  }

  private handleArticleClick(): void {
    Router.go(`/article/${this.article.slug}`);
  }

  private handleTagClick(e: Event, tag: string): void {
    e.stopPropagation();
    Router.go(`/?tag=${encodeURIComponent(tag)}`);
  }

  render() {
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
        <button
          class="favorite-btn ${this.article.favorited ? 'favorited' : ''}"
          @click=${this.handleFavorite}
        >
          <span>${this.article.favorited ? '♥' : '♡'}</span>
          <span>${this.article.favoritesCount}</span>
        </button>
      </div>

      <div class="article-content" @click=${this.handleArticleClick}>
        <h2>${this.article.title}</h2>
        <p class="description">${this.article.description}</p>
        <span class="read-more">Read more...</span>
        <div class="tag-list">
          ${this.article.tagList.map(
            (tag) =>
              html`<span class="tag" @click=${(e: Event) => this.handleTagClick(e, tag)}
                >${tag}</span
              >`
          )}
        </div>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'article-preview': ArticlePreview;
  }
}
