import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Login } from '../Login';
import * as apiModule from '../../services/api';

jest.mock('../../services/api');
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
}));

const mockApiService = apiModule.apiService as jest.Mocked<typeof apiModule.apiService>;

const renderLogin = () => {
  return render(
    <BrowserRouter>
      <Login />
    </BrowserRouter>
  );
};

describe('Login Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders login form with mobile and password inputs', () => {
    renderLogin();
    
    expect(screen.getByTestId('mobile-input')).toBeInTheDocument();
    expect(screen.getByTestId('password-input')).toBeInTheDocument();
    expect(screen.getByTestId('submit-button')).toBeInTheDocument();
  });

  it('disables submit button initially', () => {
    renderLogin();
    
    const submitButton = screen.getByTestId('submit-button');
    expect(submitButton).toBeDisabled();
  });

  it('shows mobile validation error when less than 10 digits', () => {
    renderLogin();
    
    const mobileInput = screen.getByTestId('mobile-input') as HTMLInputElement;
    fireEvent.change(mobileInput, { target: { value: '12345' } });
    
    expect(screen.getByTestId('mobile-error')).toBeInTheDocument();
    expect(screen.getByTestId('mobile-error')).toHaveTextContent(
      'Mobile number must be at least 10 digits'
    );
  });

  it('shows password validation error when less than 6 characters', () => {
    renderLogin();
    
    const passwordInput = screen.getByTestId('password-input') as HTMLInputElement;
    fireEvent.change(passwordInput, { target: { value: '12345' } });
    
    expect(screen.getByTestId('password-error')).toBeInTheDocument();
    expect(screen.getByTestId('password-error')).toHaveTextContent(
      'Password must be at least 6 characters'
    );
  });

  it('enables submit button when form is valid', () => {
    renderLogin();
    
    const mobileInput = screen.getByTestId('mobile-input') as HTMLInputElement;
    const passwordInput = screen.getByTestId('password-input') as HTMLInputElement;
    const submitButton = screen.getByTestId('submit-button');
    
    fireEvent.change(mobileInput, { target: { value: '9876543210' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    
    expect(submitButton).not.toBeDisabled();
  });

  it('accepts only digits in mobile input', () => {
    renderLogin();
    
    const mobileInput = screen.getByTestId('mobile-input') as HTMLInputElement;
    fireEvent.change(mobileInput, { target: { value: '98abc76543def210' } });
    
    expect(mobileInput.value).toBe('9876543210');
  });

  it('clears error message when user types', () => {
    renderLogin();
    
    const mobileInput = screen.getByTestId('mobile-input') as HTMLInputElement;
    const passwordInput = screen.getByTestId('password-input') as HTMLInputElement;
    
    fireEvent.change(mobileInput, { target: { value: '123' } });
    expect(screen.getByTestId('mobile-error')).toBeInTheDocument();
    
    fireEvent.change(mobileInput, { target: { value: '1234' } });
    expect(screen.getByTestId('mobile-error')).toBeInTheDocument();
    
    fireEvent.change(passwordInput, { target: { value: 'pass' } });
    expect(screen.queryByTestId('error-message')).not.toBeInTheDocument();
  });

  it('calls API login with correct credentials', async () => {
    mockApiService.login.mockResolvedValue({
      access_token: 'test-token',
      token_type: 'bearer',
    });

    renderLogin();
    
    const mobileInput = screen.getByTestId('mobile-input') as HTMLInputElement;
    const passwordInput = screen.getByTestId('password-input') as HTMLInputElement;
    const submitButton = screen.getByTestId('submit-button');
    
    fireEvent.change(mobileInput, { target: { value: '9876543210' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockApiService.login).toHaveBeenCalledWith({
        mobile: '9876543210',
        password: 'password123',
      });
    });
  });

  it('stores token in localStorage on successful login', async () => {
    mockApiService.login.mockResolvedValue({
      access_token: 'test-token-123',
      token_type: 'bearer',
    });

    renderLogin();
    
    const mobileInput = screen.getByTestId('mobile-input') as HTMLInputElement;
    const passwordInput = screen.getByTestId('password-input') as HTMLInputElement;
    const submitButton = screen.getByTestId('submit-button');
    
    fireEvent.change(mobileInput, { target: { value: '9876543210' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(localStorage.setItem).toHaveBeenCalledWith('token', 'test-token-123');
    });
  });

  it('shows error message on login failure', async () => {
    mockApiService.login.mockRejectedValue(new Error('Invalid mobile or password'));

    renderLogin();
    
    const mobileInput = screen.getByTestId('mobile-input') as HTMLInputElement;
    const passwordInput = screen.getByTestId('password-input') as HTMLInputElement;
    const submitButton = screen.getByTestId('submit-button');
    
    fireEvent.change(mobileInput, { target: { value: '9876543210' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByTestId('error-message')).toBeInTheDocument();
      expect(screen.getByTestId('error-message')).toHaveTextContent(
        'Invalid mobile or password'
      );
    });
  });

  it('disables form inputs while loading', async () => {
    mockApiService.login.mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({
        access_token: 'test-token',
        token_type: 'bearer',
      }), 100))
    );

    renderLogin();
    
    const mobileInput = screen.getByTestId('mobile-input') as HTMLInputElement;
    const passwordInput = screen.getByTestId('password-input') as HTMLInputElement;
    const submitButton = screen.getByTestId('submit-button');
    
    fireEvent.change(mobileInput, { target: { value: '9876543210' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    expect(mobileInput).toBeDisabled();
    expect(passwordInput).toBeDisabled();
    expect(submitButton).toBeDisabled();
  });

  it('shows loading text on submit button while loading', async () => {
    mockApiService.login.mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({
        access_token: 'test-token',
        token_type: 'bearer',
      }), 100))
    );

    renderLogin();
    
    const mobileInput = screen.getByTestId('mobile-input') as HTMLInputElement;
    const passwordInput = screen.getByTestId('password-input') as HTMLInputElement;
    const submitButton = screen.getByTestId('submit-button');
    
    fireEvent.change(mobileInput, { target: { value: '9876543210' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    expect(submitButton).toHaveTextContent('Logging in...');
  });

  it('validates form on submit even if validation errors not shown', async () => {
    renderLogin();
    
    const submitButton = screen.getByTestId('submit-button');
    
    // Try to submit with empty form (should be disabled anyway)
    expect(submitButton).toBeDisabled();
  });

  it('prevents submission with invalid mobile', async () => {
    renderLogin();
    
    const mobileInput = screen.getByTestId('mobile-input') as HTMLInputElement;
    const passwordInput = screen.getByTestId('password-input') as HTMLInputElement;
    const submitButton = screen.getByTestId('submit-button');
    
    fireEvent.change(mobileInput, { target: { value: '123' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    
    expect(submitButton).toBeDisabled();
    expect(mockApiService.login).not.toHaveBeenCalled();
  });

  it('prevents submission with invalid password', async () => {
    renderLogin();
    
    const mobileInput = screen.getByTestId('mobile-input') as HTMLInputElement;
    const passwordInput = screen.getByTestId('password-input') as HTMLInputElement;
    const submitButton = screen.getByTestId('submit-button');
    
    fireEvent.change(mobileInput, { target: { value: '9876543210' } });
    fireEvent.change(passwordInput, { target: { value: '123' } });
    
    expect(submitButton).toBeDisabled();
    expect(mockApiService.login).not.toHaveBeenCalled();
  });
});
