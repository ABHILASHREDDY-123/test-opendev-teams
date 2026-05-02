import React, { useState, useEffect } from 'react';
import { getContacts, addContact, deleteContact, clearToken, Contact } from './api';

interface ContactsPageProps {
  onLogout: () => void;
}

/**
 * ContactsPage Component
 * Displays user's contacts with add/delete functionality
 */
export const ContactsPage: React.FC<ContactsPageProps> = ({ onLogout }) => {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Form state
  const [name, setName] = useState('');
  const [mobile, setMobile] = useState('');
  const [nameError, setNameError] = useState('');
  const [mobileError, setMobileError] = useState('');
  const [addingContact, setAddingContact] = useState(false);

  /**
   * Fetch contacts on component mount
   */
  useEffect(() => {
    fetchContacts();
  }, []);

  /**
   * Fetch all contacts
   */
  const fetchContacts = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await getContacts();
      setContacts(data);
    } catch (err) {
      if (err instanceof Error) {
        if (err.message === 'Unauthorized') {
          handleLogout();
        } else {
          setError(err.message || 'Failed to fetch contacts');
        }
      } else {
        setError('Failed to fetch contacts');
      }
    } finally {
      setLoading(false);
    }
  };

  /**
   * Validate contact name
   */
  const validateName = (value: string): boolean => {
    if (!value.trim()) {
      setNameError('Name is required');
      return false;
    }
    if (value.length < 2) {
      setNameError('Name must be at least 2 characters');
      return false;
    }
    setNameError('');
    return true;
  };

  /**
   * Validate mobile number: digits only, minimum 10 characters
   */
  const validateMobile = (value: string): boolean => {
    if (!value) {
      setMobileError('Mobile number is required');
      return false;
    }
    if (!/^\d+$/.test(value)) {
      setMobileError('Mobile number must contain only digits');
      return false;
    }
    if (value.length < 10) {
      setMobileError('Mobile number must be at least 10 digits');
      return false;
    }
    setMobileError('');
    return true;
  };

  /**
   * Handle name input change
   */
  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setName(value);
    if (value) {
      validateName(value);
    } else {
      setNameError('');
    }
  };

  /**
   * Handle mobile input change
   */
  const handleMobileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // Allow only digits
    const digitsOnly = value.replace(/\D/g, '');
    setMobile(digitsOnly);
    if (digitsOnly) {
      validateMobile(digitsOnly);
    } else {
      setMobileError('');
    }
  };

  /**
   * Handle add contact form submission
   */
  const handleAddContact = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');

    // Validate inputs
    const nameValid = validateName(name);
    const mobileValid = validateMobile(mobile);

    if (!nameValid || !mobileValid) {
      return;
    }

    setAddingContact(true);
    try {
      await addContact(name, mobile);
      setName('');
      setMobile('');
      setNameError('');
      setMobileError('');
      await fetchContacts();
    } catch (err) {
      if (err instanceof Error) {
        if (err.message === 'Unauthorized') {
          handleLogout();
        } else {
          setError(err.message || 'Failed to add contact');
        }
      } else {
        setError('Failed to add contact');
      }
    } finally {
      setAddingContact(false);
    }
  };

  /**
   * Handle delete contact
   */
  const handleDeleteContact = async (id: string) => {
    try {
      setError('');
      await deleteContact(id);
      await fetchContacts();
    } catch (err) {
      if (err instanceof Error) {
        if (err.message === 'Unauthorized') {
          handleLogout();
        } else {
          setError(err.message || 'Failed to delete contact');
        }
      } else {
        setError('Failed to delete contact');
      }
    }
  };

  /**
   * Handle logout
   */
  const handleLogout = () => {
    clearToken();
    onLogout();
  };

  if (loading) {
    return (
      <div className="contacts-container">
        <div className="loading">Loading contacts...</div>
      </div>
    );
  }

  return (
    <div className="contacts-container" data-testid="contacts-page">
      <div className="contacts-header">
        <h1>My Contacts</h1>
        <button
          onClick={handleLogout}
          data-testid="logout-button"
          className="logout-button"
        >
          Logout
        </button>
      </div>

      {error && (
        <div className="error-alert" data-testid="contacts-error">
          {error}
        </div>
      )}

      {/* Add Contact Form */}
      <div className="add-contact-section">
        <h2>Add New Contact</h2>
        <form onSubmit={handleAddContact} data-testid="add-contact-form">
          <div className="form-group">
            <label htmlFor="contact-name">Name</label>
            <input
              id="contact-name"
              type="text"
              placeholder="Enter contact name"
              value={name}
              onChange={handleNameChange}
              disabled={addingContact}
              data-testid="contact-name-input"
            />
            {nameError && (
              <span className="error-message" data-testid="contact-name-error">
                {nameError}
              </span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="contact-mobile">Mobile</label>
            <input
              id="contact-mobile"
              type="text"
              placeholder="Enter 10+ digit mobile number"
              value={mobile}
              onChange={handleMobileChange}
              disabled={addingContact}
              data-testid="contact-mobile-input"
              maxLength={15}
            />
            {mobileError && (
              <span className="error-message" data-testid="contact-mobile-error">
                {mobileError}
              </span>
            )}
          </div>

          <button
            type="submit"
            disabled={addingContact}
            data-testid="add-contact-button"
            className="submit-button"
          >
            {addingContact ? 'Adding...' : 'Add Contact'}
          </button>
        </form>
      </div>

      {/* Contacts List */}
      <div className="contacts-list-section">
        <h2>Contacts ({contacts.length})</h2>
        {contacts.length === 0 ? (
          <div className="empty-state" data-testid="empty-contacts">
            No contacts yet. Add one to get started!
          </div>
        ) : (
          <ul className="contacts-list" data-testid="contacts-list">
            {contacts.map((contact) => (
              <li key={contact.id} className="contact-item" data-testid={`contact-${contact.id}`}>
                <div className="contact-info">
                  <div className="contact-name">{contact.name}</div>
                  <div className="contact-mobile">{contact.mobile}</div>
                </div>
                <button
                  onClick={() => handleDeleteContact(contact.id)}
                  data-testid={`delete-contact-${contact.id}`}
                  className="delete-button"
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};
