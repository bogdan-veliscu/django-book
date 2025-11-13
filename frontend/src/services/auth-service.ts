import { authApi } from './api/auth';
import type { User, LoginCredentials, RegisterCredentials, UpdateUser } from '@/types/models';

class AuthService {
  private currentUser: User | null = null;
  private listeners: Array<(user: User | null) => void> = [];

  constructor() {
    this.loadUserFromStorage();
  }

  private loadUserFromStorage(): void {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');

    if (token && userData) {
      try {
        this.currentUser = JSON.parse(userData);
      } catch {
        this.clearAuth();
      }
    }
  }

  private saveUserToStorage(user: User): void {
    localStorage.setItem('token', user.token);
    localStorage.setItem('user', JSON.stringify(user));
  }

  private clearAuth(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    this.currentUser = null;
  }

  private notifyListeners(): void {
    this.listeners.forEach((listener) => listener(this.currentUser));
  }

  subscribe(listener: (user: User | null) => void): () => void {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== listener);
    };
  }

  getUser(): User | null {
    return this.currentUser;
  }

  isAuthenticated(): boolean {
    return this.currentUser !== null;
  }

  async login(credentials: LoginCredentials): Promise<User> {
    const { user } = await authApi.login(credentials);
    this.currentUser = user;
    this.saveUserToStorage(user);
    this.notifyListeners();
    return user;
  }

  async register(credentials: RegisterCredentials): Promise<User> {
    const { user } = await authApi.register(credentials);
    this.currentUser = user;
    this.saveUserToStorage(user);
    this.notifyListeners();
    return user;
  }

  async updateUser(updates: UpdateUser): Promise<User> {
    const { user } = await authApi.updateUser(updates);
    this.currentUser = user;
    this.saveUserToStorage(user);
    this.notifyListeners();
    return user;
  }

  async refreshUser(): Promise<User | null> {
    if (!this.isAuthenticated()) {
      return null;
    }

    try {
      const { user } = await authApi.getCurrentUser();
      this.currentUser = user;
      this.saveUserToStorage(user);
      this.notifyListeners();
      return user;
    } catch {
      this.logout();
      return null;
    }
  }

  logout(): void {
    this.clearAuth();
    this.notifyListeners();
    window.location.href = '/';
  }
}

export const authService = new AuthService();
