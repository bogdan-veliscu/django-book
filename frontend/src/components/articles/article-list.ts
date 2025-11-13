import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import type { Article } from '@/types/models';
import './article-preview';

@customElement('article-list')
export class ArticleList extends LitElement {
  @property({ type: Array }) articles: Article[] = [];
  @property({ type: Boolean }) loading = false;
  @property({ type: Number }) articlesCount = 0;
  @property({ type: Number }) currentPage = 1;
  @property({ type: Number }) pageSize = 10;

  static styles = css`
    :host {
      display: block;
    }

    .loading {
      text-align: center;
      padding: 3rem 1rem;
      color: #5cb85c;
      font-size: 1.2rem;
    }

    .empty {
      text-align: center;
      padding: 3rem 1rem;
      color: #999;
    }

    .empty-title {
      font-size: 1.5rem;
      margin: 0 0 0.5rem 0;
    }

    .empty-text {
      margin: 0;
    }

    .pagination {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 0.5rem;
      margin-top: 2rem;
      padding: 1rem 0;
    }

    .page-btn {
      border: 1px solid #5cb85c;
      background: white;
      color: #5cb85c;
      padding: 0.5rem 1rem;
      border-radius: 0.25rem;
      cursor: pointer;
      font-size: 0.9rem;
      transition: all 0.2s;
      min-width: 40px;
    }

    .page-btn:hover:not(:disabled) {
      background: #5cb85c;
      color: white;
    }

    .page-btn:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }

    .page-btn.active {
      background: #5cb85c;
      color: white;
    }

    .page-info {
      color: #999;
      font-size: 0.9rem;
      padding: 0 0.5rem;
    }
  `;

  get totalPages(): number {
    return Math.ceil(this.articlesCount / this.pageSize);
  }

  private handlePageChange(page: number): void {
    if (page < 1 || page > this.totalPages || page === this.currentPage) {
      return;
    }

    this.dispatchEvent(
      new CustomEvent('page-change', {
        detail: { page, offset: (page - 1) * this.pageSize },
        bubbles: true,
        composed: true,
      })
    );
  }

  private handleArticleUpdated(e: CustomEvent): void {
    // Forward the event up
    this.dispatchEvent(
      new CustomEvent('article-updated', {
        detail: e.detail,
        bubbles: true,
        composed: true,
      })
    );
  }

  private renderPagination() {
    if (this.totalPages <= 1) {
      return null;
    }

    const pages: number[] = [];
    const maxVisiblePages = 5;
    let startPage = Math.max(1, this.currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(this.totalPages, startPage + maxVisiblePages - 1);

    if (endPage - startPage < maxVisiblePages - 1) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }

    return html`
      <div class="pagination">
        <button
          class="page-btn"
          @click=${() => this.handlePageChange(this.currentPage - 1)}
          ?disabled=${this.currentPage === 1 || this.loading}
        >
          ‹
        </button>

        ${pages.map(
          (page) => html`
            <button
              class="page-btn ${page === this.currentPage ? 'active' : ''}"
              @click=${() => this.handlePageChange(page)}
              ?disabled=${this.loading}
            >
              ${page}
            </button>
          `
        )}

        <button
          class="page-btn"
          @click=${() => this.handlePageChange(this.currentPage + 1)}
          ?disabled=${this.currentPage === this.totalPages || this.loading}
        >
          ›
        </button>
      </div>
    `;
  }

  render() {
    if (this.loading) {
      return html`<div class="loading">Loading articles...</div>`;
    }

    if (this.articles.length === 0) {
      return html`
        <div class="empty">
          <h3 class="empty-title">No articles found</h3>
          <p class="empty-text">Be the first to write an article!</p>
        </div>
      `;
    }

    return html`
      <div class="article-list">
        ${this.articles.map(
          (article) =>
            html`<article-preview
              .article=${article}
              @article-updated=${this.handleArticleUpdated}
            ></article-preview>`
        )}
      </div>
      ${this.renderPagination()}
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'article-list': ArticleList;
  }
}
