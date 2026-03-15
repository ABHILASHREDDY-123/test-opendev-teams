import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import LoginPage from '../LoginPage';
import { login } from '../api';

jest.mock('../api');

describe('LoginPage', () => {
  it('renders login form', () => {
    const { getByPlaceholderText, getByText } = render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );
    expect(getByPlaceholderText('Mobile')).toBeInTheDocument();
    expect(getByPlaceholderText('Password')).toBeInTheDocument();
    expect(getByText('Login')).toBeInTheDocument();
  });

  it('shows error on invalid credentials', async () => {
    (login as jest.Mock).mockRejectedValue(new Error('Invalid credentials'));
    const { getByText, getByPlaceholderText } = render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );
    const mobileInput = getByPlaceholderText('Mobile');
    const passwordInput = getByPlaceholderText('Password');
    const loginButton = getByText('Login');

    fireEvent.change(mobileInput, { target: { value: '1234567890' } });
    fireEvent.change(passwordInput, { target: { value: 'password' } });
    fireEvent.click(loginButton);

    await waitFor(() => expect(getByText('Invalid credentials')).toBeInTheDocument());
  });
});