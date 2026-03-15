// Implement the ContactForm component with validation and API call
import React, { useState } from 'react';
import axios from 'axios';

const ContactForm = () => {
 const [name, setName] = useState('');
 const [mobile, setMobile] = useState('');
 const [error, setError] = useState(null);
 const [loading, setLoading] = useState(false);

 const handleSubmit = async (event) => {
 event.preventDefault();
 setLoading(true);
 try {
 const response = await axios.post('/api/contacts', { name, mobile });
 // Handle successful contact creation
 } catch (error) {
 setError(error.message);
 } finally {
 setLoading(false);
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
 <button type="submit" disabled={loading}>Create Contact</button>
 {error && <div style={{ color: 'red' }}>{error}</div>}
 </form>
 );
};

export default ContactForm;
