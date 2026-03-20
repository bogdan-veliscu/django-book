import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { Router } from '@vaadin/router';
import { authService } from '../services/auth-service';
import { articlesApi } from '@services/api/articles';
import type { Article } from '@/types/models';
import '@components/articles/article-editor';

@customElement('editor-view')
export class EditorView extends LitElement {
  static styles = css`
    :host {
      display: block;
    }

    .loading,
    .error {
      max-width: 800px;
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
  `;

  @state()
  private article: Article | null = null;

  @state()
  private loading = false;

  @state()
  private error: string | null = null;

  @state()
  private slug: string | null = null;

  @state()
  private isAuthenticated = false;

  private unsubscribe?: () => void;

  connectedCallback(): void {
    super.connectedCallback();

    // Check authentication
    this.isAuthenticated = authService.isAuthenticated();

    if (!this.isAuthenticated) {
      Router.go('/login');
      return;
    }

    // Subscribe to auth changes
    this.unsubscribe = authService.subscribe((user) => {
      this.isAuthenticated = user !== null;
      if (!this.isAuthenticated) {
        Router.go('/login');
      }
    });
  }

  disconnectedCallback(): void {
    super.disconnectedCallback();
    if (this.unsubscribe) {
      this.unsubscribe();
    }
  }

  onBeforeEnter(location: any): void {
    // Get slug from URL parameter (if editing)
    this.slug = location.params.slug || null;

    if (this.slug) {
      this.loadArticle();
    }
  }

  private async loadArticle(): Promise<void> {
    if (!this.slug) {
      return;
    }

    this.loading = true;
    this.error = null;

    try {
      const response = await articlesApi.getArticle(this.slug);
      const currentUser = authService.getUser();

      // Check if the current user is the author
      if (currentUser && response.article.author.username !== currentUser.username) {
        this.error = 'You can only edit your own articles';
        this.article = null;
      } else {
        this.article = response.article;
      }
    } catch (error: any) {
      console.error('Error loading article:', error);
      this.error = error?.errors?.body?.[0] || 'Failed to load article';
      this.article = null;
    } finally {
      this.loading = false;
    }
  }

  render() {
    if (!this.isAuthenticated) {
      return html`<div class="loading">Redirecting to login...</div>`;
    }

    if (this.loading) {
      return html`<div class="loading">Loading article...</div>`;
    }

    if (this.error) {
      return html`
        <div class="error">
          <h2 class="error-title">Error</h2>
          <p class="error-message">${this.error}</p>
          <a href="/" class="home-link" @click=${(e: Event) => {
            e.preventDefault();
            Router.go('/');
          }}>Go to Home</a>
        </div>
      `;
    }

    return html`
      <article-editor .article=${this.article}></article-editor>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'editor-view': EditorView;
  }
}
