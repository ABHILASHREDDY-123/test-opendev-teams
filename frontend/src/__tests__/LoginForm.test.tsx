import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import LoginForm from '../LoginForm';

jest.mock('axios');

describe('LoginForm', () => {
 it('renders email and password fields', () => {
 const { getByLabelText } = render(<LoginForm />);
 expect(getByLabelText('Email:')).toBeInTheDocument();
 expect(getByLabelText('Password:')).toBeInTheDocument();
 });

 it('submits form with email and password', async () => {
 const { getByLabelText, getByText } = render(<LoginForm />);
 const emailInput = getByLabelText('Email:');
 const passwordInput = getByLabelText('Password:');
 const submitButton = getByText('Login');

 fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
 fireEvent.change(passwordInput, { target: { value: 'password' } });

 fireEvent.click(submitButton);

 await waitFor(() => expect(axios.post).toHaveBeenCalledTimes(1));
 expect(axios.post).toHaveBeenCalledWith('/api/login', {
 email: 'test@example.com',
 password: 'password',
 });
 });

 it('displays loading state', async () => {
 const { getByText } = render(<LoginForm />);
 const submitButton = getByText('Login');

 fireEvent.click(submitButton);

 await waitFor(() => expect(getByText('Loading...')).toBeInTheDocument());
 });

 it('displays error message', async () => {
 axios.post.mockRejectedValueOnce(new Error('Invalid credentials'));
 const { getByText } = render(<LoginForm />);
 const submitButton = getByText('Login');

 fireEvent.click(submitButton);

 await waitFor(() => expect(getByText('Invalid credentials')).toBeInTheDocument());
 });
});
