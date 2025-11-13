import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { Router } from '@vaadin/router';
import { articlesApi } from '@services/api/articles';

@customElement('tag-list')
export class TagList extends LitElement {
  @state() private tags: string[] = [];
  @state() private loading = true;
  @state() private error: string | null = null;

  static styles = css`
    :host {
      display: block;
    }

    .tag-list-container {
      background: #f3f3f3;
      padding: 1rem;
      border-radius: 0.25rem;
    }

    .title {
      margin: 0 0 0.5rem 0;
      font-size: 1rem;
      color: #373a3c;
    }

    .loading {
      color: #999;
      font-size: 0.9rem;
      padding: 0.5rem 0;
    }

    .error {
      color: #b85c5c;
      font-size: 0.9rem;
      padding: 0.5rem 0;
    }

    .tag-list {
      display: flex;
      flex-wrap: wrap;
      gap: 0.25rem;
    }

    .tag {
      background: #818a91;
      color: white;
      padding: 0.25rem 0.75rem;
      font-size: 0.8rem;
      border-radius: 0.75rem;
      cursor: pointer;
      transition: all 0.2s;
      border: none;
      font-family: inherit;
    }

    .tag:hover {
      background: #687077;
    }

    .empty {
      color: #999;
      font-size: 0.9rem;
      padding: 0.5rem 0;
    }
  `;

  connectedCallback(): void {
    super.connectedCallback();
    this.loadTags();
  }

  private async loadTags(): Promise<void> {
    this.loading = true;
    this.error = null;

    try {
      const response = await articlesApi.getTags();
      this.tags = response.tags;
    } catch (error) {
      console.error('Error loading tags:', error);
      this.error = 'Failed to load tags';
    } finally {
      this.loading = false;
    }
  }

  private handleTagClick(tag: string): void {
    Router.go(`/?tag=${encodeURIComponent(tag)}`);
  }

  render() {
    return html`
      <div class="tag-list-container">
        <p class="title">Popular Tags</p>

        ${this.loading
          ? html`<div class="loading">Loading tags...</div>`
          : this.error
          ? html`<div class="error">${this.error}</div>`
          : this.tags.length === 0
          ? html`<div class="empty">No tags yet</div>`
          : html`
              <div class="tag-list">
                ${this.tags.map(
                  (tag) =>
                    html`<button class="tag" @click=${() => this.handleTagClick(tag)}>
                      ${tag}
                    </button>`
                )}
              </div>
            `}
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'tag-list': TagList;
  }
}
