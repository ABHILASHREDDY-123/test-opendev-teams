import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService, Contact } from '../services/api';

export const Contacts: React.FC = () => {
  const navigate = useNavigate();
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState('');
  const [mobile, setMobile] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }
    fetchContacts();
  }, [navigate]);

  const fetchContacts = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await apiService.getContacts();
      setContacts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch contacts');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const handleAddContact = () => {
    setName('');
    setMobile('');
    setError('');
    setShowModal(true);
  };

  const handleMobileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '');
    setMobile(value);
  };

  const validateForm = (): boolean => {
    if (!name.trim()) {
      setError('Name is required');
      return false;
    }
    if (mobile.length < 10) {
      setError('Mobile number must be at least 10 digits');
      return false;
    }
    return true;
  };

  const handleSubmitContact = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }

    setSubmitting(true);
    try {
      await apiService.createContact({ name, mobile });
      setShowModal(false);
      await fetchContacts();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create contact');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteContact = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this contact?')) {
      return;
    }

    try {
      await apiService.deleteContact(id);
      await fetchContacts();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete contact');
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Contacts</h1>
        <button
          onClick={handleLogout}
          style={styles.logoutButton}
          data-testid="logout-button"
        >
          Logout
        </button>
      </div>

      {error && (
        <div style={styles.errorBox} data-testid="error-message">
          {error}
        </div>
      )}

      <div style={styles.content}>
        <button
          onClick={handleAddContact}
          style={styles.addButton}
          data-testid="add-contact-button"
        >
          + Add Contact
        </button>

        {loading ? (
          <p style={styles.loadingText}>Loading contacts...</p>
        ) : contacts.length === 0 ? (
          <p style={styles.emptyText} data-testid="empty-state">
            No contacts yet. Add one to get started!
          </p>
        ) : (
          <div style={styles.contactsList} data-testid="contacts-list">
            {contacts.map((contact) => (
              <div key={contact.id} style={styles.contactCard}>
                <div style={styles.contactInfo}>
                  <h3 style={styles.contactName}>{contact.name}</h3>
                  <p style={styles.contactMobile}>{contact.mobile}</p>
                </div>
                <button
                  onClick={() => handleDeleteContact(contact.id)}
                  style={styles.deleteButton}
                  data-testid={`delete-button-${contact.id}`}
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {showModal && (
        <div style={styles.modal} data-testid="add-contact-modal">
          <div style={styles.modalContent}>
            <div style={styles.modalHeader}>
              <h2 style={styles.modalTitle}>Add Contact</h2>
              <button
                onClick={() => setShowModal(false)}
                style={styles.closeButton}
                data-testid="close-modal-button"
              >
                ×
              </button>
            </div>

            <form onSubmit={handleSubmitContact} style={styles.modalForm}>
              <div style={styles.formGroup}>
                <label htmlFor="name" style={styles.label}>
                  Name
                </label>
                <input
                  id="name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Enter contact name"
                  style={styles.input}
                  disabled={submitting}
                  data-testid="contact-name-input"
                />
              </div>

              <div style={styles.formGroup}>
                <label htmlFor="contact-mobile" style={styles.label}>
                  Mobile Number
                </label>
                <input
                  id="contact-mobile"
                  type="text"
                  value={mobile}
                  onChange={handleMobileChange}
                  placeholder="Enter 10+ digit mobile number"
                  style={styles.input}
                  disabled={submitting}
                  data-testid="contact-mobile-input"
                />
              </div>

              {error && (
                <div style={styles.errorBox} data-testid="modal-error-message">
                  {error}
                </div>
              )}

              <div style={styles.modalActions}>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  style={styles.cancelButton}
                  disabled={submitting}
                  data-testid="cancel-button"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={styles.submitButton}
                  disabled={submitting}
                  data-testid="submit-contact-button"
                >
                  {submitting ? 'Adding...' : 'Add'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
    padding: '20px',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '30px',
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
  },
  title: {
    margin: '0',
    color: '#333',
    fontSize: '28px',
  },
  logoutButton: {
    padding: '10px 20px',
    backgroundColor: '#d32f2f',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
  },
  content: {
    maxWidth: '800px',
    margin: '0 auto',
  },
  addButton: {
    padding: '12px 24px',
    backgroundColor: '#1976d2',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
    marginBottom: '20px',
  },
  loadingText: {
    textAlign: 'center',
    color: '#666',
    fontSize: '16px',
  },
  emptyText: {
    textAlign: 'center',
    color: '#999',
    fontSize: '16px',
    padding: '40px',
    backgroundColor: 'white',
    borderRadius: '8px',
  },
  contactsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  contactCard: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: 'white',
    padding: '16px',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
  },
  contactInfo: {
    flex: 1,
  },
  contactName: {
    margin: '0 0 4px 0',
    color: '#333',
    fontSize: '16px',
  },
  contactMobile: {
    margin: '0',
    color: '#666',
    fontSize: '14px',
  },
  deleteButton: {
    padding: '8px 16px',
    backgroundColor: '#d32f2f',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '14px',
    cursor: 'pointer',
  },
  errorBox: {
    backgroundColor: '#ffebee',
    color: '#d32f2f',
    padding: '12px',
    borderRadius: '4px',
    fontSize: '14px',
    marginBottom: '20px',
  },
  modal: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  modalContent: {
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '30px',
    width: '100%',
    maxWidth: '400px',
    boxShadow: '0 5px 20px rgba(0, 0, 0, 0.3)',
  },
  modalHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
  },
  modalTitle: {
    margin: '0',
    color: '#333',
    fontSize: '20px',
  },
  closeButton: {
    backgroundColor: 'transparent',
    border: 'none',
    fontSize: '28px',
    cursor: 'pointer',
    color: '#999',
  },
  modalForm: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  label: {
    fontWeight: '600',
    color: '#333',
    fontSize: '14px',
  },
  input: {
    padding: '10px 12px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '14px',
    fontFamily: 'inherit',
  },
  modalActions: {
    display: 'flex',
    gap: '12px',
    justifyContent: 'flex-end',
    marginTop: '20px',
  },
  cancelButton: {
    padding: '10px 20px',
    backgroundColor: '#e0e0e0',
    color: '#333',
    border: 'none',
    borderRadius: '4px',
    fontSize: '14px',
    cursor: 'pointer',
  },
  submitButton: {
    padding: '10px 20px',
    backgroundColor: '#1976d2',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
  },
};
