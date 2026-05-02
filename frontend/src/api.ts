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

export interface AddContactRequest {
  name: string;
  mobile: string;
}

export class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'APIError';
  }
}

function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem('authToken');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function login(mobile: string, password: string): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mobile, password }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new APIError(response.status, error.message || 'Login failed');
  }

  const data: LoginResponse = await response.json();
  return data.token;
}

export async function getContacts(): Promise<Contact[]> {
  const response = await fetch(`${API_BASE_URL}/contacts`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
  });

  if (!response.ok) {
    throw new APIError(response.status, 'Failed to fetch contacts');
  }

  return response.json();
}

export async function addContact(name: string, mobile: string): Promise<Contact> {
  const response = await fetch(`${API_BASE_URL}/contacts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
    body: JSON.stringify({ name, mobile }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new APIError(response.status, error.message || 'Failed to add contact');
  }

  return response.json();
}

export async function deleteContact(id: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/contacts/${id}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
  });

  if (!response.ok) {
    throw new APIError(response.status, 'Failed to delete contact');
  }
}
