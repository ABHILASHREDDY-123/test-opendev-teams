import React, { useState, useEffect } from 'react';
import { getContacts } from '../api';

const ContactsPage = () => {
 const [contacts, setContacts] = useState([]);
 const [isLoading, setIsLoading] = useState(false);
 const [error, setError] = useState(null);

 useEffect(() => {
 const fetchContacts = async () => {
 setIsLoading(true);
 try {
 const data = await getContacts();
 setContacts(data);
 } catch (error) {
 setError(error.message);
 } finally {
 setIsLoading(false);
 }
 };
 fetchContacts();
 }, []);

 return (
 <div>
 <h1>Contacts</h1>
 {isLoading ? (
 <div>Loading...</div>
 ) : (
 <ul>
 {contacts.map((contact) => (
 <li key={contact.id}>{contact.name} {contact.mobile}</li>
 ))}
 </ul>
 )}
 {error && <div style={{ color: 'red' }}>{error}</div>}
 </div>
 );
};

export default ContactsPage;
