import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import LoginForm from '../components/LoginForm';

const server = setupServer(
 rest.post('/api/login', (req, res, ctx) => {
 return res(ctx.json({ token: 'test-token' }));
 }),
);

describe('LoginForm', () => {
 afterEach(() => server.resetHandlers());

 it('renders correctly', () => {
 const { getByText } = render(<LoginForm />);
 expect(getByText('Email:')).toBeInTheDocument();
 expect(getByText('Password:')).toBeInTheDocument();
 });

 it('submits form data correctly', async () => {
 const { getByText, getByLabelText } = render(<LoginForm />);
 const emailInput = getByLabelText('Email:');
 const passwordInput = getByLabelText('Password:');
 const submitButton = getByText('Login');

 fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
 fireEvent.change(passwordInput, { target: { value: 'test-password' } });
 fireEvent.click(submitButton);

 await waitFor(() => expect(server.handlers[0].ctx.request.body).toEqual({
 email: 'test@example.com',
 password: 'test-password',
 }));
 });
});
