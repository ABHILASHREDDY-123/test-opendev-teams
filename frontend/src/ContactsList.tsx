import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ContactsList = () => {
  const [contacts, setContacts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchContacts = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get('/contacts');
      setContacts(response.data);
    } catch (error) {
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchContacts();
  }, []);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div style={{ color: 'red' }}>{error}</div>;
  }

  return (
    <ul>
      {contacts.map((contact) => (
        <li key={contact.id}>{contact.name} ({contact.mobile})</li>
      ))}
    </ul>
  );
};

export default ContactsList;
