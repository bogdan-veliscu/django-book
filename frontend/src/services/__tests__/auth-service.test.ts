import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock the authApi before importing auth-service (which instantiates the singleton)
vi.mock('../api/auth', () => ({
  authApi: {
    login: vi.fn(),
    register: vi.fn(),
    getCurrentUser: vi.fn(),
    updateUser: vi.fn(),
  },
}));

// Must import after mocking
import { authApi } from '../api/auth';

const mockUser = {
  username: 'testuser',
  email: 'test@example.com',
  token: 'jwt-token-123',
  bio: null,
  image: null,
};

describe('AuthService', () => {
  // Re-import a fresh AuthService class before each test to avoid singleton state pollution
  let AuthServiceClass: typeof import('../auth-service').authService;

  beforeEach(async () => {
    vi.resetModules();
    vi.mock('../api/auth', () => ({
      authApi: {
        login: vi.fn(),
        register: vi.fn(),
        getCurrentUser: vi.fn(),
        updateUser: vi.fn(),
      },
    }));
  });

  describe('initial state', () => {
    it('returns null when no user in localStorage', async () => {
      const { authService } = await import('../auth-service');
      expect(authService.getUser()).toBeNull();
      expect(authService.isAuthenticated()).toBe(false);
    });

    it('loads user from localStorage on construction', async () => {
      localStorage.setItem('token', mockUser.token);
      localStorage.setItem('user', JSON.stringify(mockUser));

      const { authService } = await import('../auth-service');
      expect(authService.getUser()).toEqual(mockUser);
      expect(authService.isAuthenticated()).toBe(true);
    });

    it('clears auth when stored user JSON is invalid', async () => {
      localStorage.setItem('token', 'some-token');
      localStorage.setItem('user', 'not-valid-json{{{');

      const { authService } = await import('../auth-service');
      expect(authService.getUser()).toBeNull();
      expect(localStorage.getItem('token')).toBeNull();
    });
  });

  describe('login', () => {
    it('stores user and token after successful login', async () => {
      vi.mocked(authApi.login).mockResolvedValue({ user: mockUser });

      const { authService } = await import('../auth-service');
      const result = await authService.login({ email: mockUser.email, password: 'password' });

      expect(result).toEqual(mockUser);
      expect(authService.getUser()).toEqual(mockUser);
      expect(authService.isAuthenticated()).toBe(true);
      expect(localStorage.getItem('token')).toBe(mockUser.token);
    });

    it('notifies subscribers after login', async () => {
      vi.mocked(authApi.login).mockResolvedValue({ user: mockUser });

      const { authService } = await import('../auth-service');
      const listener = vi.fn();
      authService.subscribe(listener);

      await authService.login({ email: mockUser.email, password: 'password' });

      expect(listener).toHaveBeenCalledWith(mockUser);
    });

    it('propagates errors from API', async () => {
      const error = { errors: { 'email or password': ['is invalid'] } };
      vi.mocked(authApi.login).mockRejectedValue(error);

      const { authService } = await import('../auth-service');
      await expect(authService.login({ email: 'x@x.com', password: 'wrong' })).rejects.toEqual(error);
      expect(authService.getUser()).toBeNull();
    });
  });

  describe('register', () => {
    it('stores user and token after successful registration', async () => {
      vi.mocked(authApi.register).mockResolvedValue({ user: mockUser });

      const { authService } = await import('../auth-service');
      const result = await authService.register({
        username: mockUser.username,
        email: mockUser.email,
        password: 'Password123',
      });

      expect(result).toEqual(mockUser);
      expect(authService.isAuthenticated()).toBe(true);
    });

    it('notifies subscribers after registration', async () => {
      vi.mocked(authApi.register).mockResolvedValue({ user: mockUser });

      const { authService } = await import('../auth-service');
      const listener = vi.fn();
      authService.subscribe(listener);

      await authService.register({ username: 'u', email: 'e@e.com', password: 'p' });

      expect(listener).toHaveBeenCalledWith(mockUser);
    });
  });

  describe('updateUser', () => {
    it('updates stored user after successful update', async () => {
      const updatedUser = { ...mockUser, bio: 'New bio', image: 'https://img.com/x.png' };
      vi.mocked(authApi.updateUser).mockResolvedValue({ user: updatedUser });

      localStorage.setItem('token', mockUser.token);
      localStorage.setItem('user', JSON.stringify(mockUser));

      const { authService } = await import('../auth-service');
      const result = await authService.updateUser({ bio: 'New bio' });

      expect(result).toEqual(updatedUser);
      expect(authService.getUser()?.bio).toBe('New bio');
    });

    it('notifies subscribers after update', async () => {
      const updatedUser = { ...mockUser, bio: 'Updated' };
      vi.mocked(authApi.updateUser).mockResolvedValue({ user: updatedUser });

      const { authService } = await import('../auth-service');
      const listener = vi.fn();
      authService.subscribe(listener);

      await authService.updateUser({ bio: 'Updated' });

      expect(listener).toHaveBeenCalledWith(updatedUser);
    });
  });

  describe('subscribe/unsubscribe', () => {
    it('returns unsubscribe function that removes listener', async () => {
      vi.mocked(authApi.login).mockResolvedValue({ user: mockUser });

      const { authService } = await import('../auth-service');
      const listener = vi.fn();
      const unsubscribe = authService.subscribe(listener);

      unsubscribe();
      await authService.login({ email: mockUser.email, password: 'p' });

      expect(listener).not.toHaveBeenCalled();
    });

    it('supports multiple subscribers', async () => {
      vi.mocked(authApi.login).mockResolvedValue({ user: mockUser });

      const { authService } = await import('../auth-service');
      const listener1 = vi.fn();
      const listener2 = vi.fn();
      authService.subscribe(listener1);
      authService.subscribe(listener2);

      await authService.login({ email: mockUser.email, password: 'p' });

      expect(listener1).toHaveBeenCalledWith(mockUser);
      expect(listener2).toHaveBeenCalledWith(mockUser);
    });
  });

  describe('refreshUser', () => {
    it('returns null when not authenticated', async () => {
      const { authService } = await import('../auth-service');
      const result = await authService.refreshUser();
      expect(result).toBeNull();
      expect(authApi.getCurrentUser).not.toHaveBeenCalled();
    });

    it('refreshes user data when authenticated', async () => {
      const refreshedUser = { ...mockUser, bio: 'Refreshed' };
      vi.mocked(authApi.getCurrentUser).mockResolvedValue({ user: refreshedUser });

      localStorage.setItem('token', mockUser.token);
      localStorage.setItem('user', JSON.stringify(mockUser));

      const { authService } = await import('../auth-service');
      const result = await authService.refreshUser();

      expect(result).toEqual(refreshedUser);
      expect(authService.getUser()).toEqual(refreshedUser);
    });

    it('logs out when refresh fails', async () => {
      vi.mocked(authApi.getCurrentUser).mockRejectedValue(new Error('Unauthorized'));

      localStorage.setItem('token', mockUser.token);
      localStorage.setItem('user', JSON.stringify(mockUser));

      const { authService } = await import('../auth-service');
      // Prevent window.location redirect in test
      vi.stubGlobal('window', { location: { href: '' } });

      const result = await authService.refreshUser();

      expect(result).toBeNull();
    });
  });
});
