<!-- ContactsPage.tsx -->
import React, { useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';

const ContactsPage = () => {
 const [contacts, setContacts] = useState([]);
 const history = useHistory();

 useEffect(() => {
 // Fetch contacts from API
 console.log('Fetch contacts');
 setContacts([
 { id: 1, name: 'John Doe', mobile: '1234567890' },
 { id: 2, name: 'Jane Doe', mobile: '9876543210' },
 ]);
 }, []);

 const handleAddContact = () => {
 history.push('/add-contact');
 };

 return (
 <div>
 <h1>Contacts Page</h1>
 <ul>
 {contacts.map((contact) => (
 <li key={contact.id}>{contact.name} - {contact.mobile}</li>
 ))}
 </ul>
 <button onClick={handleAddContact}>Add Contact</button>
 </div>
 );
};

export default ContactsPage;
