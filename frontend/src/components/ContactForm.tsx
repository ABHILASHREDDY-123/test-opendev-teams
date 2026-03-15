import React, { useState } from 'react';
import axios from 'axios';

const ContactForm = () => {
  const [name, setName] = useState('');
  const [mobile, setMobile] = useState('');
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    try {
      const response = await axios.post('/api/contacts', { name, mobile });
      // Handle successful contact creation
      console.log(response);
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
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <button type="submit" disabled={isLoading}>{isLoading ? 'Loading...' : 'Add Contact'}</button>
    </form>
  );
};

export default ContactForm;
