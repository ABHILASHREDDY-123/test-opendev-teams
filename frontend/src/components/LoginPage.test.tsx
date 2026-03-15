import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import LoginPage from './LoginPage';

jest.mock('axios');

describe('LoginPage', () => {
 it('renders correctly', () => {
 const { getByText } = render(<LoginPage />);
 expect(getByText('Username:')).toBeInTheDocument();
 expect(getByText('Password:')).toBeInTheDocument();
 expect(getByText('Login')).toBeInTheDocument();
 });

 it('handles submission correctly', async () => {
 const { getByText, getByLabelText } = render(<LoginPage />);
 const usernameInput = getByLabelText('Username:');
 const passwordInput = getByLabelText('Password:');
 const loginButton = getByText('Login');

 fireEvent.change(usernameInput, { target: { value: 'testuser' } });
 fireEvent.change(passwordInput, { target: { value: 'testpassword' } });

 fireEvent.click(loginButton);

 await waitFor(() => expect(axios.post).toHaveBeenCalledTimes(1));
 expect(axios.post).toHaveBeenCalledWith('/api/login', {
 username: 'testuser',
 password: 'testpassword',
 });
 });
});
