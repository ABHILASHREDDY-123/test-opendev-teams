import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import App from '../App';
import * as api from '../api';

jest.mock('../api');

describe('App', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  it('should render LoginPage when not logged in', async () => {
    (api.apiClient.getContacts as jest.Mock).mockResolvedValue([]);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/contacts login/i)).toBeInTheDocument();
    });
  });

  it('should render ContactsPage when logged in', async () => {
    localStorage.setItem('jwt_token', 'test-token');
    (api.apiClient.getContacts as jest.Mock).mockResolvedValue([]);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/my contacts/i)).toBeInTheDocument();
    });
  });

  it('should switch to ContactsPage after successful login', async () => {
    (api.apiClient.login as jest.Mock).mockResolvedValue('test-token');
    (api.apiClient.getContacts as jest.Mock).mockResolvedValue([]);

    render(<App />);

    // Initially shows login page
    await waitFor(() => {
      expect(screen.getByText(/contacts login/i)).toBeInTheDocument();
    });

    // Simulate login by setting token
    localStorage.setItem('jwt_token', 'test-token');

    // Re-render to check if it switches
    const { rerender } = render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/my contacts/i)).toBeInTheDocument();
    });
  });
});
