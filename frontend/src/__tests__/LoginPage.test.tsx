import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import LoginPage from '../LoginPage';

const server = setupServer(
 rest.post('/api/auth/login', (req, res, ctx) => {
 return res(ctx.json({ token: 'test-token' }));
 })
);

describe('LoginPage', () => {
 afterEach(() => server.resetHandlers());

 it('renders login form', () => {
 const { getByText } = render(<LoginPage />);
 expect(getByText('Mobile')).toBeInTheDocument();
 expect(getByText('Password')).toBeInTheDocument();
 expect(getByText('Login')).toBeInTheDocument();
 });

 it('submits login form', async () => {
 const { getByText, getByLabelText } = render(<LoginPage />);
 const mobileInput = getByLabelText('Mobile');
 const passwordInput = getByLabelText('Password');
 const loginButton = getByText('Login');

 fireEvent.change(mobileInput, { target: { value: '1234567890' } });
 fireEvent.change(passwordInput, { target: { value: 'password123' } });
 fireEvent.click(loginButton);

 await waitFor(() => expect(server.handlers[0].ctx.request.body).toEqual({ mobile: '1234567890', password: 'password123' }));
 });
});
