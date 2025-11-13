import { apiClient } from './client';
import type {
  ArticleResponse,
  MultipleArticlesResponse,
  TagsResponse,
  ApiError,
} from '@/types/api';
import type {
  NewArticle,
  UpdateArticle,
  ArticleFilters,
} from '@/types/models';

export const articlesApi = {
  async getArticles(filters?: ArticleFilters): Promise<MultipleArticlesResponse> {
    try {
      const params = new URLSearchParams();
      if (filters?.tag) params.append('tag', filters.tag);
      if (filters?.author) params.append('author', filters.author);
      if (filters?.favorited) params.append('favorited', filters.favorited);
      if (filters?.limit) params.append('limit', filters.limit.toString());
      if (filters?.offset) params.append('offset', filters.offset.toString());

      const queryString = params.toString();
      const endpoint = queryString ? `/articles?${queryString}` : '/articles';

      return await apiClient.get<MultipleArticlesResponse>(endpoint);
    } catch (error) {
      throw error as ApiError;
    }
  },

  async getFeed(limit?: number, offset?: number): Promise<MultipleArticlesResponse> {
    try {
      const params = new URLSearchParams();
      if (limit) params.append('limit', limit.toString());
      if (offset) params.append('offset', offset.toString());

      const queryString = params.toString();
      const endpoint = queryString ? `/articles/feed?${queryString}` : '/articles/feed';

      return await apiClient.get<MultipleArticlesResponse>(endpoint);
    } catch (error) {
      throw error as ApiError;
    }
  },

  async getArticle(slug: string): Promise<ArticleResponse> {
    try {
      return await apiClient.get<ArticleResponse>(`/articles/${slug}`);
    } catch (error) {
      throw error as ApiError;
    }
  },

  async createArticle(article: NewArticle): Promise<ArticleResponse> {
    try {
      return await apiClient.post<ArticleResponse>('/articles', {
        article,
      });
    } catch (error) {
      throw error as ApiError;
    }
  },

  async updateArticle(slug: string, article: UpdateArticle): Promise<ArticleResponse> {
    try {
      return await apiClient.put<ArticleResponse>(`/articles/${slug}`, {
        article,
      });
    } catch (error) {
      throw error as ApiError;
    }
  },

  async deleteArticle(slug: string): Promise<void> {
    try {
      await apiClient.delete(`/articles/${slug}`);
    } catch (error) {
      throw error as ApiError;
    }
  },

  async favoriteArticle(slug: string): Promise<ArticleResponse> {
    try {
      return await apiClient.post<ArticleResponse>(`/articles/${slug}/favorite`);
    } catch (error) {
      throw error as ApiError;
    }
  },

  async unfavoriteArticle(slug: string): Promise<ArticleResponse> {
    try {
      return await apiClient.delete<ArticleResponse>(`/articles/${slug}/favorite`);
    } catch (error) {
      throw error as ApiError;
    }
  },

  async getTags(): Promise<TagsResponse> {
    try {
      return await apiClient.get<TagsResponse>('/tags');
    } catch (error) {
      throw error as ApiError;
    }
  },
};
