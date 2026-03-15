import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import LoginPage from './LoginPage';

describe('LoginPage', () => {
 it('renders login form', () => {
 const { getByText } = render(<LoginPage />);
 expect(getByText('Username:')).toBeInTheDocument();
 expect(getByText('Password:')).toBeInTheDocument();
 });

 it('submits login form', async () => {
 const { getByText, getByLabelText } = render(<LoginPage />);
 const usernameInput = getByLabelText('Username:');
 const passwordInput = getByLabelText('Password:');
 const submitButton = getByText('Login');

 fireEvent.change(usernameInput, { target: { value: 'test' } });
 fireEvent.change(passwordInput, { target: { value: 'test' } });
 fireEvent.click(submitButton);

 await waitFor(() => expect(getByText('Loading...')).toBeInTheDocument());
 });
});
