import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ContactsPage } from '../ContactsPage';
import * as api from '../api';

jest.mock('../api');

describe('ContactsPage', () => {
  const mockOnLogout = jest.fn();
  const mockContacts = [
    { id: '1', name: 'John Doe', mobile: '9876543210' },
    { id: '2', name: 'Jane Smith', mobile: '9876543211' }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    localStorage.setItem('authToken', 'test-token');
  });

  describe('Rendering', () => {
    it('should render contacts page with header', async () => {
      (api.getContacts as jest.Mock).mockResolvedValue(mockContacts);

      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByText('My Contacts')).toBeInTheDocument();
      });
    });

    it('should render logout button', async () => {
      (api.getContacts as jest.Mock).mockResolvedValue(mockContacts);

      render(<ContactsPage onLogout={mockOnLogout} />);

      expect(screen.getByTestId('logout-button')).toBeInTheDocument();
    });

    it('should render add contact button', async () => {
      (api.getContacts as jest.Mock).mockResolvedValue(mockContacts);

      render(<ContactsPage onLogout={mockOnLogout} />);

      expect(screen.getByTestId('add-contact-button')).toBeInTheDocument();
    });
  });

  describe('Loading Contacts', () => {
    it('should show loading indicator initially', () => {
      (api.getContacts as jest.Mock).mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockContacts), 100))
      );

      render(<ContactsPage onLogout={mockOnLogout} />);

      expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();
    });

    it('should fetch contacts on mount', async () => {
      (api.getContacts as jest.Mock).mockResolvedValue(mockContacts);

      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(api.getContacts).toHaveBeenCalled();
      });
    });

    it('should display contacts after loading', async () => {
      (api.getContacts as jest.Mock).mockResolvedValue(mockContacts);

      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByTestId('contact-1')).toBeInTheDocument();
        expect(screen.getByTestId('contact-2')).toBeInTheDocument();
      });
    });

    it('should display contact names and mobiles', async () => {
      (api.getContacts as jest.Mock).mockResolvedValue(mockContacts);

      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByTestId('contact-name-1')).toHaveTextContent('John Doe');
        expect(screen.getByTestId('contact-mobile-1')).toHaveTextContent('9876543210');
        expect(screen.getByTestId('contact-name-2')).toHaveTextContent('Jane Smith');
        expect(screen.getByTestId('contact-mobile-2')).toHaveTextContent('9876543211');
      });
    });
  });

  describe('Empty State', () => {
    it('should show empty state when no contacts', async () => {
      (api.getContacts as jest.Mock).mockResolvedValue([]);

      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByTestId('empty-state')).toBeInTheDocument();
        expect(screen.getByTestId('empty-state')).toHaveTextContent('No contacts yet');
      });
    });
  });

  describe('Add Contact', () => {
    it('should show add contact form when button clicked', async () => {
      const user = userEvent.setup();
      (api.getContacts as jest.Mock).mockResolvedValue(mockContacts);

      render(<ContactsPage onLogout={mockOnLogout} />);

      const addButton = await screen.findByTestId('add-contact-button');
      await user.click(addButton);

      expect(screen.getByTestId('add-contact-form')).toBeInTheDocument();
    });

    it('should hide form when cancel button clicked', async () => {
      const user = userEvent.setup();
      (api.getContacts as jest.Mock).mockResolvedValue(mockContacts);

      render(<ContactsPage onLogout={mockOnLogout} />);

      const addButton = await screen.findByTestId('add-contact-button');
      await user.click(addButton);

      expect(screen.getByTestId('add-contact-form')).toBeInTheDocument();

      await user.click(addButton);
      expect(screen.queryByTestId('add-contact-form')).not.toBeInTheDocument();
    });

    it('should validate contact name is required', async () => {
      const user = userEvent.setup();
      (api.getContacts as jest.Mock).mockResolvedValue(mockContacts);

      render(<ContactsPage onLogout={mockOnLogout} />);

      const addButton = await screen.findByTestId('add-contact-button');
      await user.click(addButton);

      const mobileInput = screen.getByTestId('contact-mobile-input');
      const submitButton = screen.getByTestId('submit-contact-button');

      await user.type(mobileInput, '9876543210');

      expect(submitButton).toBeDisabled();
    });

    it('should validate contact mobile is 10+ digits', async () => {
      const user = userEvent.setup();
      (api.getContacts as jest.Mock).mockResolvedValue(mockContacts);

      render(<ContactsPage onLogout={mockOnLogout} />);

      const addButton = await screen.findByTestId('add-contact-button');
      await user.click(addButton);

      const nameInput = screen.getByTestId('contact-name-input');
      const mobileInput = screen.getByTestId('contact-mobile-input');

      await user.type(nameInput, 'New Contact');
      await user.type(mobileInput, '12345');

      expect(screen.getByTestId('mobile-error')).toBeInTheDocument();
    });

    it('should accept only digits in mobile field', async () => {
      const user = userEvent.setup();
      (api.getContacts as jest.Mock).mockResolvedValue(mockContacts);

      render(<ContactsPage onLogout={mockOnLogout} />);

      const addButton = await screen.findByTestId('add-contact-button');
      await user.click(addButton);

      const mobileInput = screen.getByTestId('contact-mobile-input') as HTMLInputElement;
      await user.type(mobileInput, '9876543210abc');

      expect(mobileInput.value).toBe('9876543210');
    });

    it('should call addContact API with correct data', async () => {
      const user = userEvent.setup();
      (api.getContacts as jest.Mock).mockResolvedValue(mockContacts);
      (api.addContact as jest.Mock).mockResolvedValue({
        id: '3',
        name: 'New Contact',
        mobile: '9876543212'
      });

      render(<ContactsPage onLogout={mockOnLogout} />);

      const addButton = await screen.findByTestId('add-contact-button');
      await user.click(addButton);

      const nameInput = screen.getByTestId('contact-name-input');
      const mobileInput = screen.getByTestId('contact-mobile-input');
      const submitButton = screen.getByTestId('submit-contact-button');

      await user.type(nameInput, 'New Contact');
      await user.type(mobileInput, '9876543212');
      await user.click(submitButton);

      await waitFor(() => {
        expect(api.addContact).toHaveBeenCalledWith('New Contact', '9876543212');
      });
    });

    it('should add new contact to list after successful submission', async () => {
      const user = userEvent.setup();
      (api.getContacts as jest.Mock).mockResolvedValue(mockContacts);
      (api.addContact as jest.Mock).mockResolvedValue({
        id: '3',
        name: 'New Contact',
        mobile: '9876543212'
      });

      render(<ContactsPage onLogout={mockOnLogout} />);

      const addButton = await screen.findByTestId('add-contact-button');
      await user.click(addButton);

      const nameInput = screen.getByTestId('contact-name-input');
      const mobileInput = screen.getByTestId('contact-mobile-input');
      const submitButton = screen.getByTestId('submit-contact-button');

      await user.type(nameInput, 'New Contact');
      await user.type(mobileInput, '9876543212');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByTestId('contact-3')).toBeInTheDocument();
      });
    });

    it('should show error on add contact failure', async () => {
      const user = userEvent.setup();
      (api.getContacts as jest.Mock).mockResolvedValue(mockContacts);
      (api.addContact as jest.Mock).mockRejectedValue(new Error('Failed to add contact'));

      render(<ContactsPage onLogout={mockOnLogout} />);

      const addButton = await screen.findByTestId('add-contact-button');
      await user.click(addButton);

      const nameInput = screen.getByTestId('contact-name-input');
      const mobileInput = screen.getByTestId('contact-mobile-input');
      const submitButton = screen.getByTestId('submit-contact-button');

      await user.type(nameInput, 'New Contact');
      await user.type(mobileInput, '9876543212');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByTestId('form-error')).toHaveTextContent('Failed to add contact');
      });
    });
  });

  describe('Delete Contact', () => {
    it('should render delete button for each contact', async () => {
      (api.getContacts as jest.Mock).mockResolvedValue(mockContacts);

      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByTestId('delete-button-1')).toBeInTheDocument();
        expect(screen.getByTestId('delete-button-2')).toBeInTheDocument();
      });
    });

    it('should call deleteContact API when delete button clicked', async () => {
      const user = userEvent.setup();
      (api.getContacts as jest.Mock).mockResolvedValue(mockContacts);
      (api.deleteContact as jest.Mock).mockResolvedValue(undefined);

      render(<ContactsPage onLogout={mockOnLogout} />);

      const deleteButton = await screen.findByTestId('delete-button-1');
      await user.click(deleteButton);

      await waitFor(() => {
        expect(api.deleteContact).toHaveBeenCalledWith('1');
      });
    });

    it('should remove contact from list after successful deletion', async () => {
      const user = userEvent.setup();
      (api.getContacts as jest.Mock).mockResolvedValue(mockContacts);
      (api.deleteContact as jest.Mock).mockResolvedValue(undefined);

      render(<ContactsPage onLogout={mockOnLogout} />);

      const deleteButton = await screen.findByTestId('delete-button-1');
      await user.click(deleteButton);

      await waitFor(() => {
        expect(screen.queryByTestId('contact-1')).not.toBeInTheDocument();
      });
    });

    it('should show error on delete contact failure', async () => {
      const user = userEvent.setup();
      (api.getContacts as jest.Mock).mockResolvedValue(mockContacts);
      (api.deleteContact as jest.Mock).mockRejectedValue(new Error('Failed to delete'));

      render(<ContactsPage onLogout={mockOnLogout} />);

      const deleteButton = await screen.findByTestId('delete-button-1');
      await user.click(deleteButton);

      await waitFor(() => {
        expect(screen.getByTestId('delete-error')).toHaveTextContent('Failed to delete');
      });
    });
  });

  describe('Logout', () => {
    it('should call onLogout when logout button clicked', async () => {
      const user = userEvent.setup();
      (api.getContacts as jest.Mock).mockResolvedValue(mockContacts);

      render(<ContactsPage onLogout={mockOnLogout} />);

      const logoutButton = await screen.findByTestId('logout-button');
      await user.click(logoutButton);

      expect(mockOnLogout).toHaveBeenCalled();
    });

    it('should clear auth token on logout', async () => {
      const user = userEvent.setup();
      (api.getContacts as jest.Mock).mockResolvedValue(mockContacts);

      render(<ContactsPage onLogout={mockOnLogout} />);

      const logoutButton = await screen.findByTestId('logout-button');
      await user.click(logoutButton);

      expect(localStorage.getItem('authToken')).toBeNull();
    });
  });

  describe('Error Handling', () => {
    it('should show error when fetching contacts fails', async () => {
      (api.getContacts as jest.Mock).mockRejectedValue(new Error('Network error'));

      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByTestId('error-message')).toHaveTextContent('Network error');
      });
    });
  });
});
