import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ContactsPage } from '../ContactsPage';
import * as api from '../api';

// Mock the API module
jest.mock('../api');

describe('ContactsPage Component', () => {
  const mockOnLogout = jest.fn();
  const mockContacts = [
    { id: '1', name: 'John Doe', mobile: '9876543210' },
    { id: '2', name: 'Jane Smith', mobile: '9876543211' },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    (api.getContacts as jest.Mock).mockResolvedValue(mockContacts);
  });

  describe('Rendering', () => {
    it('should render contacts page with header', async () => {
      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByText('My Contacts')).toBeInTheDocument();
        expect(screen.getByTestId('logout-button')).toBeInTheDocument();
      });
    });

    it('should display loading state initially', () => {
      render(<ContactsPage onLogout={mockOnLogout} />);
      expect(screen.getByText('Loading contacts...')).toBeInTheDocument();
    });

    it('should fetch contacts on mount', async () => {
      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(api.getContacts).toHaveBeenCalled();
      });
    });
  });

  describe('Display Contacts', () => {
    it('should display list of contacts', async () => {
      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument();
        expect(screen.getByText('9876543210')).toBeInTheDocument();
        expect(screen.getByText('Jane Smith')).toBeInTheDocument();
        expect(screen.getByText('9876543211')).toBeInTheDocument();
      });
    });

    it('should display contact count', async () => {
      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByText('Contacts (2)')).toBeInTheDocument();
      });
    });

    it('should show empty state when no contacts', async () => {
      (api.getContacts as jest.Mock).mockResolvedValueOnce([]);

      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByTestId('empty-contacts')).toHaveTextContent(
          'No contacts yet'
        );
      });
    });

    it('should display delete button for each contact', async () => {
      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByTestId('delete-contact-1')).toBeInTheDocument();
        expect(screen.getByTestId('delete-contact-2')).toBeInTheDocument();
      });
    });
  });

  describe('Add Contact Form', () => {
    it('should render add contact form', async () => {
      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByTestId('add-contact-form')).toBeInTheDocument();
        expect(screen.getByTestId('contact-name-input')).toBeInTheDocument();
        expect(screen.getByTestId('contact-mobile-input')).toBeInTheDocument();
        expect(screen.getByTestId('add-contact-button')).toBeInTheDocument();
      });
    });

    it('should only allow digits in mobile input', async () => {
      const user = userEvent.setup();
      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByTestId('contact-mobile-input')).toBeInTheDocument();
      });

      const mobileInput = screen.getByTestId('contact-mobile-input') as HTMLInputElement;
      await user.type(mobileInput, '98765abc43210');

      expect(mobileInput.value).toBe('9876543210');
    });

    it('should show error for name less than 2 characters', async () => {
      const user = userEvent.setup();
      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByTestId('contact-name-input')).toBeInTheDocument();
      });

      const nameInput = screen.getByTestId('contact-name-input');
      await user.type(nameInput, 'A');

      await waitFor(() => {
        expect(screen.getByTestId('contact-name-error')).toHaveTextContent(
          'Name must be at least 2 characters'
        );
      });
    });

    it('should show error for empty name', async () => {
      const user = userEvent.setup();
      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByTestId('add-contact-button')).toBeInTheDocument();
      });

      const form = screen.getByTestId('add-contact-form');
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByTestId('contact-name-error')).toHaveTextContent(
          'Name is required'
        );
      });
    });

    it('should show error for mobile less than 10 digits', async () => {
      const user = userEvent.setup();
      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByTestId('contact-mobile-input')).toBeInTheDocument();
      });

      const mobileInput = screen.getByTestId('contact-mobile-input');
      await user.type(mobileInput, '987654321');

      await waitFor(() => {
        expect(screen.getByTestId('contact-mobile-error')).toHaveTextContent(
          'Mobile number must be at least 10 digits'
        );
      });
    });

    it('should show error for empty mobile', async () => {
      const user = userEvent.setup();
      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByTestId('add-contact-button')).toBeInTheDocument();
      });

      const form = screen.getByTestId('add-contact-form');
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByTestId('contact-mobile-error')).toHaveTextContent(
          'Mobile number is required'
        );
      });
    });

    it('should successfully add a new contact', async () => {
      const user = userEvent.setup();
      const newContact = { id: '3', name: 'Bob Johnson', mobile: '9876543212' };
      (api.addContact as jest.Mock).mockResolvedValueOnce(newContact);

      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByTestId('contact-name-input')).toBeInTheDocument();
      });

      await user.type(screen.getByTestId('contact-name-input'), 'Bob Johnson');
      await user.type(screen.getByTestId('contact-mobile-input'), '9876543212');
      await user.click(screen.getByTestId('add-contact-button'));

      await waitFor(() => {
        expect(api.addContact).toHaveBeenCalledWith('Bob Johnson', '9876543212');
        expect(api.getContacts).toHaveBeenCalledTimes(2); // Initial + after add
      });
    });

    it('should clear form after successful add', async () => {
      const user = userEvent.setup();
      (api.addContact as jest.Mock).mockResolvedValueOnce({
        id: '3',
        name: 'Bob Johnson',
        mobile: '9876543212',
      });

      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByTestId('contact-name-input')).toBeInTheDocument();
      });

      const nameInput = screen.getByTestId('contact-name-input') as HTMLInputElement;
      const mobileInput = screen.getByTestId('contact-mobile-input') as HTMLInputElement;

      await user.type(nameInput, 'Bob Johnson');
      await user.type(mobileInput, '9876543212');
      await user.click(screen.getByTestId('add-contact-button'));

      await waitFor(() => {
        expect(nameInput.value).toBe('');
        expect(mobileInput.value).toBe('');
      });
    });

    it('should show loading state during add', async () => {
      const user = userEvent.setup();
      (api.addContact as jest.Mock).mockImplementationOnce(
        () => new Promise((resolve) =>
          setTimeout(
            () => resolve({ id: '3', name: 'Bob Johnson', mobile: '9876543212' }),
            100
          )
        )
      );

      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByTestId('contact-name-input')).toBeInTheDocument();
      });

      await user.type(screen.getByTestId('contact-name-input'), 'Bob Johnson');
      await user.type(screen.getByTestId('contact-mobile-input'), '9876543212');
      await user.click(screen.getByTestId('add-contact-button'));

      expect(screen.getByTestId('add-contact-button')).toHaveTextContent('Adding...');

      await waitFor(() => {
        expect(screen.getByTestId('add-contact-button')).toHaveTextContent('Add Contact');
      });
    });

    it('should not submit form with invalid data', async () => {
      const user = userEvent.setup();
      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByTestId('add-contact-button')).toBeInTheDocument();
      });

      await user.type(screen.getByTestId('contact-name-input'), 'A');
      await user.type(screen.getByTestId('contact-mobile-input'), '123');
      await user.click(screen.getByTestId('add-contact-button'));

      await waitFor(() => {
        expect(api.addContact).not.toHaveBeenCalled();
      });
    });
  });

  describe('Delete Contact', () => {
    it('should delete a contact', async () => {
      const user = userEvent.setup();
      (api.deleteContact as jest.Mock).mockResolvedValueOnce(undefined);

      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByTestId('delete-contact-1')).toBeInTheDocument();
      });

      await user.click(screen.getByTestId('delete-contact-1'));

      await waitFor(() => {
        expect(api.deleteContact).toHaveBeenCalledWith('1');
        expect(api.getContacts).toHaveBeenCalledTimes(2); // Initial + after delete
      });
    });

    it('should handle delete error', async () => {
      const user = userEvent.setup();
      (api.deleteContact as jest.Mock).mockRejectedValueOnce(
        new Error('Delete failed')
      );

      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByTestId('delete-contact-1')).toBeInTheDocument();
      });

      await user.click(screen.getByTestId('delete-contact-1'));

      await waitFor(() => {
        expect(screen.getByTestId('contacts-error')).toHaveTextContent(
          'Delete failed'
        );
      });
    });
  });

  describe('Logout', () => {
    it('should logout when logout button is clicked', async () => {
      const user = userEvent.setup();
      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByTestId('logout-button')).toBeInTheDocument();
      });

      await user.click(screen.getByTestId('logout-button'));

      await waitFor(() => {
        expect(api.clearToken).toHaveBeenCalled();
        expect(mockOnLogout).toHaveBeenCalled();
      });
    });

    it('should logout on 401 error', async () => {
      (api.getContacts as jest.Mock).mockRejectedValueOnce(
        new Error('Unauthorized')
      );

      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(api.clearToken).toHaveBeenCalled();
        expect(mockOnLogout).toHaveBeenCalled();
      });
    });
  });

  describe('Error Handling', () => {
    it('should display error message on fetch failure', async () => {
      (api.getContacts as jest.Mock).mockRejectedValueOnce(
        new Error('Network error')
      );

      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByTestId('contacts-error')).toHaveTextContent(
          'Network error'
        );
      });
    });

    it('should display error message on add failure', async () => {
      const user = userEvent.setup();
      (api.addContact as jest.Mock).mockRejectedValueOnce(
        new Error('Add failed')
      );

      render(<ContactsPage onLogout={mockOnLogout} />);

      await waitFor(() => {
        expect(screen.getByTestId('contact-name-input')).toBeInTheDocument();
      });

      await user.type(screen.getByTestId('contact-name-input'), 'Bob Johnson');
      await user.type(screen.getByTestId('contact-mobile-input'), '9876543212');
      await user.click(screen.getByTestId('add-contact-button'));

      await waitFor(() => {
        expect(screen.getByTestId('contacts-error')).toHaveTextContent(
          'Add failed'
        );
      });
    });
  });
});
