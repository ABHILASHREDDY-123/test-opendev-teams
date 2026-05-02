import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
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
    localStorage.setItem('jwt_token', 'test-token');
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('Rendering', () => {
    it('should render contacts page with header', () => {
      (api.apiClient.getContacts as jest.Mock).mockResolvedValue([]);

      render(<ContactsPage onLogout={mockOnLogout} />);

      expect(screen.getByText(/my contacts/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument();
    });

    it('should render add contact form', () => {
      (api.apiClient.getContacts as jest.Mock).mockResolvedValue([]);

      render(<ContactsPage onLogout={mockOnLogout} />);

      expect(screen.getByLabelText(/^name$/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/mobile number/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /add contact/i })).toBeInTheDocument();
    });
  });

  describe('Fetching Contacts', () => {
    it('should fetch and display contacts on mount', async () => {
      (api.apiClient.getContacts as jest.Mock).mockResolvedValue(mockContacts);

      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument();
        expect(screen.getByText('Jane Smith')).toBeInTheDocument();
      });
    });

    it('should display empty state when no contacts', async () => {
      (api.apiClient.getContacts as jest.Mock).mockResolvedValue([]);

      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByText(/no contacts yet/i)).toBeInTheDocument();
      });
    });

    it('should display error when fetching contacts fails', async () => {
      (api.apiClient.getContacts as jest.Mock).mockRejectedValue(
        new Error('Failed to fetch contacts')
      );

      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByText(/failed to fetch contacts/i)).toBeInTheDocument();
      });
    });

    it('should show loading state initially', () => {
      (api.apiClient.getContacts as jest.Mock).mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve([]), 100)
          )
      );

      render(<ContactsPage onLogout={mockOnLogout} />);

      expect(screen.getByText(/loading contacts/i)).toBeInTheDocument();
    });
  });

  describe('Add Contact Form Validation', () => {
    beforeEach(() => {
      (api.apiClient.getContacts as jest.Mock).mockResolvedValue([]);
    });

    it('should show error if name is empty', async () => {
      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByText(/no contacts yet/i)).toBeInTheDocument();
      });

      const submitButton = screen.getByRole('button', { name: /add contact/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/name is required/i)).toBeInTheDocument();
      });
    });

    it('should show error if mobile is empty', async () => {
      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByText(/no contacts yet/i)).toBeInTheDocument();
      });

      const nameInput = screen.getByLabelText(/^name$/i);
      await userEvent.type(nameInput, 'John Doe');

      const submitButton = screen.getByRole('button', { name: /add contact/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/mobile number is required/i)).toBeInTheDocument();
      });
    });

    it('should show error if mobile contains non-digits', async () => {
      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByText(/no contacts yet/i)).toBeInTheDocument();
      });

      const nameInput = screen.getByLabelText(/^name$/i);
      const mobileInput = screen.getByLabelText(/mobile number/i);

      await userEvent.type(nameInput, 'John Doe');
      await userEvent.type(mobileInput, '123abc4567');

      const submitButton = screen.getByRole('button', { name: /add contact/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/must contain only digits/i)).toBeInTheDocument();
      });
    });

    it('should show error if mobile is less than 10 digits', async () => {
      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByText(/no contacts yet/i)).toBeInTheDocument();
      });

      const nameInput = screen.getByLabelText(/^name$/i);
      const mobileInput = screen.getByLabelText(/mobile number/i);

      await userEvent.type(nameInput, 'John Doe');
      await userEvent.type(mobileInput, '123456789');

      const submitButton = screen.getByRole('button', { name: /add contact/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/at least 10 digits/i)).toBeInTheDocument();
      });
    });
  });

  describe('Add Contact API', () => {
    beforeEach(() => {
      (api.apiClient.getContacts as jest.Mock).mockResolvedValue([]);
    });

    it('should add contact and update list', async () => {
      const newContact = { id: '3', name: 'New Contact', mobile: '9876543212' };
      (api.apiClient.createContact as jest.Mock).mockResolvedValue(newContact);

      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByText(/no contacts yet/i)).toBeInTheDocument();
      });

      const nameInput = screen.getByLabelText(/^name$/i);
      const mobileInput = screen.getByLabelText(/mobile number/i);

      await userEvent.type(nameInput, 'New Contact');
      await userEvent.type(mobileInput, '9876543212');

      const submitButton = screen.getByRole('button', { name: /add contact/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(api.apiClient.createContact).toHaveBeenCalledWith(
          'New Contact',
          '9876543212'
        );
      });

      await waitFor(() => {
        expect(screen.getByText('New Contact')).toBeInTheDocument();
      });
    });

    it('should clear form after successful add', async () => {
      const newContact = { id: '3', name: 'New Contact', mobile: '9876543212' };
      (api.apiClient.createContact as jest.Mock).mockResolvedValue(newContact);

      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByText(/no contacts yet/i)).toBeInTheDocument();
      });

      const nameInput = screen.getByLabelText(/^name$/i) as HTMLInputElement;
      const mobileInput = screen.getByLabelText(/mobile number/i) as HTMLInputElement;

      await userEvent.type(nameInput, 'New Contact');
      await userEvent.type(mobileInput, '9876543212');

      const submitButton = screen.getByRole('button', { name: /add contact/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(nameInput.value).toBe('');
        expect(mobileInput.value).toBe('');
      });
    });

    it('should display error when adding contact fails', async () => {
      (api.apiClient.createContact as jest.Mock).mockRejectedValue(
        new Error('Failed to create contact')
      );

      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByText(/no contacts yet/i)).toBeInTheDocument();
      });

      const nameInput = screen.getByLabelText(/^name$/i);
      const mobileInput = screen.getByLabelText(/mobile number/i);

      await userEvent.type(nameInput, 'New Contact');
      await userEvent.type(mobileInput, '9876543212');

      const submitButton = screen.getByRole('button', { name: /add contact/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/failed to create contact/i)).toBeInTheDocument();
      });
    });
  });

  describe('Delete Contact', () => {
    beforeEach(() => {
      (api.apiClient.getContacts as jest.Mock).mockResolvedValue(mockContacts);
    });

    it('should show delete confirmation on delete button click', async () => {
      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument();
      });

      const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
      fireEvent.click(deleteButtons[0]);

      await waitFor(() => {
        expect(screen.getByText(/delete this contact/i)).toBeInTheDocument();
      });
    });

    it('should delete contact when confirmed', async () => {
      (api.apiClient.deleteContact as jest.Mock).mockResolvedValue(undefined);

      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument();
      });

      const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
      fireEvent.click(deleteButtons[0]);

      await waitFor(() => {
        expect(screen.getByText(/delete this contact/i)).toBeInTheDocument();
      });

      const confirmYesButton = screen.getByRole('button', { name: /^yes$/i });
      fireEvent.click(confirmYesButton);

      await waitFor(() => {
        expect(api.apiClient.deleteContact).toHaveBeenCalledWith('1');
      });

      await waitFor(() => {
        expect(screen.queryByText('John Doe')).not.toBeInTheDocument();
      });
    });

    it('should cancel delete when no is clicked', async () => {
      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument();
      });

      const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
      fireEvent.click(deleteButtons[0]);

      await waitFor(() => {
        expect(screen.getByText(/delete this contact/i)).toBeInTheDocument();
      });

      const confirmNoButton = screen.getByRole('button', { name: /^no$/i });
      fireEvent.click(confirmNoButton);

      await waitFor(() => {
        expect(screen.queryByText(/delete this contact/i)).not.toBeInTheDocument();
      });

      expect(api.apiClient.deleteContact).not.toHaveBeenCalled();
    });

    it('should display error when delete fails', async () => {
      (api.apiClient.deleteContact as jest.Mock).mockRejectedValue(
        new Error('Failed to delete contact')
      );

      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument();
      });

      const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
      fireEvent.click(deleteButtons[0]);

      await waitFor(() => {
        expect(screen.getByText(/delete this contact/i)).toBeInTheDocument();
      });

      const confirmYesButton = screen.getByRole('button', { name: /^yes$/i });
      fireEvent.click(confirmYesButton);

      await waitFor(() => {
        expect(screen.getByText(/failed to delete contact/i)).toBeInTheDocument();
      });
    });
  });

  describe('Logout', () => {
    beforeEach(() => {
      (api.apiClient.getContacts as jest.Mock).mockResolvedValue([]);
    });

    it('should clear JWT token on logout', async () => {
      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByText(/no contacts yet/i)).toBeInTheDocument();
      });

      const logoutButton = screen.getByRole('button', { name: /logout/i });
      fireEvent.click(logoutButton);

      expect(localStorage.getItem('jwt_token')).toBeNull();
    });

    it('should call onLogout callback', async () => {
      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByText(/no contacts yet/i)).toBeInTheDocument();
      });

      const logoutButton = screen.getByRole('button', { name: /logout/i });
      fireEvent.click(logoutButton);

      expect(mockOnLogout).toHaveBeenCalled();
    });
  });
});
