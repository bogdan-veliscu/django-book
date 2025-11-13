import { LitElement, html, css } from 'lit';
import { customElement, property, state, query } from 'lit/decorators.js';
import { Router } from '@vaadin/router';
import { articlesApi } from '@services/api/articles';
import type { Article, NewArticle, UpdateArticle } from '@/types/models';
import type { ApiError } from '@/types/api';

@customElement('article-editor')
export class ArticleEditor extends LitElement {
  static styles = css`
    :host {
      display: block;
      max-width: 800px;
      margin: 2rem auto;
      padding: 0 1rem;
    }

    h1 {
      text-align: center;
      margin-bottom: 2rem;
      font-size: 2.5rem;
      font-weight: 500;
    }

    .error-messages {
      margin-bottom: 1rem;
      padding: 0.75rem 1rem;
      background-color: #f8d7da;
      border: 1px solid #f5c6cb;
      border-radius: 0.25rem;
      color: #721c24;
    }

    .error-messages ul {
      margin: 0;
      padding-left: 1.5rem;
    }

    .error-messages li {
      margin: 0.25rem 0;
    }

    form {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    input,
    textarea {
      padding: 0.75rem 1rem;
      font-size: 1rem;
      border: 1px solid #ccc;
      border-radius: 0.25rem;
      width: 100%;
      box-sizing: border-box;
      font-family: inherit;
    }

    input::placeholder,
    textarea::placeholder {
      color: #999;
    }

    textarea {
      min-height: 12rem;
      resize: vertical;
    }

    input:focus,
    textarea:focus {
      outline: none;
      border-color: #5cb85c;
    }

    .form-group {
      display: flex;
      flex-direction: column;
    }

    button {
      align-self: flex-end;
      padding: 0.75rem 1.5rem;
      font-size: 1.25rem;
      color: white;
      background-color: #5cb85c;
      border: 1px solid #5cb85c;
      border-radius: 0.3rem;
      cursor: pointer;
    }

    button:hover:not(:disabled) {
      background-color: #449d44;
      border-color: #419641;
    }

    button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  `;

  @property({ type: Object })
  article: Article | null = null;

  @state()
  private loading = false;

  @state()
  private errors: string[] = [];

  @query('form')
  private form!: HTMLFormElement;

  private async handleSubmit(e: Event): Promise<void> {
    e.preventDefault();
    this.errors = [];

    const formData = new FormData(this.form);
    const title = (formData.get('title') as string || '').trim();
    const description = (formData.get('description') as string || '').trim();
    const body = (formData.get('body') as string || '').trim();
    const tagsInput = (formData.get('tags') as string || '').trim();

    // Client-side validation
    const validationErrors: string[] = [];

    if (!title) {
      validationErrors.push('Title is required');
    }

    if (!description) {
      validationErrors.push('Description is required');
    }

    if (!body) {
      validationErrors.push('Body is required');
    }

    if (validationErrors.length > 0) {
      this.errors = validationErrors;
      return;
    }

    // Parse tags (comma-separated)
    const tagList = tagsInput
      ? tagsInput.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0)
      : [];

    this.loading = true;

    try {
      let response;

      if (this.article) {
        // Update existing article
        const updates: UpdateArticle = {
          title,
          description,
          body,
        };
        response = await articlesApi.updateArticle(this.article.slug, updates);
      } else {
        // Create new article
        const newArticle: NewArticle = {
          title,
          description,
          body,
          tagList,
        };
        response = await articlesApi.createArticle(newArticle);
      }

      this.loading = false;

      // Redirect to article detail page
      Router.go(`/article/${response.article.slug}`);
    } catch (error: any) {
      this.loading = false;

      // Handle API errors
      if (error.errors) {
        const apiError = error as ApiError;
        this.errors = Object.entries(apiError.errors).flatMap(
          ([key, messages]) =>
            messages.map((msg) => `${key}: ${msg}`)
        );
      } else {
        this.errors = [error.message || 'Failed to save article. Please try again.'];
      }
    }
  }

  render() {
    const isEditing = this.article !== null;
    const heading = isEditing ? 'Edit Article' : 'New Article';
    const buttonText = isEditing ? 'Update Article' : 'Publish Article';

    return html`
      <h1>${heading}</h1>

      ${this.errors.length > 0
        ? html`
            <div class="error-messages">
              <ul>
                ${this.errors.map((error) => html`<li>${error}</li>`)}
              </ul>
            </div>
          `
        : ''}

      <form @submit=${this.handleSubmit}>
        <div class="form-group">
          <input
            type="text"
            name="title"
            placeholder="Article Title"
            .value=${this.article?.title || ''}
            ?disabled=${this.loading}
            required
          />
        </div>

        <div class="form-group">
          <input
            type="text"
            name="description"
            placeholder="What's this article about?"
            .value=${this.article?.description || ''}
            ?disabled=${this.loading}
            required
          />
        </div>

        <div class="form-group">
          <textarea
            name="body"
            placeholder="Write your article (in markdown)"
            .value=${this.article?.body || ''}
            ?disabled=${this.loading}
            required
          ></textarea>
        </div>

        <div class="form-group">
          <input
            type="text"
            name="tags"
            placeholder="Enter tags (comma separated)"
            .value=${this.article?.tagList?.join(', ') || ''}
            ?disabled=${this.loading || isEditing}
          />
        </div>

        <button type="submit" ?disabled=${this.loading}>
          ${this.loading ? 'Saving...' : buttonText}
        </button>
      </form>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'article-editor': ArticleEditor;
  }
}
