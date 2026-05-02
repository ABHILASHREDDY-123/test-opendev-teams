import React, { useState, useEffect } from 'react';
import { apiClient, Contact } from './api';
import './ContactsPage.css';

interface ContactsPageProps {
  onLogout: () => void;
}

export const ContactsPage: React.FC<ContactsPageProps> = ({ onLogout }) => {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [name, setName] = useState('');
  const [mobile, setMobile] = useState('');
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);

  useEffect(() => {
    fetchContacts();
  }, []);

  const fetchContacts = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await apiClient.getContacts();
      setContacts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load contacts');
    } finally {
      setLoading(false);
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!mobile) {
      newErrors.mobile = 'Mobile number is required';
    } else if (!/^\d+$/.test(mobile)) {
      newErrors.mobile = 'Mobile number must contain only digits';
    } else if (mobile.length < 10) {
      newErrors.mobile = 'Mobile number must be at least 10 digits';
    }

    setFormErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleAddContact = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setSubmitting(true);
    try {
      const newContact = await apiClient.createContact(name, mobile);
      setContacts([...contacts, newContact]);
      setName('');
      setMobile('');
      setFormErrors({});
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add contact');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteContact = async (id: string) => {
    setDeleting(id);
    try {
      await apiClient.deleteContact(id);
      setContacts(contacts.filter((c) => c.id !== id));
      setDeleteConfirm(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete contact');
    } finally {
      setDeleting(null);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('jwt_token');
    onLogout();
  };

  return (
    <div className="contacts-container">
      <div className="contacts-header">
        <h1>My Contacts</h1>
        <button onClick={handleLogout} className="logout-button">
          Logout
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="contacts-content">
        <div className="add-contact-section">
          <h2>Add New Contact</h2>
          <form onSubmit={handleAddContact} className="add-contact-form">
            <div className="form-group">
              <label htmlFor="name">Name</label>
              <input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter contact name"
                disabled={submitting}
                aria-invalid={!!formErrors.name}
                aria-describedby={formErrors.name ? 'name-error' : undefined}
              />
              {formErrors.name && (
                <span id="name-error" className="field-error">
                  {formErrors.name}
                </span>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="mobile">Mobile Number</label>
              <input
                id="mobile"
                type="text"
                value={mobile}
                onChange={(e) => setMobile(e.target.value)}
                placeholder="Enter 10+ digit mobile number"
                disabled={submitting}
                aria-invalid={!!formErrors.mobile}
                aria-describedby={formErrors.mobile ? 'mobile-error' : undefined}
              />
              {formErrors.mobile && (
                <span id="mobile-error" className="field-error">
                  {formErrors.mobile}
                </span>
              )}
            </div>

            <button type="submit" disabled={submitting} className="submit-button">
              {submitting ? 'Adding...' : 'Add Contact'}
            </button>
          </form>
        </div>

        <div className="contacts-list-section">
          <h2>Contacts List</h2>
          {loading ? (
            <div className="loading">Loading contacts...</div>
          ) : contacts.length === 0 ? (
            <div className="empty-state">No contacts yet. Add one above!</div>
          ) : (
            <ul className="contacts-list">
              {contacts.map((contact) => (
                <li key={contact.id} className="contact-item">
                  <div className="contact-info">
                    <div className="contact-name">{contact.name}</div>
                    <div className="contact-mobile">{contact.mobile}</div>
                  </div>
                  <div className="contact-actions">
                    {deleteConfirm === contact.id ? (
                      <div className="delete-confirm">
                        <span>Delete this contact?</span>
                        <button
                          onClick={() => handleDeleteContact(contact.id)}
                          disabled={deleting === contact.id}
                          className="confirm-yes"
                        >
                          {deleting === contact.id ? 'Deleting...' : 'Yes'}
                        </button>
                        <button
                          onClick={() => setDeleteConfirm(null)}
                          disabled={deleting === contact.id}
                          className="confirm-no"
                        >
                          No
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => setDeleteConfirm(contact.id)}
                        className="delete-button"
                      >
                        Delete
                      </button>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};
