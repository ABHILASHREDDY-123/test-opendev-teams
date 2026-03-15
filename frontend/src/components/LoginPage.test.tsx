import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import axios from 'axios';
import LoginPage from './LoginPage';

const server = setupServer(
 rest.post('/api/login', (req, res, ctx) => {
 return res(ctx.json({ token: 'mock-token' }));
 })
);

afterEach(() => server.resetHandlers());

afterAll(() => server.close());

describe('LoginPage', () => {
 it('renders login form', () => {
 const { getByText } = render(<LoginPage />);
 expect(getByText('Username:')).toBeInTheDocument();
 expect(getByText('Password:')).toBeInTheDocument();
 expect(getByText('Login')).toBeInTheDocument();
 });

 it('submits login form', async () => {
 const { getByText, getByLabelText } = render(<LoginPage />);
 const usernameInput = getByLabelText('Username:');
 const passwordInput = getByLabelText('Password:');
 const loginButton = getByText('Login');

 fireEvent.change(usernameInput, { target: { value: 'test-username' } });
 fireEvent.change(passwordInput, { target: { value: 'test-password' } });

 fireEvent.click(loginButton);

 await waitFor(() => expect(axios.post).toHaveBeenCalledTimes(1));
 });
});
