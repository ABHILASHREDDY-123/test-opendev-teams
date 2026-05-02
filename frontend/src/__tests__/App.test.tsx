import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import App from '../App';
import * as api from '../api';

// Mock the API module
jest.mock('../api');

// Mock child components to simplify testing
jest.mock('../LoginPage', () => ({
  LoginPage: ({ onLoginSuccess }: any) => (
    <div data-testid="login-page">
      <button onClick={onLoginSuccess}>Mock Login Success</button>
    </div>
  ),
}));

jest.mock('../ContactsPage', () => ({
  ContactsPage: ({ onLogout }: any) => (
    <div data-testid="contacts-page">
      <button onClick={onLogout}>Mock Logout</button>
    </div>
  ),
}));

describe('App Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe('Initial State', () => {
    it('should show login page when not authenticated', async () => {
      (api.getToken as jest.Mock).mockReturnValueOnce(null);

      render(<App />);

      await waitFor(() => {
        expect(screen.getByTestId('login-page')).toBeInTheDocument();
      });
    });

    it('should show contacts page when authenticated', async () => {
      (api.getToken as jest.Mock).mockReturnValueOnce('jwt-token');

      render(<App />);

      await waitFor(() => {
        expect(screen.getByTestId('contacts-page')).toBeInTheDocument();
      });
    });
  });

  describe('Authentication Flow', () => {
    it('should navigate to contacts page after successful login', async () => {
      (api.getToken as jest.Mock).mockReturnValueOnce(null);

      const { rerender } = render(<App />);

      await waitFor(() => {
        expect(screen.getByTestId('login-page')).toBeInTheDocument();
      });

      // Simulate successful login
      (api.getToken as jest.Mock).mockReturnValueOnce('jwt-token');
      const loginButton = screen.getByText('Mock Login Success');
      loginButton.click();

      rerender(<App />);

      await waitFor(() => {
        expect(screen.getByTestId('contacts-page')).toBeInTheDocument();
      });
    });

    it('should navigate to login page after logout', async () => {
      (api.getToken as jest.Mock).mockReturnValueOnce('jwt-token');

      const { rerender } = render(<App />);

      await waitFor(() => {
        expect(screen.getByTestId('contacts-page')).toBeInTheDocument();
      });

      // Simulate logout
      (api.getToken as jest.Mock).mockReturnValueOnce(null);
      const logoutButton = screen.getByText('Mock Logout');
      logoutButton.click();

      rerender(<App />);

      await waitFor(() => {
        expect(screen.getByTestId('login-page')).toBeInTheDocument();
      });
    });
  });

  describe('Token Persistence', () => {
    it('should check for existing token on mount', async () => {
      localStorage.setItem('jwt_token', 'existing-token');
      (api.getToken as jest.Mock).mockReturnValueOnce('existing-token');

      render(<App />);

      await waitFor(() => {
        expect(api.getToken).toHaveBeenCalled();
        expect(screen.getByTestId('contacts-page')).toBeInTheDocument();
      });
    });
  });
});
