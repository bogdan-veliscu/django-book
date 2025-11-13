import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { Router } from '@vaadin/router';
import type { Article } from '@/types/models';
import './article-meta';

@customElement('article-detail')
export class ArticleDetail extends LitElement {
  @property({ type: Object }) article!: Article;

  static styles = css`
    :host {
      display: block;
    }

    .article-banner {
      background: #333;
      color: white;
      padding: 2rem 0;
    }

    .banner-content {
      max-width: 1140px;
      margin: 0 auto;
      padding: 0 1rem;
    }

    .article-title {
      font-size: 2.5rem;
      font-weight: 600;
      margin: 0 0 1.5rem 0;
      line-height: 1.2;
    }

    .article-content {
      max-width: 1140px;
      margin: 2rem auto;
      padding: 0 1rem;
    }

    .article-body {
      font-size: 1.125rem;
      line-height: 1.8;
      color: #373a3c;
      margin-bottom: 2rem;
      white-space: pre-wrap;
      word-wrap: break-word;
    }

    .article-body p {
      margin: 0 0 1rem 0;
    }

    .tag-list {
      display: flex;
      flex-wrap: wrap;
      gap: 0.25rem;
      margin-top: 2rem;
      padding-top: 2rem;
      border-top: 1px solid #e5e5e5;
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

    .article-actions {
      display: flex;
      justify-content: center;
      padding: 2rem 0;
      border-bottom: 1px solid #e5e5e5;
    }
  `;

  private handleTagClick(tag: string): void {
    Router.go(`/?tag=${encodeURIComponent(tag)}`);
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

  private handleFollowAuthor(e: CustomEvent): void {
    // Forward the event up
    this.dispatchEvent(
      new CustomEvent('follow-author', {
        detail: e.detail,
        bubbles: true,
        composed: true,
      })
    );
  }

  private handleArticleDeleted(e: CustomEvent): void {
    // Forward the event up
    this.dispatchEvent(
      new CustomEvent('article-deleted', {
        detail: e.detail,
        bubbles: true,
        composed: true,
      })
    );
  }

  render() {
    return html`
      <div class="article-banner">
        <div class="banner-content">
          <h1 class="article-title">${this.article.title}</h1>
          <article-meta
            .article=${this.article}
            @article-updated=${this.handleArticleUpdated}
            @follow-author=${this.handleFollowAuthor}
            @article-deleted=${this.handleArticleDeleted}
          ></article-meta>
        </div>
      </div>

      <div class="article-content">
        <div class="article-body">${this.article.body}</div>

        ${this.article.tagList.length > 0
          ? html`
              <div class="tag-list">
                ${this.article.tagList.map(
                  (tag) =>
                    html`<span class="tag" @click=${() => this.handleTagClick(tag)}>${tag}</span>`
                )}
              </div>
            `
          : null}
      </div>

      <div class="article-actions">
        <article-meta
          .article=${this.article}
          @article-updated=${this.handleArticleUpdated}
          @follow-author=${this.handleFollowAuthor}
          @article-deleted=${this.handleArticleDeleted}
        ></article-meta>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'article-detail': ArticleDetail;
  }
}
