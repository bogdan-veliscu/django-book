import { apiClient } from './client';
import type {
  UserResponse,
  ApiError,
} from '@/types/api';
import type {
  LoginCredentials,
  RegisterCredentials,
  UpdateUser,
} from '@/types/models';

export const authApi = {
  async login(credentials: LoginCredentials): Promise<UserResponse> {
    try {
      return await apiClient.post<UserResponse>('/users/login', {
        user: credentials,
      });
    } catch (error) {
      throw error as ApiError;
    }
  },

  async register(credentials: RegisterCredentials): Promise<UserResponse> {
    try {
      return await apiClient.post<UserResponse>('/users', {
        user: credentials,
      });
    } catch (error) {
      throw error as ApiError;
    }
  },

  async getCurrentUser(): Promise<UserResponse> {
    try {
      return await apiClient.get<UserResponse>('/user');
    } catch (error) {
      throw error as ApiError;
    }
  },

  async updateUser(user: UpdateUser): Promise<UserResponse> {
    try {
      return await apiClient.put<UserResponse>('/user', { user });
    } catch (error) {
      throw error as ApiError;
    }
  },
};
