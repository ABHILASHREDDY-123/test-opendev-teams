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

 it('shows error message when username or password is empty', () => {
 const { getByText } = render(<LoginPage />);
 const submitButton = getByText('Login');
 fireEvent.click(submitButton);
 expect(getByText('Username and password are required')).toBeInTheDocument();
 });

 it('calls API to authenticate user when form is submitted', () => {
 const { getByText, getByPlaceholderText } = render(<LoginPage />);
 const usernameInput = getByPlaceholderText('Username');
 const passwordInput = getByPlaceholderText('Password');
 const submitButton = getByText('Login');

 fireEvent.change(usernameInput, { target: { value: 'testuser' } });
 fireEvent.change(passwordInput, { target: { value: 'testpassword' } });
 fireEvent.click(submitButton);

 // TODO: Mock API call to authenticate user
 // expect(console.log).toHaveBeenCalledTimes(1);
 // expect(console.log).toHaveBeenCalledWith('Username: testuser, Password: testpassword');
 });
});
