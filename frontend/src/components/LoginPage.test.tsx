import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import LoginPage from './LoginPage';

jest.mock('axios');

describe('LoginPage', () => {
 it('renders correctly', () => {
 const { container } = render(<LoginPage />);
 expect(container).toMatchSnapshot();
 });

 it('handles login submission', async () => {
 const { getByText, getByLabelText } = render(<LoginPage />);
 const usernameInput = getByLabelText('Username:');
 const passwordInput = getByLabelText('Password:');
 const loginButton = getByText('Login');

 fireEvent.change(usernameInput, { target: { value: 'testuser' } });
 fireEvent.change(passwordInput, { target: { value: 'testpassword' } });

 await waitFor(() => fireEvent.click(loginButton));

 expect(axios.post).toHaveBeenCalledTimes(1);
 expect(axios.post).toHaveBeenCalledWith('/api/auth/login', {
 username: 'testuser',
 password: 'testpassword',
 });
 });

 it('displays error message on login failure', async () => {
 const { getByText, getByLabelText } = render(<LoginPage />);
 const usernameInput = getByLabelText('Username:');
 const passwordInput = getByLabelText('Password:');
 const loginButton = getByText('Login');

 axios.post.mockRejectedValueOnce({ response: { data: 'Invalid credentials' } });

 fireEvent.change(usernameInput, { target: { value: 'testuser' } });
 fireEvent.change(passwordInput, { target: { value: 'testpassword' } });

 await waitFor(() => fireEvent.click(loginButton));

 expect(getByText('Invalid credentials')).toBeInTheDocument();
 });
});
