import React, { useState } from 'react';
import { addContact } from '../api';

const AddContactForm = () => {
 const [name, setName] = useState('');
 const [mobile, setMobile] = useState('');
 const [error, setError] = useState(null);
 const [isLoading, setIsLoading] = useState(false);

 const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
 event.preventDefault();
 setIsLoading(true);
 try {
 await addContact(name, mobile);
 // Handle add contact success
 } catch (error) {
 setError(error.message);
 } finally {
 setIsLoading(false);
 }
 };

 return (
 <form onSubmit={handleSubmit}>
 <label>
 Name:
 <input type="text" value={name} onChange={(event) => setName(event.target.value)} />
 </label>
 <label>
 Mobile:
 <input type="text" value={mobile} onChange={(event) => setMobile(event.target.value)} />
 </label>
 <button type="submit" disabled={isLoading}>Add Contact</button>
 {error && <div style={{ color: 'red' }}>{error}</div>}
 {isLoading && <div>Loading...</div>}
 </form>
 );
};

export default AddContactForm;
