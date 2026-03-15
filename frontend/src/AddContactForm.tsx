import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const AddContactForm = () => {
 const [name, setName] = useState('');
 const [mobile, setMobile] = useState('');
 const navigate = useNavigate();

 const handleSubmit = (event) => {
 event.preventDefault();
 // Call API to add contact
 navigate('/contacts');
 };

 return (
 <form onSubmit={handleSubmit}>
 <label>Name:</label>
 <input type='text' value={name} onChange={(e) => setName(e.target.value)} />
 <label>Mobile:</label>
 <input type='text' value={mobile} onChange={(e) => setMobile(e.target.value)} />
 <button type='submit'>Add Contact</button>
 </form>
 );
};

export default AddContactForm;
