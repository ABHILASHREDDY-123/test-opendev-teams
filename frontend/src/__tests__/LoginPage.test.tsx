import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import LoginPage from '../LoginPage';

describe('LoginPage', () => {
 it('renders login form', () => {
 const { getByText } = render(<LoginPage />);
 expect(getByText('Login Page')).toBeInTheDocument();
 });

 it('submits login form', () => {
 const { getByText, getByLabelText } = render(<LoginPage />);
 const usernameInput = getByLabelText('Username:');
 const passwordInput = getByLabelText('Password:');
 const submitButton = getByText('Login');

 fireEvent.change(usernameInput, { target: { value: 'admin' } });
 fireEvent.change(passwordInput, { target: { value: 'password' } });
 fireEvent.click(submitButton);

 expect(submitButton).toBeDisabled();
 });
});
