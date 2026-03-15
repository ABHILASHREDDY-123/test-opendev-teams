import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import Login from '../pages/Login';

const server = setupServer(
 rest.post('/api/auth/login', (req, res, ctx) => {
 return res(ctx.json({ token: 'test-token' }));
 })
);

describe('Login', () => {
 afterEach(() => server.resetHandlers());

 it('renders login form', () => {
 const { getByText } = render(<Login />);
 expect(getByText('Login')).toBeInTheDocument();
 });

 it('submits login form', async () => {
 const { getByText, getByLabelText } = render(<Login />);
 const emailInput = getByLabelText('Email:');
 const passwordInput = getByLabelText('Password:');
 const submitButton = getByText('Login');

 fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
 fireEvent.change(passwordInput, { target: { value: 'test-password' } });

 fireEvent.click(submitButton);

 await waitFor(() => expect(getByText('Loading...')).toBeInTheDocument());
 });
});
