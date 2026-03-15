import { LoginForm, Contact, ContactForm } from './types';

const apiUrl = 'https://api.example.com';

async function login(formData: LoginForm): Promise<{ access_token: string; token_type: string }> {
  try {
    const response = await fetch(`${apiUrl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    });
    if (!response.ok) throw new Error('Login failed');
    return response.json();
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

async function getContacts(token: string): Promise<Contact[]> {
  try {
    const response = await fetch(`${apiUrl}/contacts`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) throw new Error('Failed to fetch contacts');
    return response.json();
  } catch (error) {
    console.error('Get contacts error:', error);
    throw error;
  }
}

async function addContact(token: string, formData: ContactForm): Promise<Contact> {
  try {
    const response = await fetch(`${apiUrl}/contacts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(formData),
    });
    if (!response.ok) throw new Error('Failed to add contact');
    return response.json();
  } catch (error) {
    console.error('Add contact error:', error);
    throw error;
  }
}

export { login, getContacts, addContact };