import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../App';
import * as api from '../api';

jest.mock('../api');

describe('App', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  it('should render login page when not logged in', () => {
    render(<App />);

    expect(screen.getByTestId('login-page')).toBeInTheDocument();
  });

  it('should render contacts page when logged in', () => {
    localStorage.setItem('authToken', 'test-token');
    (api.getContacts as jest.Mock).mockResolvedValueOnce([]);

    render(<App />);

    expect(screen.getByTestId('contacts-page')).toBeInTheDocument();
  });

  it('should switch to contacts page after successful login', async () => {
    (api.login as jest.Mock).mockResolvedValueOnce('test-token-123');
    (api.getContacts as jest.Mock).mockResolvedValueOnce([]);

    render(<App />);

    expect(screen.getByTestId('login-page')).toBeInTheDocument();

    const mobileInput = screen.getByTestId('mobile-input');
    const passwordInput = screen.getByTestId('password-input');
    const loginButton = screen.getByTestId('login-button');

    fireEvent.change(mobileInput, { target: { value: '9876543210' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByTestId('contacts-page')).toBeInTheDocument();
    });
  });

  it('should switch back to login page after logout', async () => {
    localStorage.setItem('authToken', 'test-token');
    (api.getContacts as jest.Mock).mockResolvedValueOnce([]);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByTestId('contacts-page')).toBeInTheDocument();
    });

    const logoutButton = screen.getByTestId('logout-button');
    fireEvent.click(logoutButton);

    await waitFor(() => {
      expect(screen.getByTestId('login-page')).toBeInTheDocument();
    });
  });
});
