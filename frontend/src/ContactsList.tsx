import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const ContactsList = () => {
 const [contacts, setContacts] = useState([]);

 useEffect(() => {
 // Call API to get contacts
 setContacts([
 { id: 1, name: 'John Doe', mobile: '1234567890' },
 { id: 2, name: 'Jane Doe', mobile: '9876543210' },
 ]);
 }, []);

 return (
 <div>
 <h1>Contacts List</h1>
 <ul>
 {contacts.map((contact) => (
 <li key={contact.id}>
 <Link to={`/contacts/${contact.id}`}>{contact.name}</Link>
 <span>{contact.mobile}</span>
 </li>
 ))}
 </ul>
 </div>
 );
};

export default ContactsList;
