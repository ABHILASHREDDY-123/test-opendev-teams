import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import LoginPage from './LoginPage';

describe('LoginPage', () => {
 it('renders username and password fields', () => {
 const { getByPlaceholderText } = render(<LoginPage />);
 expect(getByPlaceholderText('Username')).toBeInTheDocument();
 expect(getByPlaceholderText('Password')).toBeInTheDocument();
 });

 it('submits the form with username and password', () => {
 const { getByText, getByPlaceholderText } = render(<LoginPage />);
 const usernameInput = getByPlaceholderText('Username');
 const passwordInput = getByPlaceholderText('Password');
 const submitButton = getByText('Login');

 fireEvent.change(usernameInput, { target: { value: 'test' } });
 fireEvent.change(passwordInput, { target: { value: 'test' } });
 fireEvent.click(submitButton);

 expect(submitButton).toBeDisabled();
 });

 it('displays an error message for invalid credentials', async () => {
 const { getByText, getByPlaceholderText } = render(<LoginPage />);
 const usernameInput = getByPlaceholderText('Username');
 const passwordInput = getByPlaceholderText('Password');
 const submitButton = getByText('Login');

 fireEvent.change(usernameInput, { target: { value: 'invalid' } });
 fireEvent.change(passwordInput, { target: { value: 'invalid' } });
 fireEvent.click(submitButton);

 await waitFor(() => expect(getByText('Invalid username or password')).toBeInTheDocument());
 });
});
