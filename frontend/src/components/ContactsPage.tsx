import React, { useState, useEffect } from 'react';
import { apiClient, Contact } from '../services/apiClient';

interface ContactsPageProps {
  onLogout: () => void;
}

interface AddContactForm {
  name: string;
  mobile: string;
}

interface PageState {
  contacts: Contact[];
  loading: boolean;
  error?: string;
  addingContact: boolean;
}

export const ContactsPage: React.FC<ContactsPageProps> = ({ onLogout }) => {
  const [state, setState] = useState<PageState>({
    contacts: [],
    loading: true,
    addingContact: false,
  });

  const [formData, setFormData] = useState<AddContactForm>({
    name: '',
    mobile: '',
  });

  const [formErrors, setFormErrors] = useState<Partial<AddContactForm>>({});

  /**
   * Fetch contacts on component mount
   */
  useEffect(() => {
    fetchContacts();
  }, []);

  /**
   * Fetch user's contacts from API
   */
  const fetchContacts = async () => {
    setState((prev) => ({ ...prev, loading: true, error: undefined }));

    const result = await apiClient.getContacts();

    if (result.error) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: result.error,
        contacts: [],
      }));
    } else {
      setState((prev) => ({
        ...prev,
        loading: false,
        contacts: result.data || [],
      }));
    }
  };

  /**
   * Validate contact form
   */
  const validateForm = (): boolean => {
    const errors: Partial<AddContactForm> = {};

    if (!formData.name.trim()) {
      errors.name = 'Name is required';
    }

    if (!formData.mobile.trim()) {
      errors.mobile = 'Mobile number is required';
    } else {
      const digitsOnly = formData.mobile.replace(/\D/g, '');
      if (digitsOnly.length < 10) {
        errors.mobile = 'Mobile number must be at least 10 digits';
      }
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  /**
   * Handle add contact form submission
   */
  const handleAddContact = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setState((prev) => ({ ...prev, addingContact: true }));

    const digitsOnly = formData.mobile.replace(/\D/g, '');
    const result = await apiClient.createContact(formData.name, digitsOnly);

    if (result.error) {
      setState((prev) => ({
        ...prev,
        addingContact: false,
        error: result.error,
      }));
    } else {
      setState((prev) => ({
        ...prev,
        addingContact: false,
        contacts: [...prev.contacts, result.data!],
      }));
      setFormData({ name: '', mobile: '' });
      setFormErrors({});
    }
  };

  /**
   * Handle delete contact
   */
  const handleDeleteContact = async (id: string) => {
    const result = await apiClient.deleteContact(id);

    if (result.error) {
      setState((prev) => ({
        ...prev,
        error: result.error,
      }));
    } else {
      setState((prev) => ({
        ...prev,
        contacts: prev.contacts.filter((c) => c.id !== id),
      }));
    }
  };

  /**
   * Handle logout
   */
  const handleLogout = () => {
    apiClient.clearToken();
    onLogout();
  };

  if (state.loading) {
    return <div className="contacts-container"><p>Loading contacts...</p></div>;
  }

  return (
    <div className="contacts-container">
      <div className="contacts-header">
        <h1>My Contacts</h1>
        <button onClick={handleLogout} className="logout-button">
          Logout
        </button>
      </div>

      {state.error && (
        <div className="error-box">
          <p>{state.error}</p>
        </div>
      )}

      <div className="add-contact-section">
        <h2>Add New Contact</h2>
        <form onSubmit={handleAddContact} className="add-contact-form">
          <div className="form-group">
            <label htmlFor="name">Name</label>
            <input
              id="name"
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="Contact name"
              disabled={state.addingContact}
              className={formErrors.name ? 'input-error' : ''}
            />
            {formErrors.name && <span className="error-message">{formErrors.name}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="mobile">Mobile Number</label>
            <input
              id="mobile"
              type="tel"
              value={formData.mobile}
              onChange={(e) => setFormData({ ...formData, mobile: e.target.value })}
              placeholder="10+ digit mobile number"
              disabled={state.addingContact}
              className={formErrors.mobile ? 'input-error' : ''}
            />
            {formErrors.mobile && <span className="error-message">{formErrors.mobile}</span>}
          </div>

          <button type="submit" disabled={state.addingContact} className="submit-button">
            {state.addingContact ? 'Adding...' : 'Add Contact'}
          </button>
        </form>
      </div>

      <div className="contacts-list-section">
        <h2>Contacts</h2>
        {state.contacts.length === 0 ? (
          <p className="empty-state">No contacts yet. Add one above!</p>
        ) : (
          <ul className="contacts-list">
            {state.contacts.map((contact) => (
              <li key={contact.id} className="contact-item">
                <div className="contact-info">
                  <strong>{contact.name}</strong>
                  <span className="contact-mobile">{contact.mobile}</span>
                </div>
                <button
                  onClick={() => handleDeleteContact(contact.id)}
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
