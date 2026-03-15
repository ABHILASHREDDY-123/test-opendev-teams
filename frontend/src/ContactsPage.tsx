import React, { useState, useEffect } from 'react';
import { getContacts } from './api';
import { Contact } from './types';

const ContactsPage = () => {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchContacts = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) throw new Error('No authentication token');
        const data = await getContacts(token);
        setContacts(data);
      } catch (err) {
        setError('Failed to load contacts');
      } finally {
        setIsLoading(false);
      }
    };
    fetchContacts();
  }, []);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  return (
    <div>
      <h1>Contacts</h1>
      {contacts.length === 0 ? (
        <p>No contacts yet. Add your first contact!</p>
      ) : (
        <ul>
          {contacts.map((contact) => (
            <li key={contact.id}>
              {contact.name} - {contact.mobile}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ContactsPage;