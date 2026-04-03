import React, { useState } from 'react';
import { addContact } from './api';

const AddContactForm = ({ onAddContact }) => {
  const [formData, setFormData] = useState({ name: '', mobile: '' });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const token = localStorage.getItem('token');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const newContact = await addContact(token, formData);
      onAddContact(newContact);
      setFormData({ name: '', mobile: '' });
    } catch (err) {
      setError('Failed to add contact');
    } finally {
      setIsLoading(false);
    }
  };

  const validateName = (name: string) => {
    if (name.trim().length < 2) {
      return 'Name must be at least 2 characters';
    }
    return '';
  };

  const validateMobile = (mobile: string) => {
    if (!/^[0-9]{10,}$/.test(mobile)) {
      return 'Invalid mobile number';
    }
    return '';
  };

  const nameError = validateName(formData.name);
  const mobileError = validateMobile(formData.mobile);

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Name:</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        />
        {nameError && <div style={{ color: 'red' }}>{nameError}</div>}
      </div>
      <div>
        <label>Mobile:</label>
        <input
          type="text"
          value={formData.mobile}
          onChange={(e) => setFormData({ ...formData, mobile: e.target.value })}
        />
        {mobileError && <div style={{ color: 'red' }}>{mobileError}</div>}
      </div>
      <button type="submit" disabled={isLoading || !!nameError || !!mobileError}>
        {isLoading ? 'Loading...' : 'Add Contact'}
      </button>
      {error && <div style={{ color: 'red' }}>{error}</div>}
    </form>
  );
};

export default AddContactForm;