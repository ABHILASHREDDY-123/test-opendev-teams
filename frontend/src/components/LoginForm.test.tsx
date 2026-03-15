import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import axios from 'axios';
import LoginForm from './LoginForm';

const server = setupServer(
 rest.post('/api/login', (req, res, ctx) => {
 return res(ctx.json({ token: 'mock-token' }));
 }),
);

afterEach(() => server.resetHandlers());

afterAll(() => server.close());

describe('LoginForm', () => {
 it('renders form with email and password fields', () => {
 const { getByLabelText } = render(<LoginForm />);
 expect(getByLabelText('Email:')).toBeInTheDocument();
 expect(getByLabelText('Password:')).toBeInTheDocument();
 });

 it('submits form with valid credentials', async () => {
 const { getByLabelText, getByText } = render(<LoginForm />);
 const emailInput = getByLabelText('Email:');
 const passwordInput = getByLabelText('Password:');
 const submitButton = getByText('Login');

 fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
 fireEvent.change(passwordInput, { target: { value: 'password123' } });

 fireEvent.click(submitButton);

 await waitFor(() => expect(axios.post).toHaveBeenCalledTimes(1));
 });

 it('displays error message on submission failure', async () => {
 server.use(
 rest.post('/api/login', (req, res, ctx) => {
 return res(ctx.status(500), ctx.json({ error: 'Mock error' }));
 }),
 );
 const { getByLabelText, getByText, queryByText } = render(<LoginForm />);
 const emailInput = getByLabelText('Email:');
 const passwordInput = getByLabelText('Password:');
 const submitButton = getByText('Login');

 fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
 fireEvent.change(passwordInput, { target: { value: 'password123' } });

 fireEvent.click(submitButton);

 await waitFor(() => expect(queryByText('Mock error')).toBeInTheDocument());
 });
});
