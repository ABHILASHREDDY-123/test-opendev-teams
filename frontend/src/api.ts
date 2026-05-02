/**
 * API client for Contacts Website
 * Handles all communication with backend API
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3000/api';

/**
 * Get JWT token from storage
 */
export const getToken = (): string | null => {
  return localStorage.getItem('jwt_token') || sessionStorage.getItem('jwt_token');
};

/**
 * Store JWT token securely
 */
export const storeToken = (token: string): void => {
  localStorage.setItem('jwt_token', token);
};

/**
 * Clear JWT token
 */
export const clearToken = (): void => {
  localStorage.removeItem('jwt_token');
  sessionStorage.removeItem('jwt_token');
};

/**
 * Login API call
 */
export const login = async (mobile: string, password: string): Promise<{ token: string }> => {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ mobile, password }),
  });

  if (!response.ok) {
    throw new Error(`Login failed: ${response.status}`);
  }

  const data = await response.json();
  return data;
};

/**
 * Contact interface
 */
export interface Contact {
  id: string;
  name: string;
  mobile: string;
}

/**
 * Fetch all contacts for the user
 */
export const getContacts = async (): Promise<Contact[]> => {
  const token = getToken();
  if (!token) {
    throw new Error('No token found');
  }

  const response = await fetch(`${API_BASE_URL}/contacts`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (response.status === 401) {
    clearToken();
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    throw new Error(`Failed to fetch contacts: ${response.status}`);
  }

  const data = await response.json();
  return data.contacts || [];
};

/**
 * Add a new contact
 */
export const addContact = async (name: string, mobile: string): Promise<Contact> => {
  const token = getToken();
  if (!token) {
    throw new Error('No token found');
  }

  const response = await fetch(`${API_BASE_URL}/contacts`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ name, mobile }),
  });

  if (response.status === 401) {
    clearToken();
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    throw new Error(`Failed to add contact: ${response.status}`);
  }

  const data = await response.json();
  return data.contact;
};

/**
 * Delete a contact
 */
export const deleteContact = async (id: string): Promise<void> => {
  const token = getToken();
  if (!token) {
    throw new Error('No token found');
  }

  const response = await fetch(`${API_BASE_URL}/contacts/${id}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (response.status === 401) {
    clearToken();
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    throw new Error(`Failed to delete contact: ${response.status}`);
  }
};

/**
 * Update a contact (optional for MVP)
 */
export const updateContact = async (id: string, name: string, mobile: string): Promise<Contact> => {
  const token = getToken();
  if (!token) {
    throw new Error('No token found');
  }

  const response = await fetch(`${API_BASE_URL}/contacts/${id}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ name, mobile }),
  });

  if (response.status === 401) {
    clearToken();
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    throw new Error(`Failed to update contact: ${response.status}`);
  }

  const data = await response.json();
  return data.contact;
};
