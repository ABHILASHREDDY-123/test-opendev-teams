import * as api from '../api';

describe('API', () => {
  const mockFetch = jest.fn();
  global.fetch = mockFetch;

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    delete process.env.REACT_APP_API_URL;
  });

  describe('login', () => {
    it('should call login endpoint with correct data', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ token: 'test-token' })
      });

      const token = await api.login('9876543210', 'password123');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:3000/api/auth/login',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ mobile: '9876543210', password: 'password123' })
        })
      );
      expect(token).toBe('test-token');
    });

    it('should throw error on login failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ message: 'Invalid credentials' })
      });

      await expect(api.login('9876543210', 'wrong')).rejects.toThrow('Invalid credentials');
    });
  });

  describe('getContacts', () => {
    it('should call getContacts endpoint with auth header', async () => {
      localStorage.setItem('authToken', 'test-token');
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [
          { id: '1', name: 'John', mobile: '9876543210' }
        ]
      });

      const contacts = await api.getContacts();

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:3000/api/contacts',
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token'
          })
        })
      );
      expect(contacts).toHaveLength(1);
    });

    it('should throw error when no auth token', async () => {
      await expect(api.getContacts()).rejects.toThrow('No auth token found');
    });

    it('should throw error on fetch failure', async () => {
      localStorage.setItem('authToken', 'test-token');
      mockFetch.mockResolvedValueOnce({
        ok: false
      });

      await expect(api.getContacts()).rejects.toThrow('Failed to fetch contacts');
    });
  });

  describe('addContact', () => {
    it('should call addContact endpoint with auth header', async () => {
      localStorage.setItem('authToken', 'test-token');
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: '1', name: 'John', mobile: '9876543210' })
      });

      const contact = await api.addContact('John', '9876543210');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:3000/api/contacts',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token'
          }),
          body: JSON.stringify({ name: 'John', mobile: '9876543210' })
        })
      );
      expect(contact.name).toBe('John');
    });

    it('should throw error on add failure', async () => {
      localStorage.setItem('authToken', 'test-token');
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ message: 'Duplicate contact' })
      });

      await expect(api.addContact('John', '9876543210')).rejects.toThrow('Duplicate contact');
    });
  });

  describe('deleteContact', () => {
    it('should call deleteContact endpoint with auth header', async () => {
      localStorage.setItem('authToken', 'test-token');
      mockFetch.mockResolvedValueOnce({
        ok: true
      });

      await api.deleteContact('1');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:3000/api/contacts/1',
        expect.objectContaining({
          method: 'DELETE',
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token'
          })
        })
      );
    });

    it('should throw error on delete failure', async () => {
      localStorage.setItem('authToken', 'test-token');
      mockFetch.mockResolvedValueOnce({
        ok: false
      });

      await expect(api.deleteContact('1')).rejects.toThrow('Failed to delete contact');
    });
  });

  describe('updateContact', () => {
    it('should call updateContact endpoint with auth header', async () => {
      localStorage.setItem('authToken', 'test-token');
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: '1', name: 'Jane', mobile: '9876543211' })
      });

      const contact = await api.updateContact('1', { name: 'Jane' });

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:3000/api/contacts/1',
        expect.objectContaining({
          method: 'PUT',
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token'
          }),
          body: JSON.stringify({ name: 'Jane' })
        })
      );
      expect(contact.name).toBe('Jane');
    });

    it('should throw error on update failure', async () => {
      localStorage.setItem('authToken', 'test-token');
      mockFetch.mockResolvedValueOnce({
        ok: false
      });

      await expect(api.updateContact('1', { name: 'Jane' })).rejects.toThrow('Failed to update contact');
    });
  });
});
