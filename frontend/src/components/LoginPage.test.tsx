import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import LoginPage from './LoginPage';

jest.mock('axios');

describe('LoginPage', () => {
 it('renders the login form', () => {
 const { getByText } = render(<LoginPage />);
 expect(getByText('Username:')).toBeInTheDocument();
 expect(getByText('Password:')).toBeInTheDocument();
 expect(getByText('Login')).toBeInTheDocument();
 });

 it('submits the form with username and password', async () => {
 const { getByText, getByLabelText } = render(<LoginPage />);
 const usernameInput = getByLabelText('Username:');
 const passwordInput = getByLabelText('Password:');
 const submitButton = getByText('Login');

 fireEvent.change(usernameInput, { target: { value: 'testuser' } });
 fireEvent.change(passwordInput, { target: { value: 'testpassword' } });

 await waitFor(() => fireEvent.click(submitButton));

 expect(axios.post).toHaveBeenCalledTimes(1);
 expect(axios.post).toHaveBeenCalledWith('/api/login', {
 username: 'testuser',
 password: 'testpassword',
 });
 });
});
