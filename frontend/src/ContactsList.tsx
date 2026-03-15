import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const ContactsList = () => {
 const [contacts, setContacts] = useState([]);

 useEffect(() => {
 // Call API to get contacts
 }, []);

 return (
 <div>
 <h1>Contacts List</h1>
 <ul>
 {contacts.map((contact) => (
 <li key={contact.id}>{contact.name} {contact.mobile}</li>
 ))}
 </ul>
 <Link to='/add-contact'>Add Contact</Link>
 </div>
 );
};

export default ContactsList;
