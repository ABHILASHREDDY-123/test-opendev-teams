import axios from 'axios';

const api = axios.create({
  baseURL: 'https://api.example.com'
});

export async function login(mobile: string, password: string) {
  try {
    const response = await api.post('/auth/login', { mobile, password });
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
}

export async function getContacts(token: string) {
  try {
    const response = await api.get('/contacts', {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
}

export async function addContact(token: string, name: string, mobile: string) {
  try {
    const response = await api.post('/contacts', { name, mobile }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
}