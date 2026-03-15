// Test the LoginPage component
import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import axios from 'axios';
import LoginPage from '../components/LoginPage';

const server = setupServer(
 rest.post('/api/login', (req, res, ctx) => {
 return res(ctx.json({ message: 'Logged in successfully' }));
 }),
);

describe('LoginPage', () => {
 afterEach(() => server.resetHandlers());

 it('renders the login form', () => {
 const { getByText } = render(<LoginPage />);
 expect(getByText('Login Page')).toBeInTheDocument();
 expect(getByText('Email:')).toBeInTheDocument();
 expect(getByText('Password:')).toBeInTheDocument();
 expect(getByText('Login')).toBeInTheDocument();
 });

 it('submits the form and displays a success message', async () => {
 const { getByText, getByLabelText } = render(<LoginPage />);
 const emailInput = getByLabelText('Email:');
 const passwordInput = getByLabelText('Password:');
 const loginButton = getByText('Login');

 fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
 fireEvent.change(passwordInput, { target: { value: 'password123' } });
 fireEvent.click(loginButton);

 await waitFor(() => expect(getByText('Logged in successfully')).toBeInTheDocument());
 });

 it('displays an error message when the login fails', async () => {
 server.use(
 rest.post('/api/login', (req, res, ctx) => {
 return res(
 ctx.status(401),
 ctx.json({ message: 'Invalid email or password' }),
 );
 }),
 );

 const { getByText, getByLabelText } = render(<LoginPage />);
 const emailInput = getByLabelText('Email:');
 const passwordInput = getByLabelText('Password:');
 const loginButton = getByText('Login');

 fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
 fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
 fireEvent.click(loginButton);

 await waitFor(() => expect(getByText('Invalid email or password')).toBeInTheDocument());
 });
});
