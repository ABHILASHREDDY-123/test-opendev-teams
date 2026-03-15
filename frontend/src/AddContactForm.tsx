import React, { useState } from 'react';
import { addContact } from './api';

interface Props {}

const AddContactForm: React.FC<Props> = () => {
  const [name, setName] = useState('');
  const [mobile, setMobile] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const token = localStorage.getItem('token');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await addContact(token, name, mobile);
      // Refresh contacts list
    } catch (err) {
      setError(err.message || 'Failed to add contact');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Name"
      />
      <input
        type="text"
        value={mobile}
        onChange={(e) => setMobile(e.target.value)}
        placeholder="Mobile number"
      />
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <button type="submit" disabled={loading}>{loading ? 'Loading...' : 'Add Contact'}</button>
    </form>
  );
};

export default AddContactForm;