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

export interface UpdateContactRequest {
  name?: string;
  mobile?: string;
}

const getAuthHeader = (): { Authorization: string } => {
  const token = localStorage.getItem('authToken');
  if (!token) {
    throw new Error('No auth token found');
  }
  return {
    Authorization: `Bearer ${token}`
  };
};

export const login = async (mobile: string, password: string): Promise<string> => {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ mobile, password })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Login failed');
  }

  const data: LoginResponse = await response.json();
  return data.token;
};

export const getContacts = async (): Promise<Contact[]> => {
  const headers = getAuthHeader();
  const response = await fetch(`${API_BASE_URL}/contacts`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...headers
    }
  });

  if (!response.ok) {
    throw new Error('Failed to fetch contacts');
  }

  return response.json();
};

export const addContact = async (name: string, mobile: string): Promise<Contact> => {
  const headers = getAuthHeader();
  const response = await fetch(`${API_BASE_URL}/contacts`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...headers
    },
    body: JSON.stringify({ name, mobile })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to add contact');
  }

  return response.json();
};

export const deleteContact = async (id: string): Promise<void> => {
  const headers = getAuthHeader();
  const response = await fetch(`${API_BASE_URL}/contacts/${id}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      ...headers
    }
  });

  if (!response.ok) {
    throw new Error('Failed to delete contact');
  }
};

export const updateContact = async (id: string, data: UpdateContactRequest): Promise<Contact> => {
  const headers = getAuthHeader();
  const response = await fetch(`${API_BASE_URL}/contacts/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      ...headers
    },
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    throw new Error('Failed to update contact');
  }

  return response.json();
};
