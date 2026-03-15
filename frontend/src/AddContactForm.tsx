import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';

const AddContactForm = () => {
 const [name, setName] = useState('');
 const [mobile, setMobile] = useState('');
 const history = useHistory();

 const handleSubmit = (event) => {
 event.preventDefault();
 // Call API to add contact
 history.push('/contacts');
 };

 return (
 <div>
 <h1>Add Contact Form</h1>
 <form onSubmit={handleSubmit}>
 <label>Name:</label>
 <input type='text' value={name} onChange={(event) => setName(event.target.value)} />
 <br />
 <label>Mobile:</label>
 <input type='text' value={mobile} onChange={(event) => setMobile(event.target.value)} />
 <br />
 <button type='submit'>Add Contact</button>
 </form>
 </div>
 );
};

export default AddContactForm;
