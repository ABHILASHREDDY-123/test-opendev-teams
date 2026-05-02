/**
 * API client for Contacts Website
 * Handles authentication and contact management
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3000/api';

export interface LoginRequest {
  mobile: string;
  password: string;
}

export interface LoginResponse {
  token: string;
}

export interface Contact {
  id: string;
  name: string;
  mobile: string;
}

export interface CreateContactRequest {
  name: string;
  mobile: string;
}

class ApiClient {
  private getAuthHeader(): Record<string, string> {
    const token = localStorage.getItem('jwt_token');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
  }

  async login(mobile: string, password: string): Promise<string> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mobile, password }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Login failed' }));
      throw new Error(error.message || 'Login failed');
    }

    const data: LoginResponse = await response.json();
    return data.token;
  }

  async getContacts(): Promise<Contact[]> {
    const response = await fetch(`${API_BASE_URL}/contacts`, {
      method: 'GET',
      headers: this.getAuthHeader(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch contacts');
    }

    return response.json();
  }

  async createContact(name: string, mobile: string): Promise<Contact> {
    const response = await fetch(`${API_BASE_URL}/contacts`, {
      method: 'POST',
      headers: this.getAuthHeader(),
      body: JSON.stringify({ name, mobile }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Failed to create contact' }));
      throw new Error(error.message || 'Failed to create contact');
    }

    return response.json();
  }

  async deleteContact(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/contacts/${id}`, {
      method: 'DELETE',
      headers: this.getAuthHeader(),
    });

    if (!response.ok) {
      throw new Error('Failed to delete contact');
    }
  }
}

export const apiClient = new ApiClient();
