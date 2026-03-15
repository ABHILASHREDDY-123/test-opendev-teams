// API client functions
import fetch from 'node-fetch';

const login = async (mobile: string, password: string) => {
  const response = await fetch('/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ mobile, password })
  });
  const data = await response.json();
  return data;
};

const getContacts = async (token: string) => {
  const response = await fetch('/contacts', {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  const data = await response.json();
  return data;
};

const addContact = async (token: string, name: string, mobile: string) => {
  const response = await fetch('/contacts', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ name, mobile })
  });
  const data = await response.json();
  return data;
};

const updateContact = async (token: string, id: string, data: any) => {
  const response = await fetch(`/contacts/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(data)
  });
  const result = await response.json();
  return result;
};

const deleteContact = async (token: string, id: string) => {
  const response = await fetch(`/contacts/${id}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  return response.ok;
};

export { login, getContacts, addContact, updateContact, deleteContact };