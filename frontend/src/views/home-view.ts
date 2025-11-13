import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import type { Article, ArticleFilters } from '@/types/models';
import { articlesApi } from '@services/api/articles';
import { authService } from '@services/auth-service';
import '@components/articles/article-list';
import '@components/articles/tag-list';

type FeedType = 'global' | 'personal';

@customElement('home-view')
export class HomeView extends LitElement {
  @state() private articles: Article[] = [];
  @state() private articlesCount = 0;
  @state() private loading = true;
  @state() private currentPage = 1;
  @state() private feedType: FeedType = 'global';
  @state() private selectedTag: string | null = null;
  private pageSize = 10;

  static styles = css`
    :host {
      display: block;
    }

    .banner {
      background: #5cb85c;
      color: white;
      padding: 2rem;
      text-align: center;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
    }

    h1 {
      font-size: 3.5rem;
      font-family: 'Titillium Web', serif;
      margin: 0 0 0.5rem 0;
      font-weight: 700;
    }

    .tagline {
      font-size: 1.5rem;
      margin: 0;
    }

    .container {
      max-width: 1140px;
      margin: 2rem auto;
      padding: 0 1rem;
    }

    .main-content {
      display: grid;
      grid-template-columns: 1fr 300px;
      gap: 2rem;
    }

    @media (max-width: 768px) {
      .main-content {
        grid-template-columns: 1fr;
      }

      .sidebar {
        order: -1;
      }
    }

    .feed-toggle {
      border-bottom: 1px solid #e5e5e5;
      margin-bottom: 1rem;
    }

    .feed-tabs {
      display: flex;
      gap: 1rem;
    }

    .feed-tab {
      background: transparent;
      border: none;
      color: #aaa;
      padding: 0.75rem 1rem;
      cursor: pointer;
      font-size: 1rem;
      border-bottom: 2px solid transparent;
      transition: all 0.2s;
      font-family: inherit;
    }

    .feed-tab:hover {
      color: #5cb85c;
    }

    .feed-tab.active {
      color: #5cb85c;
      border-bottom-color: #5cb85c;
    }

    .sidebar {
      position: sticky;
      top: 1rem;
      align-self: start;
    }

    .error {
      background: #f3f3f3;
      border: 1px solid #b85c5c;
      color: #b85c5c;
      padding: 1rem;
      border-radius: 0.25rem;
      margin-bottom: 1rem;
    }
  `;

  connectedCallback(): void {
    super.connectedCallback();
    this.parseUrlParams();
    this.loadArticles();

    // Listen for auth changes
    authService.subscribe(() => {
      this.requestUpdate();
    });
  }

  private parseUrlParams(): void {
    const params = new URLSearchParams(window.location.search);
    const tag = params.get('tag');
    if (tag) {
      this.selectedTag = tag;
      this.feedType = 'global';
    }
  }

  private async loadArticles(): Promise<void> {
    this.loading = true;

    try {
      const offset = (this.currentPage - 1) * this.pageSize;

      let response;
      if (this.feedType === 'personal' && authService.isAuthenticated()) {
        response = await articlesApi.getFeed(this.pageSize, offset);
      } else {
        const filters: ArticleFilters = {
          limit: this.pageSize,
          offset,
        };

        if (this.selectedTag) {
          filters.tag = this.selectedTag;
        }

        response = await articlesApi.getArticles(filters);
      }

      this.articles = response.articles;
      this.articlesCount = response.articlesCount;
    } catch (error) {
      console.error('Error loading articles:', error);
      this.articles = [];
      this.articlesCount = 0;
    } finally {
      this.loading = false;
    }
  }

  private handleFeedChange(feedType: FeedType): void {
    if (!authService.isAuthenticated() && feedType === 'personal') {
      return;
    }

    this.feedType = feedType;
    this.selectedTag = null;
    this.currentPage = 1;
    this.loadArticles();

    // Update URL
    window.history.pushState({}, '', '/');
  }

  private handlePageChange(e: CustomEvent): void {
    this.currentPage = e.detail.page;
    this.loadArticles();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  private handleArticleUpdated(e: CustomEvent): void {
    // Update the article in the list
    const updatedArticle = e.detail.article;
    const index = this.articles.findIndex((a) => a.slug === updatedArticle.slug);
    if (index !== -1) {
      this.articles[index] = updatedArticle;
      this.requestUpdate();
    }
  }

  render() {
    const isAuthenticated = authService.isAuthenticated();

    return html`
      <div class="banner">
        <div class="container">
          <h1>conduit</h1>
          <p class="tagline">A place to share your knowledge.</p>
        </div>
      </div>

      <div class="container">
        <div class="main-content">
          <div class="feed-section">
            <div class="feed-toggle">
              <div class="feed-tabs">
                ${isAuthenticated
                  ? html`
                      <button
                        class="feed-tab ${this.feedType === 'personal' ? 'active' : ''}"
                        @click=${() => this.handleFeedChange('personal')}
                      >
                        Your Feed
                      </button>
                    `
                  : null}
                <button
                  class="feed-tab ${this.feedType === 'global' && !this.selectedTag
                    ? 'active'
                    : ''}"
                  @click=${() => this.handleFeedChange('global')}
                >
                  Global Feed
                </button>
                ${this.selectedTag
                  ? html`
                      <button class="feed-tab active">
                        <span>#${this.selectedTag}</span>
                      </button>
                    `
                  : null}
              </div>
            </div>

            <article-list
              .articles=${this.articles}
              .loading=${this.loading}
              .articlesCount=${this.articlesCount}
              .currentPage=${this.currentPage}
              .pageSize=${this.pageSize}
              @page-change=${this.handlePageChange}
              @article-updated=${this.handleArticleUpdated}
            ></article-list>
          </div>

          <div class="sidebar">
            <tag-list></tag-list>
          </div>
        </div>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'home-view': HomeView;
  }
}
