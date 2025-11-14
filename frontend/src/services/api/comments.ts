import { apiClient } from './client';
import type {
  CommentResponse,
  MultipleCommentsResponse,
  ApiError,
} from '@/types/api';

export const commentsApi = {
  async getComments(slug: string): Promise<MultipleCommentsResponse> {
    try {
      return await apiClient.get<MultipleCommentsResponse>(
        `/articles/${slug}/comments`
      );
    } catch (error) {
      throw error as ApiError;
    }
  },

  async createComment(slug: string, body: string): Promise<CommentResponse> {
    try {
      return await apiClient.post<CommentResponse>(
        `/articles/${slug}/comments`,
        { comment: { body } }
      );
    } catch (error) {
      throw error as ApiError;
    }
  },

  async deleteComment(slug: string, commentId: number): Promise<void> {
    try {
      await apiClient.delete(`/articles/${slug}/comments/${commentId}`);
    } catch (error) {
      throw error as ApiError;
    }
  },
};
