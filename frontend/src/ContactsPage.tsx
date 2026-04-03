import React, { useState, useEffect } from 'react';
import { getContacts, deleteContact } from './api';
import AddContactForm from './AddContactForm';
import ContactCard from './ContactCard';

const ContactsPage = () => {
  const [contacts, setContacts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const token = localStorage.getItem('token');

  useEffect(() => {
    const fetchContacts = async () => {
      try {
        const data = await getContacts(token);
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
      await deleteContact(token, id);
      setContacts(contacts.filter((contact) => contact.id !== id));
    } catch (err) {
      setError('Failed to delete contact');
    }
  };

  const handleAddContact = (newContact) => {
    setContacts([...contacts, newContact]);
  };

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  return (
    <div>
      <h2>Contacts</h2>
      {contacts.length === 0 ? (
        <div>No contacts yet. Add your first contact!</div>
      ) : (
        contacts.map((contact) => (
          <ContactCard key={contact.id} contact={contact} onDelete={handleDelete} />
        ))
      )}
      <button onClick={() => setShowAddForm(!showAddForm)}>Add Contact</button>
      {showAddForm && <AddContactForm onAddContact={handleAddContact} />}
    </div>
  );
};

export default ContactsPage;