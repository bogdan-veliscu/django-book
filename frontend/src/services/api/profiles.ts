import { apiClient } from './client';
import type { ProfileResponse, ApiError } from '@/types/api';

export const profilesApi = {
  async getProfile(username: string): Promise<ProfileResponse> {
    try {
      return await apiClient.get<ProfileResponse>(`/profiles/${username}`);
    } catch (error) {
      throw error as ApiError;
    }
  },

  async followUser(username: string): Promise<ProfileResponse> {
    try {
      return await apiClient.post<ProfileResponse>(`/profiles/${username}/follow`);
    } catch (error) {
      throw error as ApiError;
    }
  },

  async unfollowUser(username: string): Promise<ProfileResponse> {
    try {
      return await apiClient.delete<ProfileResponse>(`/profiles/${username}/follow`);
    } catch (error) {
      throw error as ApiError;
    }
  },
};
