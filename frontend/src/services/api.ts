const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface LoginRequest {
  mobile: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface Contact {
  id: number;
  name: string;
  mobile: string;
}

export interface CreateContactRequest {
  name: string;
  mobile: string;
}

class ApiService {
  private getAuthHeader(): HeadersInit {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    };
  }

  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (response.status === 401) {
      throw new Error('Invalid mobile or password');
    }

    if (!response.ok) {
      throw new Error('Login failed');
    }

    return response.json();
  }

  async getContacts(): Promise<Contact[]> {
    const response = await fetch(`${API_BASE_URL}/contacts`, {
      method: 'GET',
      headers: this.getAuthHeader()
    });

    if (response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
      throw new Error('Unauthorized');
    }

    if (!response.ok) {
      throw new Error('Failed to fetch contacts');
    }

    return response.json();
  }

  async createContact(data: CreateContactRequest): Promise<Contact> {
    const response = await fetch(`${API_BASE_URL}/contacts`, {
      method: 'POST',
      headers: this.getAuthHeader(),
      body: JSON.stringify(data)
    });

    if (response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
      throw new Error('Unauthorized');
    }

    if (!response.ok) {
      throw new Error('Failed to create contact');
    }

    return response.json();
  }

  async deleteContact(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/contacts/${id}`, {
      method: 'DELETE',
      headers: this.getAuthHeader()
    });

    if (response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
      throw new Error('Unauthorized');
    }

    if (!response.ok) {
      throw new Error('Failed to delete contact');
    }
  }
}

export const apiService = new ApiService();
