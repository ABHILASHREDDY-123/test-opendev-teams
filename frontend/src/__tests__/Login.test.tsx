import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import Login from '../pages/Login';

const server = setupServer(
 rest.post('/api/auth/login', (req, res, ctx) => {
 return res(ctx.json({ token: 'test-token' }));
 }),
);

afterAll(() => server.close());

test('renders login form', () => {
 const { getByText, getByLabelText } = render(<Login />);
 expect(getByText('Login')).toBeInTheDocument();
 expect(getByLabelText('Email:')).toBeInTheDocument();
 expect(getByLabelText('Password:')).toBeInTheDocument();
});

test('submits login form', async () => {
 const { getByText, getByLabelText } = render(<Login />);
 const emailInput = getByLabelText('Email:');
 const passwordInput = getByLabelText('Password:');
 const submitButton = getByText('Login');

 fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
 fireEvent.change(passwordInput, { target: { value: 'test-password' } });

 await waitFor(() => fireEvent.click(submitButton));

 await waitFor(() => expect(server.handlers[0].ctx.request.body).toEqual({
 email: 'test@example.com',
 password: 'test-password',
 }));
});
