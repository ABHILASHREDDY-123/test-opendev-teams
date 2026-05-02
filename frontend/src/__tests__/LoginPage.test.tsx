import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginPage } from '../LoginPage';
import * as api from '../api';

// Mock the API module
jest.mock('../api');

describe('LoginPage Component', () => {
  const mockOnLoginSuccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe('Rendering', () => {
    it('should render login form with all required fields', () => {
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      expect(screen.getByText('Contacts App')).toBeInTheDocument();
      expect(screen.getByTestId('mobile-input')).toBeInTheDocument();
      expect(screen.getByTestId('password-input')).toBeInTheDocument();
      expect(screen.getByTestId('login-button')).toBeInTheDocument();
    });

    it('should have login button disabled initially', () => {
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);
      expect(screen.getByTestId('login-button')).not.toBeDisabled();
    });
  });

  describe('Mobile Number Validation', () => {
    it('should only allow digits in mobile input', async () => {
      const user = userEvent.setup();
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByTestId('mobile-input') as HTMLInputElement;
      await user.type(mobileInput, '98765abc43210');

      expect(mobileInput.value).toBe('9876543210');
    });

    it('should show error for mobile less than 10 digits', async () => {
      const user = userEvent.setup();
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByTestId('mobile-input');
      await user.type(mobileInput, '987654321');
      fireEvent.blur(mobileInput);

      await waitFor(() => {
        expect(screen.getByTestId('mobile-error')).toHaveTextContent(
          'Mobile number must be at least 10 digits'
        );
      });
    });

    it('should show error for empty mobile', async () => {
      const user = userEvent.setup();
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const form = screen.getByTestId('login-form');
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByTestId('mobile-error')).toHaveTextContent(
          'Mobile number is required'
        );
      });
    });

    it('should clear error when valid mobile is entered', async () => {
      const user = userEvent.setup();
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByTestId('mobile-input');
      await user.type(mobileInput, '987654321');

      await waitFor(() => {
        expect(screen.getByTestId('mobile-error')).toBeInTheDocument();
      });

      await user.type(mobileInput, '0');

      await waitFor(() => {
        expect(screen.queryByTestId('mobile-error')).not.toBeInTheDocument();
      });
    });
  });

  describe('Password Validation', () => {
    it('should show error for password less than 6 characters', async () => {
      const user = userEvent.setup();
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const passwordInput = screen.getByTestId('password-input');
      await user.type(passwordInput, '12345');

      await waitFor(() => {
        expect(screen.getByTestId('password-error')).toHaveTextContent(
          'Password must be at least 6 characters'
        );
      });
    });

    it('should show error for empty password', async () => {
      const user = userEvent.setup();
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const form = screen.getByTestId('login-form');
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByTestId('password-error')).toHaveTextContent(
          'Password is required'
        );
      });
    });

    it('should clear error when valid password is entered', async () => {
      const user = userEvent.setup();
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const passwordInput = screen.getByTestId('password-input');
      await user.type(passwordInput, '12345');

      await waitFor(() => {
        expect(screen.getByTestId('password-error')).toBeInTheDocument();
      });

      await user.type(passwordInput, '6');

      await waitFor(() => {
        expect(screen.queryByTestId('password-error')).not.toBeInTheDocument();
      });
    });
  });

  describe('Login Submission', () => {
    it('should successfully login with valid credentials', async () => {
      const user = userEvent.setup();
      (api.login as jest.Mock).mockResolvedValueOnce({ token: 'jwt-token' });

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      await user.type(screen.getByTestId('mobile-input'), '9876543210');
      await user.type(screen.getByTestId('password-input'), 'password123');
      await user.click(screen.getByTestId('login-button'));

      await waitFor(() => {
        expect(api.login).toHaveBeenCalledWith('9876543210', 'password123');
        expect(api.storeToken).toHaveBeenCalledWith('jwt-token');
        expect(mockOnLoginSuccess).toHaveBeenCalled();
      });
    });

    it('should show error on invalid credentials (401)', async () => {
      const user = userEvent.setup();
      (api.login as jest.Mock).mockRejectedValueOnce(
        new Error('Login failed: 401')
      );

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      await user.type(screen.getByTestId('mobile-input'), '9876543210');
      await user.type(screen.getByTestId('password-input'), 'wrongpassword');
      await user.click(screen.getByTestId('login-button'));

      await waitFor(() => {
        expect(screen.getByTestId('login-error')).toHaveTextContent(
          'Invalid credentials'
        );
      });
    });

    it('should show loading indicator during login', async () => {
      const user = userEvent.setup();
      (api.login as jest.Mock).mockImplementationOnce(
        () => new Promise((resolve) => setTimeout(() => resolve({ token: 'jwt-token' }), 100))
      );

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      await user.type(screen.getByTestId('mobile-input'), '9876543210');
      await user.type(screen.getByTestId('password-input'), 'password123');
      await user.click(screen.getByTestId('login-button'));

      expect(screen.getByTestId('login-button')).toHaveTextContent('Logging in...');

      await waitFor(() => {
        expect(screen.getByTestId('login-button')).toHaveTextContent('Login');
      });
    });

    it('should disable inputs during login', async () => {
      const user = userEvent.setup();
      (api.login as jest.Mock).mockImplementationOnce(
        () => new Promise((resolve) => setTimeout(() => resolve({ token: 'jwt-token' }), 100))
      );

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      await user.type(screen.getByTestId('mobile-input'), '9876543210');
      await user.type(screen.getByTestId('password-input'), 'password123');
      await user.click(screen.getByTestId('login-button'));

      expect(screen.getByTestId('mobile-input')).toBeDisabled();
      expect(screen.getByTestId('password-input')).toBeDisabled();

      await waitFor(() => {
        expect(screen.getByTestId('mobile-input')).not.toBeDisabled();
      });
    });

    it('should not submit form with invalid data', async () => {
      const user = userEvent.setup();
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      await user.type(screen.getByTestId('mobile-input'), '123');
      await user.type(screen.getByTestId('password-input'), '123');
      await user.click(screen.getByTestId('login-button'));

      await waitFor(() => {
        expect(api.login).not.toHaveBeenCalled();
      });
    });

    it('should handle network errors gracefully', async () => {
      const user = userEvent.setup();
      (api.login as jest.Mock).mockRejectedValueOnce(
        new Error('Network error')
      );

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      await user.type(screen.getByTestId('mobile-input'), '9876543210');
      await user.type(screen.getByTestId('password-input'), 'password123');
      await user.click(screen.getByTestId('login-button'));

      await waitFor(() => {
        expect(screen.getByTestId('login-error')).toHaveTextContent(
          'Network error'
        );
      });
    });
  });

  describe('Edge Cases', () => {
    it('should handle special characters in password', async () => {
      const user = userEvent.setup();
      (api.login as jest.Mock).mockResolvedValueOnce({ token: 'jwt-token' });

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      await user.type(screen.getByTestId('mobile-input'), '9876543210');
      await user.type(screen.getByTestId('password-input'), 'p@ss!word#123');
      await user.click(screen.getByTestId('login-button'));

      await waitFor(() => {
        expect(api.login).toHaveBeenCalledWith('9876543210', 'p@ss!word#123');
      });
    });

    it('should handle exactly 10 digit mobile number', async () => {
      const user = userEvent.setup();
      (api.login as jest.Mock).mockResolvedValueOnce({ token: 'jwt-token' });

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      await user.type(screen.getByTestId('mobile-input'), '1234567890');
      await user.type(screen.getByTestId('password-input'), 'password123');
      await user.click(screen.getByTestId('login-button'));

      await waitFor(() => {
        expect(api.login).toHaveBeenCalledWith('1234567890', 'password123');
      });
    });

    it('should handle exactly 6 character password', async () => {
      const user = userEvent.setup();
      (api.login as jest.Mock).mockResolvedValueOnce({ token: 'jwt-token' });

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      await user.type(screen.getByTestId('mobile-input'), '9876543210');
      await user.type(screen.getByTestId('password-input'), '123456');
      await user.click(screen.getByTestId('login-button'));

      await waitFor(() => {
        expect(api.login).toHaveBeenCalledWith('9876543210', '123456');
      });
    });
  });
});
