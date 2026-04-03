import axios from 'axios';

const api = axios.create({
  baseURL: 'https://api.example.com',
});

export const getContacts = async (token: string) => {
  const response = await api.get('/contacts', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};