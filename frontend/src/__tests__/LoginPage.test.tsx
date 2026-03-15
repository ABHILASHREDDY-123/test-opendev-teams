import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import LoginPage from '../components/LoginPage';

jest.mock('axios');

describe('LoginPage', () => {
 it('renders email and password fields', () => {
 const { getByLabelText } = render(<LoginPage />);
 expect(getByLabelText('Email:')).toBeInTheDocument();
 expect(getByLabelText('Password:')).toBeInTheDocument();
 });

 it('submits form with email and password', async () => {
 const { getByLabelText, getByText } = render(<LoginPage />);
 const emailInput = getByLabelText('Email:');
 const passwordInput = getByLabelText('Password:');
 const submitButton = getByText('Login');

 fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
 fireEvent.change(passwordInput, { target: { value: 'password' } });

 axios.post.mockResolvedValue({ data: { token: 'mock-token' } });

 fireEvent.click(submitButton);

 await waitFor(() => expect(axios.post).toHaveBeenCalledTimes(1));
 expect(axios.post).toHaveBeenCalledWith('/api/auth/login', {
 email: 'test@example.com',
 password: 'password',
 });
 });
});
