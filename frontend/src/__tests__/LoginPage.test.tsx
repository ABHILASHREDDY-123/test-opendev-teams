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

  describe('Rendering', () => {
    it('should render login form with mobile and password inputs', () => {
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      expect(screen.getByTestId('mobile-input')).toBeInTheDocument();
      expect(screen.getByTestId('password-input')).toBeInTheDocument();
      expect(screen.getByTestId('login-button')).toBeInTheDocument();
    });

    it('should render login button as disabled initially', () => {
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const loginButton = screen.getByTestId('login-button');
      expect(loginButton).toBeDisabled();
    });
  });

  describe('Mobile Validation', () => {
    it('should accept only digits in mobile field', async () => {
      const user = userEvent.setup();
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByTestId('mobile-input') as HTMLInputElement;
      await user.type(mobileInput, '9876543210abc');

      expect(mobileInput.value).toBe('9876543210');
    });

    it('should show error for mobile with less than 10 digits', async () => {
      const user = userEvent.setup();
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByTestId('mobile-input');
      await user.type(mobileInput, '12345');

      expect(screen.getByTestId('mobile-error')).toBeInTheDocument();
      expect(screen.getByTestId('mobile-error')).toHaveTextContent('Mobile must be at least 10 digits');
    });

    it('should not show error for mobile with 10+ digits', async () => {
      const user = userEvent.setup();
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByTestId('mobile-input');
      await user.type(mobileInput, '9876543210');

      expect(screen.queryByTestId('mobile-error')).not.toBeInTheDocument();
    });
  });

  describe('Password Validation', () => {
    it('should show error for password with less than 6 characters', async () => {
      const user = userEvent.setup();
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const passwordInput = screen.getByTestId('password-input');
      await user.type(passwordInput, '12345');

      expect(screen.getByTestId('password-error')).toBeInTheDocument();
      expect(screen.getByTestId('password-error')).toHaveTextContent('Password must be at least 6 characters');
    });

    it('should not show error for password with 6+ characters', async () => {
      const user = userEvent.setup();
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const passwordInput = screen.getByTestId('password-input');
      await user.type(passwordInput, '123456');

      expect(screen.queryByTestId('password-error')).not.toBeInTheDocument();
    });
  });

  describe('Form Submission', () => {
    it('should enable login button when form is valid', async () => {
      const user = userEvent.setup();
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByTestId('mobile-input');
      const passwordInput = screen.getByTestId('password-input');
      const loginButton = screen.getByTestId('login-button');

      await user.type(mobileInput, '9876543210');
      await user.type(passwordInput, '123456');

      expect(loginButton).not.toBeDisabled();
    });

    it('should call login API with correct credentials', async () => {
      const user = userEvent.setup();
      (api.login as jest.Mock).mockResolvedValue('test-token');

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByTestId('mobile-input');
      const passwordInput = screen.getByTestId('password-input');
      const loginButton = screen.getByTestId('login-button');

      await user.type(mobileInput, '9876543210');
      await user.type(passwordInput, 'password123');
      await user.click(loginButton);

      await waitFor(() => {
        expect(api.login).toHaveBeenCalledWith('9876543210', 'password123');
      });
    });

    it('should store token in localStorage on successful login', async () => {
      const user = userEvent.setup();
      (api.login as jest.Mock).mockResolvedValue('test-token');

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByTestId('mobile-input');
      const passwordInput = screen.getByTestId('password-input');
      const loginButton = screen.getByTestId('login-button');

      await user.type(mobileInput, '9876543210');
      await user.type(passwordInput, 'password123');
      await user.click(loginButton);

      await waitFor(() => {
        expect(localStorage.getItem('authToken')).toBe('test-token');
      });
    });

    it('should call onLoginSuccess callback on successful login', async () => {
      const user = userEvent.setup();
      (api.login as jest.Mock).mockResolvedValue('test-token');

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByTestId('mobile-input');
      const passwordInput = screen.getByTestId('password-input');
      const loginButton = screen.getByTestId('login-button');

      await user.type(mobileInput, '9876543210');
      await user.type(passwordInput, 'password123');
      await user.click(loginButton);

      await waitFor(() => {
        expect(mockOnLoginSuccess).toHaveBeenCalledWith('test-token');
      });
    });

    it('should show loading state during login', async () => {
      const user = userEvent.setup();
      (api.login as jest.Mock).mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve('test-token'), 100))
      );

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByTestId('mobile-input');
      const passwordInput = screen.getByTestId('password-input');
      const loginButton = screen.getByTestId('login-button');

      await user.type(mobileInput, '9876543210');
      await user.type(passwordInput, 'password123');
      await user.click(loginButton);

      expect(screen.getByTestId('login-button')).toHaveTextContent('Logging in...');
      expect(mobileInput).toBeDisabled();
      expect(passwordInput).toBeDisabled();
    });
  });

  describe('Error Handling', () => {
    it('should display error message on login failure', async () => {
      const user = userEvent.setup();
      (api.login as jest.Mock).mockRejectedValue(new Error('Invalid credentials'));

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByTestId('mobile-input');
      const passwordInput = screen.getByTestId('password-input');
      const loginButton = screen.getByTestId('login-button');

      await user.type(mobileInput, '9876543210');
      await user.type(passwordInput, 'password123');
      await user.click(loginButton);

      await waitFor(() => {
        expect(screen.getByTestId('error-message')).toHaveTextContent('Invalid credentials');
      });
    });

    it('should clear error when user types', async () => {
      const user = userEvent.setup();
      (api.login as jest.Mock).mockRejectedValue(new Error('Invalid credentials'));

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByTestId('mobile-input');
      const passwordInput = screen.getByTestId('password-input');
      const loginButton = screen.getByTestId('login-button');

      await user.type(mobileInput, '9876543210');
      await user.type(passwordInput, 'password123');
      await user.click(loginButton);

      await waitFor(() => {
        expect(screen.getByTestId('error-message')).toBeInTheDocument();
      });

      await user.type(mobileInput, '1');
      expect(screen.queryByTestId('error-message')).not.toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty form submission', async () => {
      const user = userEvent.setup();
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const loginButton = screen.getByTestId('login-button');
      expect(loginButton).toBeDisabled();
    });

    it('should handle very long mobile numbers', async () => {
      const user = userEvent.setup();
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByTestId('mobile-input') as HTMLInputElement;
      await user.type(mobileInput, '98765432101234567890');

      expect(mobileInput.value).toBe('98765432101234567890');
    });

    it('should handle special characters in password', async () => {
      const user = userEvent.setup();
      (api.login as jest.Mock).mockResolvedValue('test-token');

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByTestId('mobile-input');
      const passwordInput = screen.getByTestId('password-input');
      const loginButton = screen.getByTestId('login-button');

      await user.type(mobileInput, '9876543210');
      await user.type(passwordInput, 'p@ss!word#123');
      await user.click(loginButton);

      await waitFor(() => {
        expect(api.login).toHaveBeenCalledWith('9876543210', 'p@ss!word#123');
      });
    });
  });
});
