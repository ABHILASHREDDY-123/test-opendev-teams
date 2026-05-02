import { apiClient } from '../apiClient';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

describe('ApiClient', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
    localStorageMock.removeItem.mockClear();
    localStorageMock.clear.mockClear();
    (global.fetch as any) = jest.fn();
  });

  describe('Token Management', () => {
    it('should store token in localStorage', () => {
      const token = 'test-token-123';
      apiClient.setToken(token);
      expect(localStorageMock.setItem).toHaveBeenCalledWith('auth_token', token);
    });

    it('should retrieve token from localStorage', () => {
      const token = 'test-token-123';
      localStorageMock.getItem.mockReturnValue(token);
      const retrieved = apiClient.getToken();
      expect(retrieved).toBe(token);
      expect(localStorageMock.getItem).toHaveBeenCalledWith('auth_token');
    });

    it('should clear token from localStorage', () => {
      apiClient.clearToken();
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token');
    });

    it('should return null when no token exists', () => {
      localStorageMock.getItem.mockReturnValue(null);
      const token = apiClient.getToken();
      expect(token).toBeNull();
    });
  });

  describe('Login', () => {
    it('should send login request with mobile and password', async () => {
      const mockResponse = {
        access_token: 'jwt-token',
        token_type: 'bearer',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const result = await apiClient.login('9876543210', 'password123');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/login'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ mobile: '9876543210', password: 'password123' }),
        })
      );

      expect(result.data).toEqual(mockResponse);
      expect(result.status).toBe(200);
    });

    it('should handle 401 Unauthorized response', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Invalid credentials' }),
      });

      const result = await apiClient.login('9876543210', 'wrongpassword');

      expect(result.status).toBe(401);
      expect(result.error).toBe('Invalid credentials');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token');
    });

    it('should handle network errors', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      const result = await apiClient.login('9876543210', 'password123');

      expect(result.error).toBe('Network error');
      expect(result.status).toBe(0);
    });
  });

  describe('Header Injection', () => {
    it('should include Authorization header with token for protected endpoints', async () => {
      const token = 'jwt-token-123';
      localStorageMock.getItem.mockReturnValue(token);

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ contacts: [] }),
      });

      await apiClient.getContacts();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: `Bearer ${token}`,
          }),
        })
      );
    });

    it('should not include Authorization header for public endpoints', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ access_token: 'token' }),
      });

      await apiClient.login('9876543210', 'password123');

      const callArgs = (global.fetch as jest.Mock).mock.calls[0];
      expect(callArgs[1].headers).not.toHaveProperty('Authorization');
    });
  });

  describe('Contacts API', () => {
    beforeEach(() => {
      localStorageMock.getItem.mockReturnValue('jwt-token');
    });

    it('should fetch contacts', async () => {
      const mockContacts = [
        { id: '1', name: 'John', mobile: '9876543210' },
        { id: '2', name: 'Jane', mobile: '9876543211' },
      ];

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockContacts,
      });

      const result = await apiClient.getContacts();

      expect(result.data).toEqual(mockContacts);
      expect(result.status).toBe(200);
    });

    it('should create contact', async () => {
      const newContact = { id: '3', name: 'Bob', mobile: '9876543212' };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => newContact,
      });

      const result = await apiClient.createContact('Bob', '9876543212');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/contacts'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ name: 'Bob', mobile: '9876543212' }),
        })
      );

      expect(result.data).toEqual(newContact);
    });

    it('should update contact', async () => {
      const updated = { id: '1', name: 'John Updated', mobile: '9876543210' };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => updated,
      });

      const result = await apiClient.updateContact('1', { name: 'John Updated' });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/contacts/1'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify({ name: 'John Updated' }),
        })
      );

      expect(result.data).toEqual(updated);
    });

    it('should delete contact', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 204,
        json: async () => ({}),
      });

      const result = await apiClient.deleteContact('1');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/contacts/1'),
        expect.objectContaining({
          method: 'DELETE',
        })
      );

      expect(result.status).toBe(204);
    });

    it('should handle 401 on protected endpoint and clear token', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Unauthorized' }),
      });

      await apiClient.getContacts();

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token');
    });
  });

  describe('Register', () => {
    it('should send register request', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => ({ message: 'User registered' }),
      });

      const result = await apiClient.register('9876543210', 'password123');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/register'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ mobile: '9876543210', password: 'password123' }),
        })
      );

      expect(result.status).toBe(201);
    });
  });
});
