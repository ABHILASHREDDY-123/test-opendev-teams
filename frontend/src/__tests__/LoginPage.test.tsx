import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginPage } from '../LoginPage';
import * as api from '../api';

jest.mock('../api');

describe('LoginPage', () => {
  const mockOnLoginSuccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  it('should render login form', () => {
    render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

    expect(screen.getByTestId('login-page')).toBeInTheDocument();
    expect(screen.getByTestId('mobile-input')).toBeInTheDocument();
    expect(screen.getByTestId('password-input')).toBeInTheDocument();
    expect(screen.getByTestId('login-button')).toBeInTheDocument();
  });

  it('should validate mobile number - required', async () => {
    render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

    const loginButton = screen.getByTestId('login-button');
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByTestId('mobile-error')).toHaveTextContent('Mobile number is required');
    });
  });

  it('should validate mobile number - digits only', async () => {
    render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

    const mobileInput = screen.getByTestId('mobile-input');
    fireEvent.change(mobileInput, { target: { value: 'abc1234567' } });

    const loginButton = screen.getByTestId('login-button');
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByTestId('mobile-error')).toHaveTextContent('Mobile number must contain only digits');
    });
  });

  it('should validate mobile number - minimum 10 digits', async () => {
    render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

    const mobileInput = screen.getByTestId('mobile-input');
    fireEvent.change(mobileInput, { target: { value: '123456789' } });

    const loginButton = screen.getByTestId('login-button');
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByTestId('mobile-error')).toHaveTextContent('Mobile number must be at least 10 digits');
    });
  });

  it('should validate password - required', async () => {
    render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

    const mobileInput = screen.getByTestId('mobile-input');
    fireEvent.change(mobileInput, { target: { value: '9876543210' } });

    const loginButton = screen.getByTestId('login-button');
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByTestId('password-error')).toHaveTextContent('Password is required');
    });
  });

  it('should validate password - minimum 6 characters', async () => {
    render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

    const mobileInput = screen.getByTestId('mobile-input');
    const passwordInput = screen.getByTestId('password-input');

    fireEvent.change(mobileInput, { target: { value: '9876543210' } });
    fireEvent.change(passwordInput, { target: { value: '12345' } });

    const loginButton = screen.getByTestId('login-button');
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByTestId('password-error')).toHaveTextContent('Password must be at least 6 characters');
    });
  });

  it('should successfully login with valid credentials', async () => {
    (api.login as jest.Mock).mockResolvedValueOnce('test-token-123');

    render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

    const mobileInput = screen.getByTestId('mobile-input');
    const passwordInput = screen.getByTestId('password-input');
    const loginButton = screen.getByTestId('login-button');

    fireEvent.change(mobileInput, { target: { value: '9876543210' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(api.login).toHaveBeenCalledWith('9876543210', 'password123');
      expect(mockOnLoginSuccess).toHaveBeenCalledWith('test-token-123');
      expect(localStorage.getItem('authToken')).toBe('test-token-123');
    });
  });

  it('should display API error on login failure', async () => {
    // Create a custom error that properly extends Error
    const error = new Error('Invalid credentials');
    Object.setPrototypeOf(error, api.APIError.prototype);
    (error as any).status = 401;

    (api.login as jest.Mock).mockRejectedValueOnce(error);

    render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

    const mobileInput = screen.getByTestId('mobile-input');
    const passwordInput = screen.getByTestId('password-input');
    const loginButton = screen.getByTestId('login-button');

    fireEvent.change(mobileInput, { target: { value: '9876543210' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
    fireEvent.click(loginButton);

    // Wait for the error to appear after async login attempt completes
    await waitFor(
      () => {
        const errorElement = screen.queryByTestId('api-error');
        if (!errorElement) {
          throw new Error('api-error not found');
        }
      },
      { timeout: 3000 }
    );

    expect(screen.getByTestId('api-error')).toHaveTextContent('Invalid credentials');
    expect(mockOnLoginSuccess).not.toHaveBeenCalled();
  });

  it('should show loading state during login', async () => {
    (api.login as jest.Mock).mockImplementationOnce(
      () => new Promise((resolve) => setTimeout(() => resolve('token'), 100))
    );

    render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

    const mobileInput = screen.getByTestId('mobile-input');
    const passwordInput = screen.getByTestId('password-input');
    const loginButton = screen.getByTestId('login-button');

    fireEvent.change(mobileInput, { target: { value: '9876543210' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(loginButton);

    expect(screen.getByTestId('login-button')).toHaveTextContent('Logging in...');
    expect(screen.getByTestId('login-button')).toBeDisabled();

    await waitFor(() => {
      expect(screen.getByTestId('login-button')).toHaveTextContent('Login');
    });
  });

  it('should clear errors when user modifies input', async () => {
    render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

    const mobileInput = screen.getByTestId('mobile-input');
    const loginButton = screen.getByTestId('login-button');

    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByTestId('mobile-error')).toBeInTheDocument();
    });

    fireEvent.change(mobileInput, { target: { value: '9876543210' } });

    await waitFor(() => {
      expect(screen.queryByTestId('mobile-error')).not.toBeInTheDocument();
    });
  });
});
