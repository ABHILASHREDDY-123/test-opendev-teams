import React, { useState, useEffect } from 'react';
import { getContacts } from './api';
import { Contact } from './types';

const ContactsPage = () => {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const token = localStorage.getItem('token');

  useEffect(() => {
    const fetchContacts = async () => {
      try {
        const data = await getContacts(token);
        setContacts(data);
      } catch (err) {
        setError(err.message || 'Failed to fetch contacts');
      } finally {
        setLoading(false);
      }
    };
    fetchContacts();
  }, [token]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  return (
    <div>
      <h1>Contacts</h1>
      {contacts.length === 0 ? (
        <div>No contacts yet. Add your first contact!</div>
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