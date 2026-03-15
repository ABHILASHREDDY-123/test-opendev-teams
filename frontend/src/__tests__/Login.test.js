import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import Login from '../components/Login';

describe('Login component', () => {
 it('renders username and password fields', () => {
 const { getByLabelText } = render(<Login />);
 expect(getByLabelText('Username:')).toBeInTheDocument();
 expect(getByLabelText('Password:')).toBeInTheDocument();
 });

 it('submits the form with username and password', () => {
 const { getByLabelText, getByText } = render(<Login />);
 const usernameInput = getByLabelText('Username:');
 const passwordInput = getByLabelText('Password:');
 const submitButton = getByText('Login');

 fireEvent.change(usernameInput, { target: { value: 'testuser' } });
 fireEvent.change(passwordInput, { target: { value: 'testpassword' } });
 fireEvent.click(submitButton);

 // API integration test
 });
});
