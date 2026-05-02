import axios, { AxiosInstance } from 'axios';
import { LoginResponse, Contact } from './types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('jwt_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: async (mobile: string, password: string): Promise<string> => {
    const response = await apiClient.post<LoginResponse>('/auth/login', {
      mobile,
      password,
    });
    return response.data.access_token;
  },
};

export const contactsAPI = {
  getContacts: async (): Promise<Contact[]> => {
    const response = await apiClient.get<Contact[]>('/contacts');
    return response.data;
  },

  addContact: async (name: string, mobile: string): Promise<Contact> => {
    const response = await apiClient.post<Contact>('/contacts', {
      name,
      mobile,
    });
    return response.data;
  },

  deleteContact: async (contactId: string): Promise<void> => {
    await apiClient.delete(`/contacts/${contactId}`);
  },
};

export default apiClient;
