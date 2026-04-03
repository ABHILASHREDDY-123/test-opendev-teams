import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import LoginPage from '../LoginPage';
import { login } from '../api';

jest.mock('../api');

describe('LoginPage', () => {
  it('renders login form', () => {
    const { getByLabelText } = render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );
    expect(getByLabelText('Mobile:')).toBeInTheDocument();
    expect(getByLabelText('Password:')).toBeInTheDocument();
  });

  it('validates mobile number', async () => {
    const { getByText, getByLabelText } = render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );
    const mobileInput = getByLabelText('Mobile:');
    fireEvent.change(mobileInput, { target: { value: '123' } });
    fireEvent.click(getByText('Login'));
    await waitFor(() => expect(getByText('Invalid mobile number')).toBeInTheDocument());
  });

  it('shows loading state when submitting', async () => {
    (login as jest.Mock).mockResolvedValue({ access_token: 'token' });
    const { getByText } = render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );
    const mobileInput = getByText('Mobile:').closest('input');
    const passwordInput = getByText('Password:').closest('input');
    if (mobileInput && passwordInput) {
      fireEvent.change(mobileInput, { target: { value: '1234567890' } });
      fireEvent.change(passwordInput, { target: { value: 'password' } });
    }
    const submitButton = getByText('Login');
    fireEvent.click(submitButton);
    expect(getByText('Loading...')).toBeInTheDocument();
  });
});