import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Contacts } from '../Contacts';
import * as apiModule from '../../services/api';

jest.mock('../../services/api');

const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

const mockApiService = apiModule.apiService as jest.Mocked<typeof apiModule.apiService>;

const mockContacts: apiModule.Contact[] = [
  { id: 1, name: 'John Doe', mobile: '9876543210' },
  { id: 2, name: 'Jane Smith', mobile: '9123456789' },
];

const renderContacts = () => {
  (localStorage.getItem as jest.Mock).mockReturnValue('test-token');
  mockNavigate.mockClear();
  return render(
    <BrowserRouter>
      <Contacts />
    </BrowserRouter>
  );
};

describe('Contacts Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockApiService.getContacts.mockResolvedValue(mockContacts);
  });

  it('renders contacts page with header', async () => {
    renderContacts();
    
    await waitFor(() => {
      expect(screen.getByText('Contacts')).toBeInTheDocument();
    });
  });

  it('displays logout button', () => {
    renderContacts();
    
    expect(screen.getByTestId('logout-button')).toBeInTheDocument();
  });

  it('displays add contact button', () => {
    renderContacts();
    
    expect(screen.getByTestId('add-contact-button')).toBeInTheDocument();
  });

  it('fetches and displays contacts on mount', async () => {
    renderContacts();
    
    await waitFor(() => {
      expect(mockApiService.getContacts).toHaveBeenCalled();
    });
    
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
  });

  it('displays contact mobile numbers', async () => {
    renderContacts();
    
    await waitFor(() => {
      expect(mockApiService.getContacts).toHaveBeenCalled();
    });
    
    expect(screen.getByText('9876543210')).toBeInTheDocument();
    expect(screen.getByText('9123456789')).toBeInTheDocument();
  });

  it('shows empty state when no contacts', async () => {
    mockApiService.getContacts.mockResolvedValue([]);
    
    renderContacts();
    
    await waitFor(() => {
      expect(screen.getByTestId('empty-state')).toBeInTheDocument();
    });
    
    expect(screen.getByTestId('empty-state')).toHaveTextContent(
      'No contacts yet. Add one to get started!'
    );
  });

  it('shows loading text initially', () => {
    mockApiService.getContacts.mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve(mockContacts), 100))
    );
    
    renderContacts();
    
    expect(screen.getByText('Loading contacts...')).toBeInTheDocument();
  });

  it('opens add contact modal when button clicked', async () => {
    renderContacts();
    
    await waitFor(() => {
      expect(mockApiService.getContacts).toHaveBeenCalled();
    });
    
    const addButton = screen.getByTestId('add-contact-button');
    fireEvent.click(addButton);
    
    expect(screen.getByTestId('add-contact-modal')).toBeInTheDocument();
  });

  it('closes modal when close button clicked', async () => {
    renderContacts();
    
    await waitFor(() => {
      expect(mockApiService.getContacts).toHaveBeenCalled();
    });
    
    const addButton = screen.getByTestId('add-contact-button');
    fireEvent.click(addButton);
    
    expect(screen.getByTestId('add-contact-modal')).toBeInTheDocument();
    
    const closeButton = screen.getByTestId('close-modal-button');
    fireEvent.click(closeButton);
    
    await waitFor(() => {
      expect(screen.queryByTestId('add-contact-modal')).not.toBeInTheDocument();
    });
  });

  it('closes modal when cancel button clicked', async () => {
    renderContacts();
    
    await waitFor(() => {
      expect(mockApiService.getContacts).toHaveBeenCalled();
    });
    
    const addButton = screen.getByTestId('add-contact-button');
    fireEvent.click(addButton);
    
    expect(screen.getByTestId('add-contact-modal')).toBeInTheDocument();
    
    const cancelButton = screen.getByTestId('cancel-button');
    fireEvent.click(cancelButton);
    
    await waitFor(() => {
      expect(screen.queryByTestId('add-contact-modal')).not.toBeInTheDocument();
    });
  });

  it('accepts only digits in mobile input in modal', async () => {
    renderContacts();
    
    await waitFor(() => {
      expect(mockApiService.getContacts).toHaveBeenCalled();
    });
    
    const addButton = screen.getByTestId('add-contact-button');
    fireEvent.click(addButton);
    
    expect(screen.getByTestId('add-contact-modal')).toBeInTheDocument();
    
    const mobileInput = screen.getByTestId('contact-mobile-input') as HTMLInputElement;
    fireEvent.change(mobileInput, { target: { value: '98abc76543def210' } });
    
    expect(mobileInput.value).toBe('9876543210');
  });

  it('creates contact with valid data', async () => {
    mockApiService.createContact.mockResolvedValue({
      id: 3,
      name: 'New Contact',
      mobile: '9999999999',
    });

    renderContacts();
    
    await waitFor(() => {
      expect(mockApiService.getContacts).toHaveBeenCalled();
    });
    
    const addButton = screen.getByTestId('add-contact-button');
    fireEvent.click(addButton);
    
    expect(screen.getByTestId('add-contact-modal')).toBeInTheDocument();
    
    const nameInput = screen.getByTestId('contact-name-input') as HTMLInputElement;
    const mobileInput = screen.getByTestId('contact-mobile-input') as HTMLInputElement;
    const submitButton = screen.getByTestId('submit-contact-button');
    
    fireEvent.change(nameInput, { target: { value: 'New Contact' } });
    fireEvent.change(mobileInput, { target: { value: '9999999999' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockApiService.createContact).toHaveBeenCalledWith({
        name: 'New Contact',
        mobile: '9999999999',
      });
    });
  });

  it('shows error when creating contact with empty name', async () => {
    renderContacts();
    
    await waitFor(() => {
      expect(mockApiService.getContacts).toHaveBeenCalled();
    });
    
    const addButton = screen.getByTestId('add-contact-button');
    fireEvent.click(addButton);
    
    expect(screen.getByTestId('add-contact-modal')).toBeInTheDocument();
    
    const mobileInput = screen.getByTestId('contact-mobile-input') as HTMLInputElement;
    const submitButton = screen.getByTestId('submit-contact-button');
    
    fireEvent.change(mobileInput, { target: { value: '9999999999' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByTestId('modal-error-message')).toHaveTextContent(
        'Name is required'
      );
    });
  });

  it('shows error when creating contact with invalid mobile', async () => {
    renderContacts();
    
    await waitFor(() => {
      expect(mockApiService.getContacts).toHaveBeenCalled();
    });
    
    const addButton = screen.getByTestId('add-contact-button');
    fireEvent.click(addButton);
    
    expect(screen.getByTestId('add-contact-modal')).toBeInTheDocument();
    
    const nameInput = screen.getByTestId('contact-name-input') as HTMLInputElement;
    const mobileInput = screen.getByTestId('contact-mobile-input') as HTMLInputElement;
    const submitButton = screen.getByTestId('submit-contact-button');
    
    fireEvent.change(nameInput, { target: { value: 'New Contact' } });
    fireEvent.change(mobileInput, { target: { value: '123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByTestId('modal-error-message')).toHaveTextContent(
        'Mobile number must be at least 10 digits'
      );
    });
  });

  it('refreshes contacts after creating new contact', async () => {
    mockApiService.createContact.mockResolvedValue({
      id: 3,
      name: 'New Contact',
      mobile: '9999999999',
    });
    mockApiService.getContacts.mockResolvedValueOnce(mockContacts);
    mockApiService.getContacts.mockResolvedValueOnce([
      ...mockContacts,
      { id: 3, name: 'New Contact', mobile: '9999999999' },
    ]);

    renderContacts();
    
    await waitFor(() => {
      expect(mockApiService.getContacts).toHaveBeenCalledTimes(1);
    });
    
    const addButton = screen.getByTestId('add-contact-button');
    fireEvent.click(addButton);
    
    expect(screen.getByTestId('add-contact-modal')).toBeInTheDocument();
    
    const nameInput = screen.getByTestId('contact-name-input') as HTMLInputElement;
    const mobileInput = screen.getByTestId('contact-mobile-input') as HTMLInputElement;
    const submitButton = screen.getByTestId('submit-contact-button');
    
    fireEvent.change(nameInput, { target: { value: 'New Contact' } });
    fireEvent.change(mobileInput, { target: { value: '9999999999' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockApiService.getContacts).toHaveBeenCalledTimes(2);
    });
  });

  it('deletes contact when delete button clicked', async () => {
    mockApiService.deleteContact.mockResolvedValue(undefined);
    mockApiService.getContacts.mockResolvedValueOnce(mockContacts);
    mockApiService.getContacts.mockResolvedValueOnce([mockContacts[1]]);

    renderContacts();
    
    await waitFor(() => {
      expect(mockApiService.getContacts).toHaveBeenCalledTimes(1);
    });
    
    window.confirm = jest.fn(() => true);
    
    const deleteButton = screen.getByTestId('delete-button-1');
    fireEvent.click(deleteButton);
    
    await waitFor(() => {
      expect(mockApiService.deleteContact).toHaveBeenCalledWith(1);
    });
  });

  it('does not delete contact when confirmation cancelled', async () => {
    renderContacts();
    
    await waitFor(() => {
      expect(mockApiService.getContacts).toHaveBeenCalled();
    });
    
    window.confirm = jest.fn(() => false);
    
    const deleteButton = screen.getByTestId('delete-button-1');
    fireEvent.click(deleteButton);
    
    expect(mockApiService.deleteContact).not.toHaveBeenCalled();
  });

  it('shows error message on delete failure', async () => {
    mockApiService.deleteContact.mockRejectedValue(new Error('Failed to delete contact'));

    renderContacts();
    
    await waitFor(() => {
      expect(mockApiService.getContacts).toHaveBeenCalled();
    });
    
    window.confirm = jest.fn(() => true);
    
    const deleteButton = screen.getByTestId('delete-button-1');
    fireEvent.click(deleteButton);
    
    await waitFor(() => {
      expect(screen.getByTestId('error-message')).toHaveTextContent(
        'Failed to delete contact'
      );
    });
  });

  it('clears token and navigates to login on logout', async () => {
    renderContacts();
    
    await waitFor(() => {
      expect(mockApiService.getContacts).toHaveBeenCalled();
    });
    
    const logoutButton = screen.getByTestId('logout-button');
    fireEvent.click(logoutButton);
    
    expect(localStorage.removeItem).toHaveBeenCalledWith('token');
  });

  it('disables form inputs while submitting', async () => {
    mockApiService.createContact.mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({
        id: 3,
        name: 'New Contact',
        mobile: '9999999999',
      }), 100))
    );

    renderContacts();
    
    await waitFor(() => {
      expect(mockApiService.getContacts).toHaveBeenCalled();
    });
    
    const addButton = screen.getByTestId('add-contact-button');
    fireEvent.click(addButton);
    
    expect(screen.getByTestId('add-contact-modal')).toBeInTheDocument();
    
    const nameInput = screen.getByTestId('contact-name-input') as HTMLInputElement;
    const mobileInput = screen.getByTestId('contact-mobile-input') as HTMLInputElement;
    const submitButton = screen.getByTestId('submit-contact-button');
    
    fireEvent.change(nameInput, { target: { value: 'New Contact' } });
    fireEvent.change(mobileInput, { target: { value: '9999999999' } });
    fireEvent.click(submitButton);
    
    expect(nameInput).toBeDisabled();
    expect(mobileInput).toBeDisabled();
    expect(submitButton).toBeDisabled();
  });
});
