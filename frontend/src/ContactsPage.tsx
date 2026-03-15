import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const ContactsPage = () => {
 const [contacts, setContacts] = useState([]);
 const navigate = useNavigate();

 useEffect(() => {
 // Call API to fetch contacts
 }, []);

 const handleAddContact = () => {
 navigate('/add-contact');
 };

 return (
 <div>
 <h1>Contacts</h1>
 <ul>
 {contacts.map((contact) => (
 <li key={contact.id}>{contact.name} {contact.mobile}</li>
 ))}
 </ul>
 <button onClick={handleAddContact}>Add Contact</button>
 </div>
 );
};

export default ContactsPage;
