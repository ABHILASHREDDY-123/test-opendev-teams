import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import LoginPage from '../LoginPage';
import { login } from '../api';

jest.mock('../api');

describe('LoginPage', () => {
  it('renders login form', () => {
    const { getByPlaceholderText } = render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );
    expect(getByPlaceholderText('Mobile')).toBeInTheDocument();
    expect(getByPlaceholderText('Password')).toBeInTheDocument();
  });

  it('validates mobile number', async () => {
    const { getByText, getByPlaceholderText } = render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );
    const mobileInput = getByPlaceholderText('Mobile');
    const passwordInput = getByPlaceholderText('Password');
    const submitButton = getByText('Login');

    fireEvent.change(mobileInput, { target: { value: '123' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(login).not.toHaveBeenCalled();
    });
  });
});