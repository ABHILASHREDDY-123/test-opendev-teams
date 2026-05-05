import { apiService, LoginRequest, Contact, CreateContactRequest } from '../api';

describe('API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockClear();
  });

  describe('login', () => {
    it('calls login endpoint with correct data', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ access_token: 'test-token', token_type: 'bearer' }),
      });

      const loginData: LoginRequest = {
        mobile: '9876543210',
        password: 'password123',
      };

      await apiService.login(loginData);

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/auth/login',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(loginData),
        }
      );
    });

    it('returns access token on successful login', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ access_token: 'test-token-123', token_type: 'bearer' }),
      });

      const result = await apiService.login({
        mobile: '9876543210',
        password: 'password123',
      });

      expect(result.access_token).toBe('test-token-123');
      expect(result.token_type).toBe('bearer');
    });

    it('throws error on 401 response', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

      await expect(
        apiService.login({
          mobile: '9876543210',
          password: 'wrongpassword',
        })
      ).rejects.toThrow('Invalid mobile or password');
    });

    it('throws error on other failed responses', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      await expect(
        apiService.login({
          mobile: '9876543210',
          password: 'password123',
        })
      ).rejects.toThrow('Login failed');
    });

    it('throws error on network failure', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      await expect(
        apiService.login({
          mobile: '9876543210',
          password: 'password123',
        })
      ).rejects.toThrow('Network error');
    });
  });

  describe('getContacts', () => {
    it('calls getContacts endpoint with auth header', async () => {
      (localStorage.getItem as jest.Mock).mockReturnValue('test-token');
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => [],
      });

      await apiService.getContacts();

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/contacts',
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Bearer test-token',
          },
        }
      );
    });

    it('returns contacts list', async () => {
      (localStorage.getItem as jest.Mock).mockReturnValue('test-token');
      const mockContacts: Contact[] = [
        { id: 1, name: 'John', mobile: '9876543210' },
        { id: 2, name: 'Jane', mobile: '9123456789' },
      ];

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockContacts,
      });

      const result = await apiService.getContacts();

      expect(result).toEqual(mockContacts);
    });

    it('clears token and redirects on 401', async () => {
      (localStorage.getItem as jest.Mock).mockReturnValue('test-token');
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

      const originalLocation = window.location;
      const mockLocation = { href: '' };
      Object.defineProperty(window, 'location', {
        value: mockLocation,
        writable: true,
      });

      await expect(apiService.getContacts()).rejects.toThrow('Unauthorized');

      expect(localStorage.removeItem).toHaveBeenCalledWith('token');
      expect(mockLocation.href).toBe('/login');

      Object.defineProperty(window, 'location', {
        value: originalLocation,
        writable: true,
      });
    });

    it('throws error on fetch failure', async () => {
      (localStorage.getItem as jest.Mock).mockReturnValue('test-token');
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      await expect(apiService.getContacts()).rejects.toThrow(
        'Failed to fetch contacts'
      );
    });
  });

  describe('createContact', () => {
    it('calls createContact endpoint with auth header', async () => {
      (localStorage.getItem as jest.Mock).mockReturnValue('test-token');
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ id: 1, name: 'John', mobile: '9876543210' }),
      });

      const contactData: CreateContactRequest = {
        name: 'John',
        mobile: '9876543210',
      };

      await apiService.createContact(contactData);

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/contacts',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Bearer test-token',
          },
          body: JSON.stringify(contactData),
        }
      );
    });

    it('returns created contact', async () => {
      (localStorage.getItem as jest.Mock).mockReturnValue('test-token');
      const createdContact: Contact = {
        id: 1,
        name: 'John',
        mobile: '9876543210',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => createdContact,
      });

      const result = await apiService.createContact({
        name: 'John',
        mobile: '9876543210',
      });

      expect(result).toEqual(createdContact);
    });

    it('clears token and redirects on 401', async () => {
      (localStorage.getItem as jest.Mock).mockReturnValue('test-token');
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

      const originalLocation = window.location;
      const mockLocation = { href: '' };
      Object.defineProperty(window, 'location', {
        value: mockLocation,
        writable: true,
      });

      await expect(
        apiService.createContact({
          name: 'John',
          mobile: '9876543210',
        })
      ).rejects.toThrow('Unauthorized');

      expect(localStorage.removeItem).toHaveBeenCalledWith('token');
      expect(mockLocation.href).toBe('/login');

      Object.defineProperty(window, 'location', {
        value: originalLocation,
        writable: true,
      });
    });

    it('throws error on creation failure', async () => {
      (localStorage.getItem as jest.Mock).mockReturnValue('test-token');
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
      });

      await expect(
        apiService.createContact({
          name: 'John',
          mobile: '9876543210',
        })
      ).rejects.toThrow('Failed to create contact');
    });
  });

  describe('deleteContact', () => {
    it('calls deleteContact endpoint with auth header', async () => {
      (localStorage.getItem as jest.Mock).mockReturnValue('test-token');
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
      });

      await apiService.deleteContact(1);

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/contacts/1',
        {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Bearer test-token',
          },
        }
      );
    });

    it('clears token and redirects on 401', async () => {
      (localStorage.getItem as jest.Mock).mockReturnValue('test-token');
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

      const originalLocation = window.location;
      const mockLocation = { href: '' };
      Object.defineProperty(window, 'location', {
        value: mockLocation,
        writable: true,
      });

      await expect(apiService.deleteContact(1)).rejects.toThrow('Unauthorized');

      expect(localStorage.removeItem).toHaveBeenCalledWith('token');
      expect(mockLocation.href).toBe('/login');

      Object.defineProperty(window, 'location', {
        value: originalLocation,
        writable: true,
      });
    });

    it('throws error on deletion failure', async () => {
      (localStorage.getItem as jest.Mock).mockReturnValue('test-token');
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
      });

      await expect(apiService.deleteContact(1)).rejects.toThrow(
        'Failed to delete contact'
      );
    });
  });
});
