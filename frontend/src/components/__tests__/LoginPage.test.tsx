import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginPage } from '../LoginPage';
import { apiClient } from '../../services/apiClient';

jest.mock('../../services/apiClient');

describe('LoginPage', () => {
  const mockOnLoginSuccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render login form with mobile and password fields', () => {
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      expect(screen.getByLabelText(/mobile number/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
    });

    it('should render with empty initial values', () => {
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByLabelText(/mobile number/i) as HTMLInputElement;
      const passwordInput = screen.getByLabelText(/password/i) as HTMLInputElement;

      expect(mobileInput.value).toBe('');
      expect(passwordInput.value).toBe('');
    });
  });

  describe('Client-side Validation', () => {
    it('should show error for empty mobile number', async () => {
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/mobile number is required/i)).toBeInTheDocument();
      });
    });

    it('should show error for mobile number with less than 10 digits', async () => {
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByLabelText(/mobile number/i);
      await act(async () => {
        await userEvent.type(mobileInput, '12345');
      });

      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/mobile number must be at least 10 digits/i)).toBeInTheDocument();
      });
    });

    it('should accept mobile number with 10+ digits', async () => {
      (apiClient.login as jest.Mock).mockResolvedValueOnce({
        data: { access_token: 'token' },
        status: 200,
      });

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByLabelText(/mobile number/i);
      const passwordInput = screen.getByLabelText(/password/i);

      await act(async () => {
        await userEvent.type(mobileInput, '9876543210');
        await userEvent.type(passwordInput, 'password123');
      });

      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockOnLoginSuccess).toHaveBeenCalled();
      });
    });

    it('should show error for empty password', async () => {
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByLabelText(/mobile number/i);
      await act(async () => {
        await userEvent.type(mobileInput, '9876543210');
      });

      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/password is required/i)).toBeInTheDocument();
      });
    });

    it('should show error for password with less than 6 characters', async () => {
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByLabelText(/mobile number/i);
      const passwordInput = screen.getByLabelText(/password/i);

      await act(async () => {
        await userEvent.type(mobileInput, '9876543210');
        await userEvent.type(passwordInput, '12345');
      });

      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/password must be at least 6 characters/i)).toBeInTheDocument();
      });
    });

    it('should not call API if validation fails', async () => {
      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(apiClient.login).not.toHaveBeenCalled();
      });
    });
  });

  describe('Happy Path - Successful Login', () => {
    it('should call login API with correct credentials', async () => {
      (apiClient.login as jest.Mock).mockResolvedValueOnce({
        data: { access_token: 'jwt-token-123' },
        status: 200,
      });

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByLabelText(/mobile number/i);
      const passwordInput = screen.getByLabelText(/password/i);

      await act(async () => {
        await userEvent.type(mobileInput, '9876543210');
        await userEvent.type(passwordInput, 'password123');
      });

      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(apiClient.login).toHaveBeenCalledWith('9876543210', 'password123');
      });
    });

    it('should store JWT token on successful login', async () => {
      (apiClient.login as jest.Mock).mockResolvedValueOnce({
        data: { access_token: 'jwt-token-123' },
        status: 200,
      });

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByLabelText(/mobile number/i);
      const passwordInput = screen.getByLabelText(/password/i);

      await act(async () => {
        await userEvent.type(mobileInput, '9876543210');
        await userEvent.type(passwordInput, 'password123');
      });

      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(apiClient.setToken).toHaveBeenCalledWith('jwt-token-123');
      });
    });

    it('should call onLoginSuccess callback after successful login', async () => {
      (apiClient.login as jest.Mock).mockResolvedValueOnce({
        data: { access_token: 'jwt-token-123' },
        status: 200,
      });

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByLabelText(/mobile number/i);
      const passwordInput = screen.getByLabelText(/password/i);

      await act(async () => {
        await userEvent.type(mobileInput, '9876543210');
        await userEvent.type(passwordInput, 'password123');
      });

      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockOnLoginSuccess).toHaveBeenCalled();
      });
    });

    it('should show loading indicator during login request', async () => {
      (apiClient.login as jest.Mock).mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve({ data: { access_token: 'token' }, status: 200 }), 100)
          )
      );

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByLabelText(/mobile number/i);
      const passwordInput = screen.getByLabelText(/password/i);

      await act(async () => {
        await userEvent.type(mobileInput, '9876543210');
        await userEvent.type(passwordInput, 'password123');
      });

      const submitButton = screen.getByRole('button', { name: /login/i });
      
      await act(async () => {
        fireEvent.click(submitButton);
      });

      // Button should show "Logging in..." immediately after click
      expect(screen.getByRole('button', { name: /logging in/i })).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should display error message on 401 Unauthorized response', async () => {
      (apiClient.login as jest.Mock).mockResolvedValueOnce({
        error: 'Invalid credentials',
        status: 401,
      });

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByLabelText(/mobile number/i);
      const passwordInput = screen.getByLabelText(/password/i);

      await act(async () => {
        await userEvent.type(mobileInput, '9876543210');
        await userEvent.type(passwordInput, 'wrongpassword');
      });

      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
      });
    });

    it('should not call onLoginSuccess on failed login', async () => {
      (apiClient.login as jest.Mock).mockResolvedValueOnce({
        error: 'Invalid credentials',
        status: 401,
      });

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByLabelText(/mobile number/i);
      const passwordInput = screen.getByLabelText(/password/i);

      await act(async () => {
        await userEvent.type(mobileInput, '9876543210');
        await userEvent.type(passwordInput, 'wrongpassword');
      });

      const submitButton = screen.getByRole('button', { name: /login/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockOnLoginSuccess).not.toHaveBeenCalled();
      });
    });

    it('should disable form inputs during loading', async () => {
      (apiClient.login as jest.Mock).mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve({ data: { access_token: 'token' }, status: 200 }), 100)
          )
      );

      render(<LoginPage onLoginSuccess={mockOnLoginSuccess} />);

      const mobileInput = screen.getByLabelText(/mobile number/i) as HTMLInputElement;
      const passwordInput = screen.getByLabelText(/password/i) as HTMLInputElement;

      await act(async () => {
        await userEvent.type(mobileInput, '9876543210');
        await userEvent.type(passwordInput, 'password123');
      });

      const submitButton = screen.getByRole('button', { name: /login/i });
      
      await act(async () => {
        fireEvent.click(submitButton);
      });

      expect(mobileInput.disabled).toBe(true);
      expect(passwordInput.disabled).toBe(true);
    });
  });
});
