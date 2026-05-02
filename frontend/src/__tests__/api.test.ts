import { login, getContacts, addContact, deleteContact, APIError } from '../api';

describe('API Module', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe('login', () => {
    it('should successfully login and return token', async () => {
      const mockToken = 'test-token-123';
      global.fetch = jest.fn().mockResolvedValueOnce({
        ok: true,
        json: async () => ({ token: mockToken }),
      });

      const token = await login('9876543210', 'password123');

      expect(token).toBe(mockToken);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:3000/api/auth/login',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ mobile: '9876543210', password: 'password123' }),
        })
      );
    });

    it('should throw APIError on failed login', async () => {
      global.fetch = jest.fn().mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ message: 'Invalid credentials' }),
      });

      await expect(login('9876543210', 'wrongpass')).rejects.toThrow(APIError);
    });

    it('should handle missing error message in response', async () => {
      global.fetch = jest.fn().mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({}),
      });

      await expect(login('9876543210', 'password123')).rejects.toThrow('Login failed');
    });
  });

  describe('getContacts', () => {
    it('should fetch contacts with authorization header', async () => {
      const mockContacts = [
        { id: '1', name: 'John', mobile: '9876543210' },
        { id: '2', name: 'Jane', mobile: '9876543211' },
      ];
      localStorage.setItem('authToken', 'test-token');

      global.fetch = jest.fn().mockResolvedValueOnce({
        ok: true,
        json: async () => mockContacts,
      });

      const contacts = await getContacts();

      expect(contacts).toEqual(mockContacts);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:3000/api/contacts',
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            Authorization: 'Bearer test-token',
          }),
        })
      );
    });

    it('should throw APIError on failed fetch', async () => {
      localStorage.setItem('authToken', 'test-token');
      global.fetch = jest.fn().mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

      await expect(getContacts()).rejects.toThrow(APIError);
    });

    it('should work without token', async () => {
      global.fetch = jest.fn().mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      const contacts = await getContacts();

      expect(contacts).toEqual([]);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:3000/api/contacts',
        expect.objectContaining({
          headers: expect.not.objectContaining({
            Authorization: expect.anything(),
          }),
        })
      );
    });
  });

  describe('addContact', () => {
    it('should add contact with authorization header', async () => {
      const newContact = { id: '3', name: 'Bob', mobile: '9876543212' };
      localStorage.setItem('authToken', 'test-token');

      global.fetch = jest.fn().mockResolvedValueOnce({
        ok: true,
        json: async () => newContact,
      });

      const contact = await addContact('Bob', '9876543212');

      expect(contact).toEqual(newContact);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:3000/api/contacts',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            Authorization: 'Bearer test-token',
          }),
          body: JSON.stringify({ name: 'Bob', mobile: '9876543212' }),
        })
      );
    });

    it('should throw APIError on failed add', async () => {
      localStorage.setItem('authToken', 'test-token');
      global.fetch = jest.fn().mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ message: 'Invalid contact data' }),
      });

      await expect(addContact('Bob', '9876543212')).rejects.toThrow(APIError);
    });
  });

  describe('deleteContact', () => {
    it('should delete contact with authorization header', async () => {
      localStorage.setItem('authToken', 'test-token');

      global.fetch = jest.fn().mockResolvedValueOnce({
        ok: true,
      });

      await deleteContact('3');

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:3000/api/contacts/3',
        expect.objectContaining({
          method: 'DELETE',
          headers: expect.objectContaining({
            Authorization: 'Bearer test-token',
          }),
        })
      );
    });

    it('should throw APIError on failed delete', async () => {
      localStorage.setItem('authToken', 'test-token');
      global.fetch = jest.fn().mockResolvedValueOnce({
        ok: false,
        status: 404,
      });

      await expect(deleteContact('999')).rejects.toThrow(APIError);
    });
  });

  describe('APIError', () => {
    it('should create error with status and message', () => {
      const error = new APIError(401, 'Unauthorized');
      expect(error.status).toBe(401);
      expect(error.message).toBe('Unauthorized');
      expect(error.name).toBe('APIError');
    });
  });
});
