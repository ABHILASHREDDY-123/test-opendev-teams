import { LoginForm, Contact, ContactForm } from './types';

const apiBase = 'https://api.example.com';

async function login(formData: LoginForm): Promise<{ access_token: string; token_type: string }> {
  try {
    const response = await fetch(`${apiBase}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  } catch (error) {
    console.error('Login API error:', error);
    throw error;
  }
}

async function getContacts(token: string): Promise<Contact[]> {
  try {
    const response = await fetch(`${apiBase}/contacts`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  } catch (error) {
    console.error('Get contacts API error:', error);
    throw error;
  }
}

async function addContact(token: string, formData: ContactForm): Promise<Contact> {
  try {
    const response = await fetch(`${apiBase}/contacts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(formData),
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  } catch (error) {
    console.error('Add contact API error:', error);
    throw error;
  }
}

async function updateContact(token: string, id: string, data: Partial<ContactForm>): Promise<Contact> {
  try {
    const response = await fetch(`${apiBase}/contacts/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  } catch (error) {
    console.error('Update contact API error:', error);
    throw error;
  }
}

async function deleteContact(token: string, id: string): Promise<void> {
  try {
    const response = await fetch(`${apiBase}/contacts/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
  } catch (error) {
    console.error('Delete contact API error:', error);
    throw error;
  }
}

export { login, getContacts, addContact, updateContact, deleteContact };