import React, { useState, useEffect } from 'react';
import { getContacts } from './api';
import ContactCard from './ContactCard';
import AddContactForm from './AddContactForm';

interface Props {}

const ContactsPage: React.FC<Props> = () => {
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const token = localStorage.getItem('token');

  useEffect(() => {
    const fetchContacts = async () => {
      try {
        const data = await getContacts(token);
        setContacts(data);
      } catch (err) {
        setError(err.message || 'Failed to load contacts');
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
        <p>No contacts yet. Add your first contact!</p>
      ) : (
        contacts.map((contact) => (
          <ContactCard key={contact.id} contact={contact} />
        ))
      )}
      <button onClick={() => setShowAddForm(!showAddForm)}>Add Contact</button>
      {showAddForm && <AddContactForm />}
    </div>
  );
};

export default ContactsPage;