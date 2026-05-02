import React, { useState, useEffect } from 'react';
import { Contact, getContacts, addContact, deleteContact } from './api';

interface ContactsPageProps {
  onLogout: () => void;
}

export const ContactsPage: React.FC<ContactsPageProps> = ({ onLogout }) => {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [formName, setFormName] = useState('');
  const [formMobile, setFormMobile] = useState('');
  const [formError, setFormError] = useState('');
  const [formLoading, setFormLoading] = useState(false);
  const [deleteError, setDeleteError] = useState('');

  useEffect(() => {
    fetchContacts();
  }, []);

  const fetchContacts = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getContacts();
      setContacts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load contacts');
    } finally {
      setLoading(false);
    }
  };

  const validateMobile = (value: string): boolean => {
    const digitsOnly = value.replace(/\D/g, '');
    return digitsOnly.length >= 10;
  };

  const handleAddContact = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');

    if (!formName.trim()) {
      setFormError('Name is required');
      return;
    }

    if (!validateMobile(formMobile)) {
      setFormError('Mobile must be at least 10 digits');
      return;
    }

    setFormLoading(true);
    try {
      const newContact = await addContact(formName, formMobile);
      setContacts([...contacts, newContact]);
      setFormName('');
      setFormMobile('');
      setShowForm(false);
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Failed to add contact');
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteContact = async (id: string) => {
    setDeleteError('');
    try {
      await deleteContact(id);
      setContacts(contacts.filter(c => c.id !== id));
    } catch (err) {
      setDeleteError(err instanceof Error ? err.message : 'Failed to delete contact');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    onLogout();
  };

  const handleMobileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '');
    setFormMobile(value);
  };

  const isMobileValid = validateMobile(formMobile);
  const isFormValid = formName.trim().length > 0 && isMobileValid;

  return (
    <div className="contacts-container">
      <div className="contacts-header">
        <h1>My Contacts</h1>
        <button onClick={handleLogout} className="logout-btn" data-testid="logout-button">
          Logout
        </button>
      </div>

      {error && (
        <div className="error-message" data-testid="error-message">
          {error}
        </div>
      )}

      {deleteError && (
        <div className="error-message" data-testid="delete-error">
          {deleteError}
        </div>
      )}

      <button
        onClick={() => setShowForm(!showForm)}
        className="add-contact-btn"
        data-testid="add-contact-button"
      >
        {showForm ? 'Cancel' : 'Add Contact'}
      </button>

      {showForm && (
        <form onSubmit={handleAddContact} className="add-contact-form" data-testid="add-contact-form">
          <div className="form-group">
            <label htmlFor="name">Name</label>
            <input
              id="name"
              type="text"
              placeholder="Contact name"
              value={formName}
              onChange={(e) => setFormName(e.target.value)}
              disabled={formLoading}
              data-testid="contact-name-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="mobile">Mobile</label>
            <input
              id="mobile"
              type="text"
              inputMode="numeric"
              placeholder="10+ digit mobile"
              value={formMobile}
              onChange={handleMobileChange}
              disabled={formLoading}
              data-testid="contact-mobile-input"
            />
            {formMobile && !isMobileValid && (
              <span className="error-text" data-testid="mobile-error">
                Mobile must be at least 10 digits
              </span>
            )}
          </div>

          {formError && (
            <div className="error-message" data-testid="form-error">
              {formError}
            </div>
          )}

          <button
            type="submit"
            disabled={!isFormValid || formLoading}
            data-testid="submit-contact-button"
          >
            {formLoading ? 'Adding...' : 'Add Contact'}
          </button>
        </form>
      )}

      {loading ? (
        <div className="loading" data-testid="loading-indicator">Loading contacts...</div>
      ) : contacts.length === 0 ? (
        <div className="empty-state" data-testid="empty-state">
          No contacts yet. Add one to get started!
        </div>
      ) : (
        <div className="contacts-list">
          {contacts.map((contact) => (
            <div key={contact.id} className="contact-item" data-testid={`contact-${contact.id}`}>
              <div className="contact-info">
                <div className="contact-name" data-testid={`contact-name-${contact.id}`}>
                  {contact.name}
                </div>
                <div className="contact-mobile" data-testid={`contact-mobile-${contact.id}`}>
                  {contact.mobile}
                </div>
              </div>
              <button
                onClick={() => handleDeleteContact(contact.id)}
                className="delete-btn"
                data-testid={`delete-button-${contact.id}`}
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}

      <style>{`
        .contacts-container {
          max-width: 600px;
          margin: 0 auto;
          padding: 20px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
          min-height: 100vh;
          background: #f5f5f5;
        }

        .contacts-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 30px;
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .contacts-header h1 {
          margin: 0;
          color: #333;
          font-size: 24px;
        }

        .logout-btn {
          background: #e74c3c;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 600;
          transition: background 0.3s;
        }

        .logout-btn:hover {
          background: #c0392b;
        }

        .add-contact-btn {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 16px;
          font-weight: 600;
          margin-bottom: 20px;
          width: 100%;
          transition: transform 0.2s;
        }

        .add-contact-btn:hover {
          transform: translateY(-2px);
        }

        .add-contact-form {
          background: white;
          padding: 20px;
          border-radius: 8px;
          margin-bottom: 20px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .form-group {
          margin-bottom: 16px;
        }

        .form-group label {
          display: block;
          margin-bottom: 6px;
          color: #555;
          font-weight: 500;
          font-size: 14px;
        }

        .form-group input {
          width: 100%;
          padding: 10px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 14px;
          box-sizing: border-box;
        }

        .form-group input:focus {
          outline: none;
          border-color: #667eea;
        }

        .error-text {
          display: block;
          color: #e74c3c;
          font-size: 12px;
          margin-top: 4px;
        }

        .error-message {
          background-color: #fee;
          border: 1px solid #fcc;
          color: #c33;
          padding: 12px;
          border-radius: 4px;
          margin-bottom: 16px;
          font-size: 14px;
        }

        .add-contact-form button {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border: none;
          padding: 10px 20px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 600;
          width: 100%;
          transition: transform 0.2s;
        }

        .add-contact-form button:hover:not(:disabled) {
          transform: translateY(-2px);
        }

        .add-contact-form button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .loading {
          text-align: center;
          padding: 40px 20px;
          color: #666;
          font-size: 16px;
        }

        .empty-state {
          text-align: center;
          padding: 60px 20px;
          color: #999;
          font-size: 16px;
          background: white;
          border-radius: 8px;
          border: 2px dashed #ddd;
        }

        .contacts-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .contact-item {
          background: white;
          padding: 16px;
          border-radius: 8px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          transition: box-shadow 0.3s;
        }

        .contact-item:hover {
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }

        .contact-info {
          flex: 1;
        }

        .contact-name {
          font-weight: 600;
          color: #333;
          font-size: 16px;
          margin-bottom: 4px;
        }

        .contact-mobile {
          color: #666;
          font-size: 14px;
        }

        .delete-btn {
          background: #e74c3c;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 600;
          transition: background 0.3s;
          margin-left: 12px;
        }

        .delete-btn:hover {
          background: #c0392b;
        }
      `}</style>
    </div>
  );
};
