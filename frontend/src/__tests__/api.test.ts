import {
  login,
  getContacts,
  addContact,
  deleteContact,
  updateContact,
  getToken,
  storeToken,
  clearToken,
} from '../api';

// Mock fetch
global.fetch = jest.fn();

describe('API Client', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    sessionStorage.clear();
  });

  describe('Token Management', () => {
    it('should store token in localStorage', () => {
      storeToken('test-token');
      expect(localStorage.getItem('jwt_token')).toBe('test-token');
    });

    it('should retrieve token from localStorage', () => {
      localStorage.setItem('jwt_token', 'test-token');
      expect(getToken()).toBe('test-token');
    });

    it('should retrieve token from sessionStorage if localStorage is empty', () => {
      sessionStorage.setItem('jwt_token', 'session-token');
      expect(getToken()).toBe('session-token');
    });

    it('should return null if no token exists', () => {
      expect(getToken()).toBeNull();
    });

    it('should clear token from both storages', () => {
      localStorage.setItem('jwt_token', 'test-token');
      sessionStorage.setItem('jwt_token', 'session-token');
      clearToken();
      expect(localStorage.getItem('jwt_token')).toBeNull();
      expect(sessionStorage.getItem('jwt_token')).toBeNull();
    });
  });

  describe('Login', () => {
    it('should successfully login with valid credentials', async () => {
      const mockResponse = { token: 'jwt-token-123' };
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await login('9876543210', 'password123');
      expect(result.token).toBe('jwt-token-123');
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/auth/login'),
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ mobile: '9876543210', password: 'password123' }),
        })
      );
    });

    it('should throw error on invalid credentials (401)', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

      await expect(login('9876543210', 'wrongpassword')).rejects.toThrow(
        'Login failed: 401'
      );
    });

    it('should throw error on network failure', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      await expect(login('9876543210', 'password123')).rejects.toThrow(
        'Network error'
      );
    });
  });

  describe('Get Contacts', () => {
    beforeEach(() => {
      storeToken('test-token');
    });

    it('should fetch contacts with valid token', async () => {
      const mockContacts = [
        { id: '1', name: 'John Doe', mobile: '9876543210' },
        { id: '2', name: 'Jane Smith', mobile: '9876543211' },
      ];
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ contacts: mockContacts }),
      });

      const result = await getContacts();
      expect(result).toEqual(mockContacts);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/contacts'),
        expect.objectContaining({
          method: 'GET',
          headers: {
            'Authorization': 'Bearer test-token',
            'Content-Type': 'application/json',
          },
        })
      );
    });

    it('should return empty array if no contacts', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ contacts: [] }),
      });

      const result = await getContacts();
      expect(result).toEqual([]);
    });

    it('should throw error on 401 unauthorized', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

      await expect(getContacts()).rejects.toThrow('Unauthorized');
      expect(localStorage.getItem('jwt_token')).toBeNull();
    });

    it('should throw error if no token found', async () => {
      clearToken();
      await expect(getContacts()).rejects.toThrow('No token found');
    });
  });

  describe('Add Contact', () => {
    beforeEach(() => {
      storeToken('test-token');
    });

    it('should add a new contact', async () => {
      const mockContact = { id: '3', name: 'Bob Johnson', mobile: '9876543212' };
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ contact: mockContact }),
      });

      const result = await addContact('Bob Johnson', '9876543212');
      expect(result).toEqual(mockContact);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/contacts'),
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Authorization': 'Bearer test-token',
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ name: 'Bob Johnson', mobile: '9876543212' }),
        })
      );
    });

    it('should throw error on 401 unauthorized', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

      await expect(addContact('Bob Johnson', '9876543212')).rejects.toThrow(
        'Unauthorized'
      );
      expect(localStorage.getItem('jwt_token')).toBeNull();
    });

    it('should throw error if no token found', async () => {
      clearToken();
      await expect(addContact('Bob Johnson', '9876543212')).rejects.toThrow(
        'No token found'
      );
    });
  });

  describe('Delete Contact', () => {
    beforeEach(() => {
      storeToken('test-token');
    });

    it('should delete a contact', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
      });

      await deleteContact('1');
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/contacts/1'),
        expect.objectContaining({
          method: 'DELETE',
          headers: {
            'Authorization': 'Bearer test-token',
            'Content-Type': 'application/json',
          },
        })
      );
    });

    it('should throw error on 401 unauthorized', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

      await expect(deleteContact('1')).rejects.toThrow('Unauthorized');
      expect(localStorage.getItem('jwt_token')).toBeNull();
    });

    it('should throw error if no token found', async () => {
      clearToken();
      await expect(deleteContact('1')).rejects.toThrow('No token found');
    });
  });

  describe('Update Contact', () => {
    beforeEach(() => {
      storeToken('test-token');
    });

    it('should update a contact', async () => {
      const mockContact = { id: '1', name: 'John Updated', mobile: '9876543299' };
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ contact: mockContact }),
      });

      const result = await updateContact('1', 'John Updated', '9876543299');
      expect(result).toEqual(mockContact);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/contacts/1'),
        expect.objectContaining({
          method: 'PUT',
          headers: {
            'Authorization': 'Bearer test-token',
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ name: 'John Updated', mobile: '9876543299' }),
        })
      );
    });

    it('should throw error on 401 unauthorized', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

      await expect(updateContact('1', 'John Updated', '9876543299')).rejects.toThrow(
        'Unauthorized'
      );
    });

    it('should throw error if no token found', async () => {
      clearToken();
      await expect(updateContact('1', 'John Updated', '9876543299')).rejects.toThrow(
        'No token found'
      );
    });
  });
});
