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
    it('should render login form with mobile and password fields', () => {
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      expect(screen.getByLabelText(/mobile number/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
    });

    it('should render with title', () => {
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);
      expect(screen.getByText(/contacts login/i)).toBeInTheDocument();
    });
  });

  describe('Mobile Validation', () => {
    it('should show error if mobile is empty', async () => {
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/mobile number is required/i)).toBeInTheDocument();
      });
    });

    it('should show error if mobile contains non-digits', async () => {
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByLabelText(/mobile number/i);
      await userEvent.type(mobileInput, '123abc4567');

      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/must contain only digits/i)).toBeInTheDocument();
      });
    });

    it('should show error if mobile is less than 10 digits', async () => {
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByLabelText(/mobile number/i);
      await userEvent.type(mobileInput, '123456789');

      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/at least 10 digits/i)).toBeInTheDocument();
      });
    });

    it('should accept valid 10-digit mobile', async () => {
      (api.apiClient.login as jest.Mock).mockResolvedValue('test-token');

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByLabelText(/mobile number/i);
      const passwordInput = screen.getByLabelText(/password/i);

      await userEvent.type(mobileInput, '9876543210');
      await userEvent.type(passwordInput, 'password123');

      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(api.apiClient.login).toHaveBeenCalledWith('9876543210', 'password123');
      });
    });
  });

  describe('Password Validation', () => {
    it('should show error if password is empty', async () => {
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByLabelText(/mobile number/i);
      await userEvent.type(mobileInput, '9876543210');

      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/password is required/i)).toBeInTheDocument();
      });
    });

    it('should show error if password is less than 6 characters', async () => {
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByLabelText(/mobile number/i);
      const passwordInput = screen.getByLabelText(/password/i);

      await userEvent.type(mobileInput, '9876543210');
      await userEvent.type(passwordInput, 'pass');

      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/at least 6 characters/i)).toBeInTheDocument();
      });
    });

    it('should accept valid password', async () => {
      (api.apiClient.login as jest.Mock).mockResolvedValue('test-token');

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByLabelText(/mobile number/i);
      const passwordInput = screen.getByLabelText(/password/i);

      await userEvent.type(mobileInput, '9876543210');
      await userEvent.type(passwordInput, 'password123');

      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(api.apiClient.login).toHaveBeenCalled();
      });
    });
  });

  describe('Login API Integration', () => {
    it('should call login API with correct credentials', async () => {
      (api.apiClient.login as jest.Mock).mockResolvedValue('test-token');

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByLabelText(/mobile number/i);
      const passwordInput = screen.getByLabelText(/password/i);

      await userEvent.type(mobileInput, '9876543210');
      await userEvent.type(passwordInput, 'password123');

      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(api.apiClient.login).toHaveBeenCalledWith('9876543210', 'password123');
      });
    });

    it('should store JWT token in localStorage on successful login', async () => {
      (api.apiClient.login as jest.Mock).mockResolvedValue('test-token-123');

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByLabelText(/mobile number/i);
      const passwordInput = screen.getByLabelText(/password/i);

      await userEvent.type(mobileInput, '9876543210');
      await userEvent.type(passwordInput, 'password123');

      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(localStorage.getItem('jwt_token')).toBe('test-token-123');
      });
    });

    it('should call onLoginSuccess callback on successful login', async () => {
      (api.apiClient.login as jest.Mock).mockResolvedValue('test-token');

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByLabelText(/mobile number/i);
      const passwordInput = screen.getByLabelText(/password/i);

      await userEvent.type(mobileInput, '9876543210');
      await userEvent.type(passwordInput, 'password123');

      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockOnLoginSuccess).toHaveBeenCalled();
      });
    });

    it('should display error message on login failure', async () => {
      (api.apiClient.login as jest.Mock).mockRejectedValue(
        new Error('Invalid credentials')
      );

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByLabelText(/mobile number/i);
      const passwordInput = screen.getByLabelText(/password/i);

      await userEvent.type(mobileInput, '9876543210');
      await userEvent.type(passwordInput, 'password123');

      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
      });
    });

    it('should show loading state during login', async () => {
      (api.apiClient.login as jest.Mock).mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve('test-token'), 100)
          )
      );

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByLabelText(/mobile number/i);
      const passwordInput = screen.getByLabelText(/password/i);

      await userEvent.type(mobileInput, '9876543210');
      await userEvent.type(passwordInput, 'password123');

      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);

      expect(screen.getByRole('button', { name: /logging in/i })).toBeInTheDocument();

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
      });
    });
  });
});
