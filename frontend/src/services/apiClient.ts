/**
 * Centralized API Client Service
 * Handles token management, header injection, and error handling
 */

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

export interface LoginRequest {
  mobile: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
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

export interface UpdateContactRequest {
  name?: string;
  mobile?: string;
}

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const TOKEN_KEY = 'auth_token';

class ApiClient {
  /**
   * Store JWT token in localStorage
   */
  setToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token);
  }

  /**
   * Retrieve JWT token from localStorage
   */
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  /**
   * Clear token from localStorage
   */
  clearToken(): void {
    localStorage.removeItem(TOKEN_KEY);
  }

  /**
   * Build headers with token injection
   */
  private getHeaders(includeAuth: boolean = true): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (includeAuth) {
      const token = this.getToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    return headers;
  }

  /**
   * Make HTTP request with error handling
   */
  private async request<T>(
    method: string,
    endpoint: string,
    body?: any,
    includeAuth: boolean = true
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${API_BASE_URL}${endpoint}`;
      const options: RequestInit = {
        method,
        headers: this.getHeaders(includeAuth),
      };

      if (body) {
        options.body = JSON.stringify(body);
      }

      const response = await fetch(url, options);
      const data = await response.json();

      if (!response.ok) {
        // Handle 401 Unauthorized
        if (response.status === 401) {
          this.clearToken();
        }
        return {
          error: data.detail || `HTTP ${response.status}`,
          status: response.status,
        };
      }

      return {
        data,
        status: response.status,
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Unknown error',
        status: 0,
      };
    }
  }

  /**
   * POST /register - User registration
   */
  async register(mobile: string, password: string): Promise<ApiResponse<any>> {
    return this.request('POST', '/register', { mobile, password }, false);
  }

  /**
   * POST /login - User login
   */
  async login(mobile: string, password: string): Promise<ApiResponse<LoginResponse>> {
    return this.request('POST', '/login', { mobile, password }, false);
  }

  /**
   * GET /contacts - Fetch user's contacts
   */
  async getContacts(): Promise<ApiResponse<Contact[]>> {
    return this.request('GET', '/contacts', undefined, true);
  }

  /**
   * POST /contacts - Create new contact
   */
  async createContact(name: string, mobile: string): Promise<ApiResponse<Contact>> {
    return this.request('POST', '/contacts', { name, mobile }, true);
  }

  /**
   * PUT /contacts/{id} - Update contact
   */
  async updateContact(id: string, updates: UpdateContactRequest): Promise<ApiResponse<Contact>> {
    return this.request('PUT', `/contacts/${id}`, updates, true);
  }

  /**
   * DELETE /contacts/{id} - Delete contact
   */
  async deleteContact(id: string): Promise<ApiResponse<any>> {
    return this.request('DELETE', `/contacts/${id}`, undefined, true);
  }
}

export const apiClient = new ApiClient();
