import React, { useState, useEffect } from 'react';
import { getContacts, deleteContact } from './api';
import { Contact } from './types';

const ContactsPage = () => {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const token = localStorage.getItem('token');

  useEffect(() => {
    const fetchContacts = async () => {
      try {
        const data = await getContacts(token!);
        setContacts(data);
      } catch (err) {
        setError('Failed to load contacts');
      } finally {
        setIsLoading(false);
      }
    };
    fetchContacts();
  }, [token]);

  const handleDelete = async (id: string) => {
    try {
      await deleteContact(token!, id);
      setContacts(contacts.filter((contact) => contact.id !== id));
    } catch (err) {
      setError('Failed to delete contact');
    }
  };

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  return (
    <div>
      <h2>Contacts</h2>
      {contacts.length === 0 ? (
        <p>No contacts yet. Add your first contact!</p>
      ) : (
        <ul>
          {contacts.map((contact) => (
            <li key={contact.id}>
              {contact.name} - {contact.mobile}
              <button onClick={() => handleDelete(contact.id)}>Delete</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ContactsPage;