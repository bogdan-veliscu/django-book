import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ApiClient } from '../api/client';

describe('ApiClient', () => {
  let client: ApiClient;

  beforeEach(() => {
    client = new ApiClient('http://test-api');
    vi.stubGlobal('fetch', vi.fn());
  });

  const makeResponse = (body: unknown, status = 200): Response =>
    ({
      ok: status >= 200 && status < 300,
      status,
      json: () => Promise.resolve(body),
    }) as Response;

  describe('GET requests', () => {
    it('sends GET request to correct URL', async () => {
      vi.mocked(fetch).mockResolvedValue(makeResponse({ data: 'test' }));

      await client.get('/users');

      expect(fetch).toHaveBeenCalledWith(
        'http://test-api/users',
        expect.objectContaining({ method: 'GET' })
      );
    });

    it('includes Content-Type header', async () => {
      vi.mocked(fetch).mockResolvedValue(makeResponse({}));

      await client.get('/users');

      const [, options] = vi.mocked(fetch).mock.calls[0];
      const headers = options?.headers as Headers;
      expect(headers.get('Content-Type')).toBe('application/json');
    });

    it('includes Authorization header when token in localStorage', async () => {
      localStorage.setItem('token', 'my-jwt-token');
      vi.mocked(fetch).mockResolvedValue(makeResponse({}));

      await client.get('/user');

      const [, options] = vi.mocked(fetch).mock.calls[0];
      const headers = options?.headers as Headers;
      expect(headers.get('Authorization')).toBe('Bearer my-jwt-token');
    });

    it('omits Authorization header when no token', async () => {
      vi.mocked(fetch).mockResolvedValue(makeResponse({}));

      await client.get('/articles');

      const [, options] = vi.mocked(fetch).mock.calls[0];
      const headers = options?.headers as Headers;
      expect(headers.get('Authorization')).toBeNull();
    });

    it('uses token from options over localStorage', async () => {
      localStorage.setItem('token', 'storage-token');
      vi.mocked(fetch).mockResolvedValue(makeResponse({}));

      await client.get('/user', { token: 'options-token' });

      const [, options] = vi.mocked(fetch).mock.calls[0];
      const headers = options?.headers as Headers;
      expect(headers.get('Authorization')).toBe('Bearer options-token');
    });
  });

  describe('POST requests', () => {
    it('sends POST with JSON body', async () => {
      vi.mocked(fetch).mockResolvedValue(makeResponse({ user: {} }, 201));

      await client.post('/users', { email: 'test@example.com' });

      const [, options] = vi.mocked(fetch).mock.calls[0];
      expect(options?.method).toBe('POST');
      expect(options?.body).toBe('{"email":"test@example.com"}');
    });

    it('sends POST with no body when data is undefined', async () => {
      vi.mocked(fetch).mockResolvedValue(makeResponse({}));

      await client.post('/endpoint');

      const [, options] = vi.mocked(fetch).mock.calls[0];
      expect(options?.body).toBeUndefined();
    });
  });

  describe('PUT requests', () => {
    it('sends PUT with JSON body', async () => {
      vi.mocked(fetch).mockResolvedValue(makeResponse({ user: {} }));

      await client.put('/user', { bio: 'Updated bio' });

      const [, options] = vi.mocked(fetch).mock.calls[0];
      expect(options?.method).toBe('PUT');
      expect(options?.body).toBe('{"bio":"Updated bio"}');
    });
  });

  describe('DELETE requests', () => {
    it('sends DELETE request', async () => {
      vi.mocked(fetch).mockResolvedValue(makeResponse(null, 204));

      await client.delete('/articles/my-slug');

      expect(fetch).toHaveBeenCalledWith(
        'http://test-api/articles/my-slug',
        expect.objectContaining({ method: 'DELETE' })
      );
    });
  });

  describe('error handling', () => {
    it('throws API error on non-OK response', async () => {
      const errorBody = { errors: { email: ['is already taken'] } };
      vi.mocked(fetch).mockResolvedValue(makeResponse(errorBody, 422));

      await expect(client.post('/users', {})).rejects.toMatchObject({
        errors: { email: ['is already taken'] },
      });
    });

    it('throws fallback error when response body is not valid JSON', async () => {
      vi.mocked(fetch).mockResolvedValue({
        ok: false,
        status: 500,
        json: () => Promise.reject(new Error('not json')),
      } as Response);

      await expect(client.get('/broken')).rejects.toMatchObject({
        errors: { body: ['An error occurred'] },
      });
    });

    it('returns empty object for 204 No Content', async () => {
      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        status: 204,
        json: () => Promise.reject(new Error('no content')),
      } as Response);

      const result = await client.delete('/articles/slug/favorite');
      expect(result).toEqual({});
    });
  });
});
