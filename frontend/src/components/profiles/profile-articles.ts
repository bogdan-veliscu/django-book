import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import type { Article } from '@/types/models';
import { articlesApi } from '@services/api/articles';
import '../articles/article-preview';

type TabType = 'author' | 'favorited';

@customElement('profile-articles')
export class ProfileArticles extends LitElement {
  @property({ type: String }) username!: string;

  @state() private activeTab: TabType = 'author';
  @state() private articles: Article[] = [];
  @state() private articlesCount = 0;
  @state() private isLoading = false;
  @state() private error: string | null = null;
  @state() private currentPage = 0;

  private readonly articlesPerPage = 10;

  static styles = css`
    :host {
      display: block;
    }

    .container {
      max-width: 1140px;
      margin: 0 auto;
      padding: 0 15px;
    }

    .tabs {
      display: flex;
      border-bottom: 1px solid #e5e5e5;
      margin-bottom: 1.5rem;
    }

    .tab {
      background: transparent;
      border: none;
      padding: 0.75rem 1rem;
      cursor: pointer;
      color: #aaa;
      font-size: 1rem;
      transition: color 0.2s;
      border-bottom: 2px solid transparent;
    }

    .tab:hover {
      color: #5cb85c;
    }

    .tab.active {
      color: #5cb85c;
      border-bottom-color: #5cb85c;
    }

    .articles-list {
      min-height: 200px;
    }

    .loading,
    .error,
    .empty {
      text-align: center;
      padding: 2rem;
      color: #999;
    }

    .error {
      color: #b85c5c;
    }

    .pagination {
      display: flex;
      justify-content: center;
      gap: 0.5rem;
      margin-top: 2rem;
      padding: 1rem 0;
    }

    .page-btn {
      background: white;
      border: 1px solid #ddd;
      padding: 0.5rem 0.75rem;
      cursor: pointer;
      color: #5cb85c;
      font-size: 0.9rem;
      border-radius: 0.25rem;
      transition: all 0.2s;
    }

    .page-btn:hover:not(:disabled) {
      background: #5cb85c;
      color: white;
      border-color: #5cb85c;
    }

    .page-btn.active {
      background: #5cb85c;
      color: white;
      border-color: #5cb85c;
    }

    .page-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  `;

  connectedCallback(): void {
    super.connectedCallback();
    this.loadArticles();
  }

  willUpdate(changedProperties: Map<string, unknown>): void {
    if (changedProperties.has('username') && this.username) {
      this.currentPage = 0;
      this.loadArticles();
    }
  }

  private async loadArticles(): Promise<void> {
    if (!this.username) return;

    this.isLoading = true;
    this.error = null;

    try {
      const offset = this.currentPage * this.articlesPerPage;
      const filters =
        this.activeTab === 'author'
          ? { author: this.username, limit: this.articlesPerPage, offset }
          : { favorited: this.username, limit: this.articlesPerPage, offset };

      const response = await articlesApi.getArticles(filters);
      this.articles = response.articles;
      this.articlesCount = response.articlesCount;
    } catch (error) {
      console.error('Error loading articles:', error);
      this.error = 'Failed to load articles. Please try again.';
      this.articles = [];
      this.articlesCount = 0;
    } finally {
      this.isLoading = false;
    }
  }

  private handleTabClick(tab: TabType): void {
    if (this.activeTab === tab) return;
    this.activeTab = tab;
    this.currentPage = 0;
    this.loadArticles();
  }

  private handlePageClick(page: number): void {
    if (this.currentPage === page) return;
    this.currentPage = page;
    this.loadArticles();
    // Scroll to top of articles
    this.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  private handleArticleUpdated(e: CustomEvent): void {
    // Update the article in the list when favorited/unfavorited
    const updatedArticle = e.detail.article as Article;
    const index = this.articles.findIndex((a) => a.slug === updatedArticle.slug);
    if (index !== -1) {
      this.articles[index] = updatedArticle;
      this.requestUpdate();
    }
  }

  private renderPagination() {
    const pageCount = Math.ceil(this.articlesCount / this.articlesPerPage);

    if (pageCount <= 1) return '';

    return html`
      <div class="pagination">
        ${Array.from({ length: pageCount }, (_, i) => i).map(
          (page) => html`
            <button
              class="page-btn ${page === this.currentPage ? 'active' : ''}"
              @click=${() => this.handlePageClick(page)}
              ?disabled=${this.isLoading}
            >
              ${page + 1}
            </button>
          `
        )}
      </div>
    `;
  }

  private renderContent() {
    if (this.isLoading) {
      return html`<div class="loading">Loading articles...</div>`;
    }

    if (this.error) {
      return html`<div class="error">${this.error}</div>`;
    }

    if (this.articles.length === 0) {
      const message =
        this.activeTab === 'author'
          ? 'No articles are here... yet.'
          : 'No articles favorited yet.';
      return html`<div class="empty">${message}</div>`;
    }

    return html`
      ${this.articles.map(
        (article) =>
          html`<article-preview
            .article=${article}
            @article-updated=${this.handleArticleUpdated}
          ></article-preview>`
      )}
      ${this.renderPagination()}
    `;
  }

  render() {
    return html`
      <div class="container">
        <div class="tabs">
          <button
            class="tab ${this.activeTab === 'author' ? 'active' : ''}"
            @click=${() => this.handleTabClick('author')}
          >
            My Articles
          </button>
          <button
            class="tab ${this.activeTab === 'favorited' ? 'active' : ''}"
            @click=${() => this.handleTabClick('favorited')}
          >
            Favorited Articles
          </button>
        </div>

        <div class="articles-list">${this.renderContent()}</div>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'profile-articles': ProfileArticles;
  }
}
