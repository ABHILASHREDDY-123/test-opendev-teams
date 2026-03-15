import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import LoginPage from './LoginPage';

jest.mock('axios');

describe('LoginPage', () => {
 it('renders login form', () => {
 const { getByText, getByLabelText } = render(<LoginPage />);
 expect(getByText('Login Page')).toBeInTheDocument();
 expect(getByLabelText('Email:')).toBeInTheDocument();
 expect(getByLabelText('Password:')).toBeInTheDocument();
 });

 it('submits login form', async () => {
 const { getByText, getByLabelText } = render(<LoginPage />);
 const emailInput = getByLabelText('Email:');
 const passwordInput = getByLabelText('Password:');
 const submitButton = getByText('Login');

 fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
 fireEvent.change(passwordInput, { target: { value: 'password' } });

 fireEvent.click(submitButton);

 await waitFor(() => expect(axios.post).toHaveBeenCalledTimes(1));
 expect(axios.post).toHaveBeenCalledWith('/api/auth/login', {
 email: 'test@example.com',
 password: 'password',
 });
 });

 it('displays loading state', () => {
 const { getByText } = render(<LoginPage />);
 const submitButton = getByText('Login');

 fireEvent.click(submitButton);

 expect(getByText('Loading...')).toBeInTheDocument();
 });

 it('displays error message', async () => {
 axios.post.mockRejectedValueOnce(new Error('Invalid credentials'));
 const { getByText } = render(<LoginPage />);
 const submitButton = getByText('Login');

 fireEvent.click(submitButton);

 await waitFor(() => expect(getByText('Invalid credentials')).toBeInTheDocument());
 });
});
