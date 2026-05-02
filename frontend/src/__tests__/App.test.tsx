import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { App } from '../App';
import * as api from '../api';

jest.mock('../api');

describe('App', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe('Initial State', () => {
    it('should render LoginPage when not logged in', () => {
      (api.getContacts as jest.Mock).mockResolvedValue([]);

      render(<App />);

      expect(screen.getByTestId('mobile-input')).toBeInTheDocument();
      expect(screen.getByTestId('password-input')).toBeInTheDocument();
    });

    it('should render ContactsPage when token exists in localStorage', async () => {
      localStorage.setItem('authToken', 'test-token');
      (api.getContacts as jest.Mock).mockResolvedValue([]);

      render(<App />);

      await waitFor(() => {
        expect(screen.getByText('My Contacts')).toBeInTheDocument();
      });
    });
  });

  describe('Login Flow', () => {
    it('should navigate to ContactsPage after successful login', async () => {
      const user = userEvent.setup();
      (api.login as jest.Mock).mockResolvedValue('test-token');
      (api.getContacts as jest.Mock).mockResolvedValue([]);

      render(<App />);

      const mobileInput = screen.getByTestId('mobile-input');
      const passwordInput = screen.getByTestId('password-input');
      const loginButton = screen.getByTestId('login-button');

      await user.type(mobileInput, '9876543210');
      await user.type(passwordInput, 'password123');
      await user.click(loginButton);

      await waitFor(() => {
        expect(screen.getByText('My Contacts')).toBeInTheDocument();
      });
    });
  });

  describe('Logout Flow', () => {
    it('should navigate to LoginPage after logout', async () => {
      const user = userEvent.setup();
      localStorage.setItem('authToken', 'test-token');
      (api.getContacts as jest.Mock).mockResolvedValue([]);

      render(<App />);

      const logoutButton = await screen.findByTestId('logout-button');
      await user.click(logoutButton);

      await waitFor(() => {
        expect(screen.getByTestId('mobile-input')).toBeInTheDocument();
      });
    });
  });
});
