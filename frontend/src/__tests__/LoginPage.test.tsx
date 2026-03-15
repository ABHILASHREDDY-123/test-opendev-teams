import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import axios from 'axios';
import LoginPage from '../components/LoginPage';

const server = setupServer(
 rest.post('/api/login', (req, res, ctx) => {
 return res(ctx.json({ token: 'test-token' }));
 }),
);

afterEach(() => server.resetHandlers());

afterAll(() => server.close());

describe('LoginPage', () => {
 it('should render login form', () => {
 const { getByText } = render(<LoginPage />);
 expect(getByText('Login Page')).toBeInTheDocument();
 expect(getByText('Email:')).toBeInTheDocument();
 expect(getByText('Password:')).toBeInTheDocument();
 expect(getByText('Login')).toBeInTheDocument();
 });

 it('should handle login submission', async () => {
 const { getByText, getByLabelText } = render(<LoginPage />);
 const emailInput = getByLabelText('Email:');
 const passwordInput = getByLabelText('Password:');
 const loginButton = getByText('Login');

 fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
 fireEvent.change(passwordInput, { target: { value: 'test-password' } });

 fireEvent.click(loginButton);

 await waitFor(() => expect(axios.post).toHaveBeenCalledTimes(1));
 });

 it('should handle login error', async () => {
 server.use(
 rest.post('/api/login', (req, res, ctx) => {
 return res(ctx.status(401), ctx.json({ error: 'Invalid credentials' }));
 }),
 );

 const { getByText, getByLabelText } = render(<LoginPage />);
 const emailInput = getByLabelText('Email:');
 const passwordInput = getByLabelText('Password:');
 const loginButton = getByText('Login');

 fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
 fireEvent.change(passwordInput, { target: { value: 'test-password' } });

 fireEvent.click(loginButton);

 await waitFor(() => expect(getByText('Invalid credentials')).toBeInTheDocument());
 });
});
