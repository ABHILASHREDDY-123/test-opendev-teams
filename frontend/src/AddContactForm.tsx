<!-- AddContactForm.tsx -->
import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';

const AddContactForm = () => {
 const [name, setName] = useState('');
 const [mobile, setMobile] = useState('');
 const history = useHistory();

 const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
 event.preventDefault();
 // Call API to add contact
 console.log(`Add contact with name: ${name} and mobile: ${mobile}`);
 history.push('/contacts');
 };

 return (
 <div>
 <h1>Add Contact Form</h1>
 <form onSubmit={handleSubmit}>
 <label>
 Name:
 <input type="text" value={name} onChange={(event) => setName(event.target.value)} />
 </label>
 <br />
 <label>
 Mobile:
 <input type="text" value={mobile} onChange={(event) => setMobile(event.target.value)} />
 </label>
 <br />
 <button type="submit">Add Contact</button>
 </form>
 </div>
 );
};

export default AddContactForm;
