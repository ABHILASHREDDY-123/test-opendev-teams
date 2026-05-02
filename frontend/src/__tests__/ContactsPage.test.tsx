import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ContactsPage } from '../ContactsPage';
import * as api from '../api';

jest.mock('../api');

describe('ContactsPage', () => {
  const mockOnLogout = jest.fn();
  const mockContacts = [
    { id: '1', name: 'John Doe', mobile: '9876543210' },
    { id: '2', name: 'Jane Smith', mobile: '9876543211' },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    localStorage.setItem('authToken', 'test-token');
  });

  it('should render contacts page', async () => {
    (api.getContacts as jest.Mock).mockResolvedValueOnce(mockContacts);

    render(<ContactsPage onLogout={mockOnLogout} />);

    await waitFor(() => {
      expect(screen.getByTestId('contacts-page')).toBeInTheDocument();
      expect(screen.getByTestId('logout-button')).toBeInTheDocument();
    });
  });

  it('should load and display contacts on mount', async () => {
    (api.getContacts as jest.Mock).mockResolvedValueOnce(mockContacts);

    render(<ContactsPage onLogout={mockOnLogout} />);

    expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByTestId('contacts-list')).toBeInTheDocument();
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });
  });

  it('should display empty state when no contacts', async () => {
    (api.getContacts as jest.Mock).mockResolvedValueOnce([]);

    render(<ContactsPage onLogout={mockOnLogout} />);

    await waitFor(() => {
      expect(screen.getByTestId('empty-state')).toHaveTextContent('No contacts yet. Add one above!');
    });
  });

  it('should validate name - required', async () => {
    (api.getContacts as jest.Mock).mockResolvedValueOnce(mockContacts);

    render(<ContactsPage onLogout={mockOnLogout} />);

    await waitFor(() => {
      expect(screen.getByTestId('contacts-list')).toBeInTheDocument();
    });

    const addButton = screen.getByTestId('add-contact-button');
    fireEvent.click(addButton);

    await waitFor(() => {
      expect(screen.getByTestId('name-error')).toHaveTextContent('Name is required');
    });
  });

  it('should validate mobile - required', async () => {
    (api.getContacts as jest.Mock).mockResolvedValueOnce(mockContacts);

    render(<ContactsPage onLogout={mockOnLogout} />);

    await waitFor(() => {
      expect(screen.getByTestId('contacts-list')).toBeInTheDocument();
    });

    const nameInput = screen.getByTestId('add-name-input');
    fireEvent.change(nameInput, { target: { value: 'Bob' } });

    const addButton = screen.getByTestId('add-contact-button');
    fireEvent.click(addButton);

    await waitFor(() => {
      expect(screen.getByTestId('mobile-error')).toHaveTextContent('Mobile number is required');
    });
  });

  it('should validate mobile - digits only', async () => {
    (api.getContacts as jest.Mock).mockResolvedValueOnce(mockContacts);

    render(<ContactsPage onLogout={mockOnLogout} />);

    await waitFor(() => {
      expect(screen.getByTestId('contacts-list')).toBeInTheDocument();
    });

    const nameInput = screen.getByTestId('add-name-input');
    const mobileInput = screen.getByTestId('add-mobile-input');

    fireEvent.change(nameInput, { target: { value: 'Bob' } });
    fireEvent.change(mobileInput, { target: { value: 'abc1234567' } });

    const addButton = screen.getByTestId('add-contact-button');
    fireEvent.click(addButton);

    await waitFor(() => {
      expect(screen.getByTestId('mobile-error')).toHaveTextContent('Mobile number must contain only digits');
    });
  });

  it('should validate mobile - minimum 10 digits', async () => {
    (api.getContacts as jest.Mock).mockResolvedValueOnce(mockContacts);

    render(<ContactsPage onLogout={mockOnLogout} />);

    await waitFor(() => {
      expect(screen.getByTestId('contacts-list')).toBeInTheDocument();
    });

    const nameInput = screen.getByTestId('add-name-input');
    const mobileInput = screen.getByTestId('add-mobile-input');

    fireEvent.change(nameInput, { target: { value: 'Bob' } });
    fireEvent.change(mobileInput, { target: { value: '123456789' } });

    const addButton = screen.getByTestId('add-contact-button');
    fireEvent.click(addButton);

    await waitFor(() => {
      expect(screen.getByTestId('mobile-error')).toHaveTextContent('Mobile number must be at least 10 digits');
    });
  });

  it('should successfully add a contact', async () => {
    (api.getContacts as jest.Mock).mockResolvedValueOnce(mockContacts);
    const newContact = { id: '3', name: 'Bob Wilson', mobile: '9876543212' };
    (api.addContact as jest.Mock).mockResolvedValueOnce(newContact);

    render(<ContactsPage onLogout={mockOnLogout} />);

    await waitFor(() => {
      expect(screen.getByTestId('contacts-list')).toBeInTheDocument();
    });

    const nameInput = screen.getByTestId('add-name-input');
    const mobileInput = screen.getByTestId('add-mobile-input');
    const addButton = screen.getByTestId('add-contact-button');

    fireEvent.change(nameInput, { target: { value: 'Bob Wilson' } });
    fireEvent.change(mobileInput, { target: { value: '9876543212' } });
    fireEvent.click(addButton);

    await waitFor(() => {
      expect(api.addContact).toHaveBeenCalledWith('Bob Wilson', '9876543212');
      expect(screen.getByText('Bob Wilson')).toBeInTheDocument();
    });
  });

  it('should delete contact with confirmation', async () => {
    (api.getContacts as jest.Mock).mockResolvedValueOnce(mockContacts);
    (api.deleteContact as jest.Mock).mockResolvedValueOnce(undefined);

    window.confirm = jest.fn(() => true);

    render(<ContactsPage onLogout={mockOnLogout} />);

    await waitFor(() => {
      expect(screen.getByTestId('contacts-list')).toBeInTheDocument();
    });

    const deleteButton = screen.getByTestId('delete-button-1');
    fireEvent.click(deleteButton);

    await waitFor(() => {
      expect(window.confirm).toHaveBeenCalled();
      expect(api.deleteContact).toHaveBeenCalledWith('1');
      expect(screen.queryByText('John Doe')).not.toBeInTheDocument();
    });
  });

  it('should not delete contact if user cancels confirmation', async () => {
    (api.getContacts as jest.Mock).mockResolvedValueOnce(mockContacts);

    window.confirm = jest.fn(() => false);

    render(<ContactsPage onLogout={mockOnLogout} />);

    await waitFor(() => {
      expect(screen.getByTestId('contacts-list')).toBeInTheDocument();
    });

    const deleteButton = screen.getByTestId('delete-button-1');
    fireEvent.click(deleteButton);

    await waitFor(() => {
      expect(window.confirm).toHaveBeenCalled();
      expect(api.deleteContact).not.toHaveBeenCalled();
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
  });

  it('should logout and clear token', async () => {
    (api.getContacts as jest.Mock).mockResolvedValueOnce(mockContacts);

    render(<ContactsPage onLogout={mockOnLogout} />);

    await waitFor(() => {
      expect(screen.getByTestId('contacts-list')).toBeInTheDocument();
    });

    const logoutButton = screen.getByTestId('logout-button');
    fireEvent.click(logoutButton);

    expect(localStorage.getItem('authToken')).toBeNull();
    expect(mockOnLogout).toHaveBeenCalled();
  });

  it('should clear form after successful add', async () => {
    (api.getContacts as jest.Mock).mockResolvedValueOnce(mockContacts);
    const newContact = { id: '3', name: 'Bob Wilson', mobile: '9876543212' };
    (api.addContact as jest.Mock).mockResolvedValueOnce(newContact);

    render(<ContactsPage onLogout={mockOnLogout} />);

    await waitFor(() => {
      expect(screen.getByTestId('contacts-list')).toBeInTheDocument();
    });

    const nameInput = screen.getByTestId('add-name-input') as HTMLInputElement;
    const mobileInput = screen.getByTestId('add-mobile-input') as HTMLInputElement;
    const addButton = screen.getByTestId('add-contact-button');

    fireEvent.change(nameInput, { target: { value: 'Bob Wilson' } });
    fireEvent.change(mobileInput, { target: { value: '9876543212' } });
    fireEvent.click(addButton);

    await waitFor(() => {
      expect(nameInput.value).toBe('');
      expect(mobileInput.value).toBe('');
    });
  });
});
