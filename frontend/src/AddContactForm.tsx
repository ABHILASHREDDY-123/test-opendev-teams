import React, { useState } from 'react';
import { addContact } from './api';
import { ContactForm } from './types';

const AddContactForm = () => {
  const [formData, setFormData] = useState<ContactForm>({ name: '', mobile: '' });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('token');
      if (!token) throw new Error('No authentication token');
      await addContact(token, formData);
      setSuccess(true);
      setFormData({ name: '', mobile: '' });
    } catch (err) {
      setError('Failed to add contact');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Name"
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
      />
      <input
        type="text"
        placeholder="Mobile"
        value={formData.mobile}
        onChange={(e) => setFormData({ ...formData, mobile: e.target.value })}
      />
      <button type="submit" disabled={isLoading}>{isLoading ? 'Loading...' : 'Add Contact'}</button>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      {success && <div style={{ color: 'green' }}>Contact added successfully!</div>}
    </form>
  );
};

export default AddContactForm;