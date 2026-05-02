import React, { useState, useEffect } from 'react';
import { getContacts, addContact, deleteContact, Contact, APIError } from './api';

interface ContactsPageProps {
  onLogout: () => void;
}

export const ContactsPage: React.FC<ContactsPageProps> = ({ onLogout }) => {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [name, setName] = useState('');
  const [mobile, setMobile] = useState('');
  const [formErrors, setFormErrors] = useState<{ name?: string; mobile?: string }>({});
  const [addingContact, setAddingContact] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    loadContacts();
  }, []);

  const loadContacts = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await getContacts();
      setContacts(data);
    } catch (err) {
      if (err instanceof APIError) {
        setError(err.message);
      } else {
        setError('Failed to load contacts');
      }
    } finally {
      setLoading(false);
    }
  };

  const validateForm = (): boolean => {
    const newErrors: typeof formErrors = {};

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
    setError('');

    if (!validateForm()) {
      return;
    }

    setAddingContact(true);
    try {
      const newContact = await addContact(name, mobile);
      setContacts([...contacts, newContact]);
      setName('');
      setMobile('');
      setFormErrors({});
    } catch (err) {
      if (err instanceof APIError) {
        setError(err.message);
      } else {
        setError('Failed to add contact');
      }
    } finally {
      setAddingContact(false);
    }
  };

  const handleDeleteContact = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this contact?')) {
      return;
    }

    setDeletingId(id);
    try {
      await deleteContact(id);
      setContacts(contacts.filter((c) => c.id !== id));
    } catch (err) {
      if (err instanceof APIError) {
        setError(err.message);
      } else {
        setError('Failed to delete contact');
      }
    } finally {
      setDeletingId(null);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    onLogout();
  };

  return (
    <div data-testid="contacts-page" style={{ maxWidth: '600px', margin: '20px auto', padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>My Contacts</h1>
        <button onClick={handleLogout} data-testid="logout-button" style={{ padding: '8px 16px' }}>
          Logout
        </button>
      </div>

      {error && (
        <div data-testid="error-message" style={{ color: 'red', padding: '10px', backgroundColor: '#ffe0e0', borderRadius: '4px', marginBottom: '15px' }}>
          {error}
        </div>
      )}

      {loading && (
        <div data-testid="loading-indicator" style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
          Loading contacts...
        </div>
      )}

      {!loading && (
        <>
          <div style={{ marginBottom: '30px', padding: '15px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
            <h2>Add New Contact</h2>
            <form onSubmit={handleAddContact}>
              <div style={{ marginBottom: '10px' }}>
                <label htmlFor="name">Name:</label>
                <input
                  id="name"
                  type="text"
                  value={name}
                  onChange={(e) => {
                    setName(e.target.value);
                    setFormErrors((prev) => ({ ...prev, name: undefined }));
                  }}
                  placeholder="Enter contact name"
                  disabled={addingContact}
                  data-testid="add-name-input"
                />
                {formErrors.name && (
                  <div data-testid="name-error" style={{ color: 'red', fontSize: '12px', marginTop: '5px' }}>
                    {formErrors.name}
                  </div>
                )}
              </div>

              <div style={{ marginBottom: '10px' }}>
                <label htmlFor="mobile">Mobile:</label>
                <input
                  id="mobile"
                  type="text"
                  value={mobile}
                  onChange={(e) => {
                    setMobile(e.target.value);
                    setFormErrors((prev) => ({ ...prev, mobile: undefined }));
                  }}
                  placeholder="Enter 10+ digit mobile number"
                  disabled={addingContact}
                  data-testid="add-mobile-input"
                />
                {formErrors.mobile && (
                  <div data-testid="mobile-error" style={{ color: 'red', fontSize: '12px', marginTop: '5px' }}>
                    {formErrors.mobile}
                  </div>
                )}
              </div>

              <button type="submit" disabled={addingContact} data-testid="add-contact-button">
                {addingContact ? 'Adding...' : 'Add Contact'}
              </button>
            </form>
          </div>

          <div>
            <h2>Contacts List</h2>
            {contacts.length === 0 ? (
              <div data-testid="empty-state">No contacts yet. Add one above!</div>
            ) : (
              <ul data-testid="contacts-list" style={{ listStyle: 'none', padding: 0 }}>
                {contacts.map((contact) => (
                  <li
                    key={contact.id}
                    data-testid={`contact-item-${contact.id}`}
                    style={{
                      padding: '10px',
                      marginBottom: '10px',
                      backgroundColor: '#f9f9f9',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <div>
                      <strong>{contact.name}</strong>
                      <br />
                      <span style={{ color: '#666', fontSize: '14px' }}>{contact.mobile}</span>
                    </div>
                    <button
                      onClick={() => handleDeleteContact(contact.id)}
                      disabled={deletingId === contact.id}
                      data-testid={`delete-button-${contact.id}`}
                      style={{ padding: '6px 12px', backgroundColor: '#ff4444', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                    >
                      {deletingId === contact.id ? 'Deleting...' : 'Delete'}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </>
      )}
    </div>
  );
};
