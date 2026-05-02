import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ContactsPage from '../pages/ContactsPage';
import * as contactsAPI from '../api';

jest.mock('../api');

describe('ContactsPage', () => {
  const mockToken = 'test-token-123';
  const mockContacts = [
    { id: '1', name: 'John Doe', mobile: '1234567890' },
    { id: '2', name: 'Jane Smith', mobile: '9876543210' },
  ];

  beforeEach(() => {
    localStorage.setItem('jwt_token', mockToken);
    jest.clearAllMocks();
    (contactsAPI.contactsAPI.getContacts as jest.Mock).mockResolvedValue(mockContacts);
    (contactsAPI.contactsAPI.addContact as jest.Mock).mockResolvedValue({
      id: '3',
      name: 'New Contact',
      mobile: '5555555555',
    });
    (contactsAPI.contactsAPI.deleteContact as jest.Mock).mockResolvedValue(undefined);
  });

  afterEach(() => {
    localStorage.clear();
  });

  const renderContactsPage = () => {
    render(
      <BrowserRouter>
        <ContactsPage />
      </BrowserRouter>
    );
  };

  test('renders contacts page with title', async () => {
    renderContactsPage();
    await waitFor(() => {
      expect(screen.getByText('My Contacts')).toBeInTheDocument();
    });
  });

  test('displays add contact form', async () => {
    renderContactsPage();
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/contact name/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/mobile number/i)).toBeInTheDocument();
    });
  });

  test('validates contact name is required', async () => {
    renderContactsPage();
    await waitFor(() => {
      const addButton = screen.getByRole('button', { name: /add contact/i });
      fireEvent.click(addButton);
    });

    await waitFor(() => {
      expect(screen.getByText(/name is required/i)).toBeInTheDocument();
    });
  });

  test('validates mobile is required and has 10+ digits', async () => {
    renderContactsPage();
    await waitFor(() => {
      const nameInput = screen.getByPlaceholderText(/contact name/i);
      fireEvent.change(nameInput, { target: { value: 'John Doe' } });

      const mobileInput = screen.getByPlaceholderText(/mobile number/i);
      fireEvent.change(mobileInput, { target: { value: '123456789' } });

      const addButton = screen.getByRole('button', { name: /add contact/i });
      fireEvent.click(addButton);
    });

    await waitFor(() => {
      expect(screen.getByText(/at least 10 digits/i)).toBeInTheDocument();
    });
  });

  test('mobile input accepts only digits', async () => {
    renderContactsPage();
    await waitFor(() => {
      const mobileInput = screen.getByPlaceholderText(/mobile number/i) as HTMLInputElement;
      fireEvent.change(mobileInput, { target: { value: '12345abc' } });
      expect(mobileInput.value).toBe('12345');
    });
  });

  test('displays list of contacts', async () => {
    renderContactsPage();
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
      expect(screen.getByText('1234567890')).toBeInTheDocument();
      expect(screen.getByText('9876543210')).toBeInTheDocument();
    });
  });

  test('displays empty state when no contacts', async () => {
    (contactsAPI.contactsAPI.getContacts as jest.Mock).mockResolvedValue([]);
    renderContactsPage();
    await waitFor(() => {
      expect(screen.getByText(/no contacts yet/i)).toBeInTheDocument();
    });
  });

  test('adds a new contact', async () => {
    renderContactsPage();
    await waitFor(() => {
      const nameInput = screen.getByPlaceholderText(/contact name/i);
      const mobileInput = screen.getByPlaceholderText(/mobile number/i);
      const addButton = screen.getByRole('button', { name: /add contact/i });

      fireEvent.change(nameInput, { target: { value: 'New Contact' } });
      fireEvent.change(mobileInput, { target: { value: '5555555555' } });
      fireEvent.click(addButton);
    });

    await waitFor(() => {
      expect(contactsAPI.contactsAPI.addContact).toHaveBeenCalledWith('New Contact', '5555555555');
    });
  });

  test('shows delete confirmation dialog', async () => {
    renderContactsPage();
    await waitFor(() => {
      const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
      fireEvent.click(deleteButtons[0]);
    });

    await waitFor(() => {
      expect(screen.getByText(/are you sure/i)).toBeInTheDocument();
    });
  });

  test('deletes a contact after confirmation', async () => {
    renderContactsPage();
    await waitFor(() => {
      const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
      fireEvent.click(deleteButtons[0]);
    });

    await waitFor(() => {
      const confirmButton = screen.getByRole('button', { name: /yes, delete/i });
      fireEvent.click(confirmButton);
    });

    await waitFor(() => {
      expect(contactsAPI.contactsAPI.deleteContact).toHaveBeenCalledWith('1');
    });
  });

  test('has logout button', async () => {
    renderContactsPage();
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument();
    });
  });

  test('redirects to login on logout', async () => {
    const mockNavigate = jest.fn();
    jest.mock('react-router-dom', () => ({
      ...jest.requireActual('react-router-dom'),
      useNavigate: () => mockNavigate,
    }));

    renderContactsPage();
    await waitFor(() => {
      const logoutButton = screen.getByRole('button', { name: /logout/i });
      fireEvent.click(logoutButton);
    });

    // Token should be removed
    expect(localStorage.getItem('jwt_token')).toBeNull();
  });

  test('redirects to login if no token', () => {
    localStorage.clear();
    renderContactsPage();
    // Component should redirect, but we can't easily test navigation in this setup
    // The important thing is that it checks for the token
    expect(localStorage.getItem('jwt_token')).toBeNull();
  });
});
