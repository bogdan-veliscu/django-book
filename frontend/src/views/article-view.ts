import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { Router } from '@vaadin/router';
import type { Article } from '@/types/models';
import { articlesApi } from '@services/api/articles';
import { profilesApi } from '@services/api/profiles';
import '@components/articles/article-detail';

@customElement('article-view')
export class ArticleView extends LitElement {
  @state() private article: Article | null = null;
  @state() private loading = true;
  @state() private error: string | null = null;
  @state() private slug = '';

  static styles = css`
    :host {
      display: block;
    }

    .loading,
    .error {
      max-width: 1140px;
      margin: 4rem auto;
      padding: 2rem 1rem;
      text-align: center;
    }

    .loading {
      color: #5cb85c;
      font-size: 1.2rem;
    }

    .error {
      color: #b85c5c;
      font-size: 1rem;
    }

    .error-title {
      font-size: 1.5rem;
      margin: 0 0 1rem 0;
    }

    .error-message {
      margin: 0 0 1.5rem 0;
    }

    .home-link {
      color: #5cb85c;
      text-decoration: none;
      font-weight: 500;
    }

    .home-link:hover {
      text-decoration: underline;
    }

    .comments-placeholder {
      max-width: 1140px;
      margin: 0 auto 2rem;
      padding: 2rem 1rem;
      background: #f9f9f9;
      border-radius: 0.25rem;
      text-align: center;
      color: #999;
    }
  `;

  onBeforeEnter(location: any): void {
    this.slug = location.params.slug;
    this.loadArticle();
  }

  private async loadArticle(): Promise<void> {
    if (!this.slug) {
      this.error = 'No article slug provided';
      this.loading = false;
      return;
    }

    this.loading = true;
    this.error = null;

    try {
      const response = await articlesApi.getArticle(this.slug);
      this.article = response.article;
    } catch (error: any) {
      console.error('Error loading article:', error);
      this.error = error?.errors?.body?.[0] || 'Failed to load article';
      this.article = null;
    } finally {
      this.loading = false;
    }
  }

  private handleArticleUpdated(e: CustomEvent): void {
    if (this.article) {
      this.article = e.detail.article;
      this.requestUpdate();
    }
  }

  private async handleFollowAuthor(e: CustomEvent): Promise<void> {
    const { username, following } = e.detail;

    try {
      const response = following
        ? await profilesApi.unfollowUser(username)
        : await profilesApi.followUser(username);

      // Update the article with the new profile following status
      if (this.article) {
        this.article = {
          ...this.article,
          author: response.profile,
        };
        this.requestUpdate();
      }
    } catch (error) {
      console.error('Error following/unfollowing author:', error);
      // Reload the article to ensure consistency
      await this.loadArticle();
    }
  }

  private handleArticleDeleted(): void {
    // Article was deleted, redirect to home
    Router.go('/');
  }

  render() {
    if (this.loading) {
      return html`<div class="loading">Loading article...</div>`;
    }

    if (this.error || !this.article) {
      return html`
        <div class="error">
          <h2 class="error-title">Article Not Found</h2>
          <p class="error-message">${this.error || 'The article you are looking for does not exist.'}</p>
          <a href="/" class="home-link" @click=${(e: Event) => {
            e.preventDefault();
            Router.go('/');
          }}>Go to Home</a>
        </div>
      `;
    }

    return html`
      <article-detail
        .article=${this.article}
        @article-updated=${this.handleArticleUpdated}
        @follow-author=${this.handleFollowAuthor}
        @article-deleted=${this.handleArticleDeleted}
      ></article-detail>

      <div class="comments-placeholder">
        <p>Comments section coming soon...</p>
      </div>
    `;
  }
}
