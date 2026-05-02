import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { contactsAPI } from '../api';
import { Contact } from '../types';
import { validateName, validateMobile } from '../utils/validation';

const ContactsPage: React.FC = () => {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [name, setName] = useState('');
  const [mobile, setMobile] = useState('');
  const [nameError, setNameError] = useState('');
  const [mobileError, setMobileError] = useState('');
  const [addError, setAddError] = useState('');
  const [addLoading, setAddLoading] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('jwt_token');
    if (!token) {
      navigate('/login');
      return;
    }
    fetchContacts();
  }, [navigate]);

  const fetchContacts = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await contactsAPI.getContacts();
      setContacts(data);
    } catch (err: any) {
      if (err.response?.status === 401) {
        localStorage.removeItem('jwt_token');
        navigate('/login');
      } else {
        setError('Failed to load contacts');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleMobileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '');
    setMobile(value);
    setMobileError('');
  };

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setName(e.target.value);
    setNameError('');
  };

  const handleAddContact = async (e: React.FormEvent) => {
    e.preventDefault();
    setAddError('');
    setNameError('');
    setMobileError('');

    const nameValidation = validateName(name);
    if (!nameValidation.valid) {
      setNameError(nameValidation.error || 'Invalid name');
      return;
    }

    const mobileValidation = validateMobile(mobile);
    if (!mobileValidation.valid) {
      setMobileError(mobileValidation.error || 'Invalid mobile');
      return;
    }

    setAddLoading(true);
    try {
      const newContact = await contactsAPI.addContact(name, mobile);
      setContacts([...contacts, newContact]);
      setName('');
      setMobile('');
    } catch (err: any) {
      if (err.response?.status === 401) {
        localStorage.removeItem('jwt_token');
        navigate('/login');
      } else {
        setAddError('Failed to add contact');
      }
    } finally {
      setAddLoading(false);
    }
  };

  const handleDeleteContact = async (contactId: string) => {
    try {
      await contactsAPI.deleteContact(contactId);
      setContacts(contacts.filter((c) => c.id !== contactId));
      setDeleteConfirm(null);
    } catch (err: any) {
      if (err.response?.status === 401) {
        localStorage.removeItem('jwt_token');
        navigate('/login');
      } else {
        setError('Failed to delete contact');
      }
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('jwt_token');
    navigate('/login');
  };

  if (loading) {
    return <div className="contacts-container"><p>Loading...</p></div>;
  }

  return (
    <div className="contacts-container">
      <div className="header">
        <h1>My Contacts</h1>
        <button onClick={handleLogout} className="logout-btn">
          Logout
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="add-contact-form">
        <h2>Add New Contact</h2>
        <form onSubmit={handleAddContact}>
          <div className="form-group">
            <label htmlFor="name">Name</label>
            <input
              id="name"
              type="text"
              placeholder="Enter contact name"
              value={name}
              onChange={handleNameChange}
              disabled={addLoading}
            />
            {nameError && <span className="error">{nameError}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="mobile">Mobile Number</label>
            <input
              id="mobile"
              type="text"
              placeholder="Enter 10+ digit mobile number"
              value={mobile}
              onChange={handleMobileChange}
              disabled={addLoading}
              maxLength={15}
            />
            {mobileError && <span className="error">{mobileError}</span>}
          </div>

          {addError && <div className="error-message">{addError}</div>}

          <button type="submit" disabled={addLoading}>
            {addLoading ? 'Adding...' : 'Add Contact'}
          </button>
        </form>
      </div>

      <div className="contacts-list">
        <h2>Contacts</h2>
        {contacts.length === 0 ? (
          <p className="empty-state">No contacts yet. Add one above!</p>
        ) : (
          <ul>
            {contacts.map((contact) => (
              <li key={contact.id} className="contact-item">
                <div className="contact-info">
                  <span className="contact-name">{contact.name}</span>
                  <span className="contact-mobile">{contact.mobile}</span>
                </div>
                <button
                  onClick={() => setDeleteConfirm(contact.id)}
                  className="delete-btn"
                >
                  Delete
                </button>
                {deleteConfirm === contact.id && (
                  <div className="confirmation-dialog">
                    <p>Are you sure you want to delete this contact?</p>
                    <button
                      onClick={() => handleDeleteContact(contact.id)}
                      className="confirm-btn"
                    >
                      Yes, Delete
                    </button>
                    <button
                      onClick={() => setDeleteConfirm(null)}
                      className="cancel-btn"
                    >
                      Cancel
                    </button>
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default ContactsPage;
