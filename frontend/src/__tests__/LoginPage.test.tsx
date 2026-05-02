import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import LoginPage from '../pages/LoginPage';
import * as authAPI from '../api';

jest.mock('../api');

describe('LoginPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  const renderLoginPage = () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );
  };

  test('renders login form', () => {
    renderLoginPage();
    expect(screen.getByRole('heading', { name: /login/i })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/mobile/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  test('mobile input accepts only digits', () => {
    renderLoginPage();
    const mobileInput = screen.getByPlaceholderText(/mobile/i) as HTMLInputElement;

    fireEvent.change(mobileInput, { target: { value: '12345abc' } });
    expect(mobileInput.value).toBe('12345');
  });

  test('mobile input requires 10+ digits', () => {
    renderLoginPage();
    const mobileInput = screen.getByPlaceholderText(/mobile/i);
    const loginButton = screen.getByRole('button', { name: /login/i });

    fireEvent.change(mobileInput, { target: { value: '123456789' } });
    fireEvent.click(loginButton);

    expect(screen.getByText(/at least 10 digits/i)).toBeInTheDocument();
  });

  test('password input requires 6+ characters', () => {
    renderLoginPage();
    const mobileInput = screen.getByPlaceholderText(/mobile/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const loginButton = screen.getByRole('button', { name: /login/i });

    fireEvent.change(mobileInput, { target: { value: '1234567890' } });
    fireEvent.change(passwordInput, { target: { value: '12345' } });
    fireEvent.click(loginButton);

    expect(screen.getByText(/at least 6 characters/i)).toBeInTheDocument();
  });

  test('shows loading state during login', async () => {
    (authAPI.authAPI.login as jest.Mock).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve('test-token'), 100))
    );

    renderLoginPage();
    const mobileInput = screen.getByPlaceholderText(/mobile/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const loginButton = screen.getByRole('button', { name: /login/i });

    fireEvent.change(mobileInput, { target: { value: '1234567890' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /logging in/i })).toBeDisabled();
    });
  });

  test('shows error on login failure (401)', async () => {
    const error = new Error('Unauthorized');
    (error as any).response = { status: 401 };
    (authAPI.authAPI.login as jest.Mock).mockRejectedValue(error);

    renderLoginPage();
    const mobileInput = screen.getByPlaceholderText(/mobile/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const loginButton = screen.getByRole('button', { name: /login/i });

    fireEvent.change(mobileInput, { target: { value: '1234567890' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByText(/invalid mobile or password/i)).toBeInTheDocument();
    });
  });

  test('shows error on general login failure', async () => {
    (authAPI.authAPI.login as jest.Mock).mockRejectedValue(new Error('Network error'));

    renderLoginPage();
    const mobileInput = screen.getByPlaceholderText(/mobile/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const loginButton = screen.getByRole('button', { name: /login/i });

    fireEvent.change(mobileInput, { target: { value: '1234567890' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByText(/login failed/i)).toBeInTheDocument();
    });
  });

  test('stores token in localStorage on successful login', async () => {
    (authAPI.authAPI.login as jest.Mock).mockResolvedValue('test-token-123');

    renderLoginPage();
    const mobileInput = screen.getByPlaceholderText(/mobile/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const loginButton = screen.getByRole('button', { name: /login/i });

    fireEvent.change(mobileInput, { target: { value: '1234567890' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(localStorage.getItem('jwt_token')).toBe('test-token-123');
    });
  });

  test('disables button while loading', async () => {
    (authAPI.authAPI.login as jest.Mock).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve('test-token'), 200))
    );

    renderLoginPage();
    const mobileInput = screen.getByPlaceholderText(/mobile/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const loginButton = screen.getByRole('button', { name: /login/i });

    fireEvent.change(mobileInput, { target: { value: '1234567890' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(loginButton);

    expect(loginButton).toBeDisabled();

    await waitFor(() => {
      expect(loginButton).not.toBeDisabled();
    });
  });

  test('clears previous errors on input change', () => {
    renderLoginPage();
    const mobileInput = screen.getByPlaceholderText(/mobile/i);
    const loginButton = screen.getByRole('button', { name: /login/i });

    // Trigger validation error
    fireEvent.change(mobileInput, { target: { value: '123' } });
    fireEvent.click(loginButton);
    expect(screen.getByText(/at least 10 digits/i)).toBeInTheDocument();

    // Change input and error should clear
    fireEvent.change(mobileInput, { target: { value: '1234567890' } });
    expect(screen.queryByText(/at least 10 digits/i)).not.toBeInTheDocument();
  });

  test('validates both fields before submission', () => {
    renderLoginPage();
    const loginButton = screen.getByRole('button', { name: /login/i });

    fireEvent.click(loginButton);

    // Should not call API
    expect(authAPI.authAPI.login).not.toHaveBeenCalled();
  });
});
