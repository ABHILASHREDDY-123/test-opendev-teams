import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import axios from 'axios';
import LoginForm from './LoginForm';

const server = setupServer(
 rest.post('/api/login', (req, res, ctx) => {
 return res(ctx.json({ token: 'test-token' }));
 }),
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('renders login form', () => {
 const { getByText } = render(<LoginForm />);
 expect(getByText('Email:')).toBeInTheDocument();
 expect(getByText('Password:')).toBeInTheDocument();
 expect(getByText('Login')).toBeInTheDocument();
});

test('submits login form', async () => {
 const { getByText, getByLabelText } = render(<LoginForm />);
 const emailInput = getByLabelText('Email:');
 const passwordInput = getByLabelText('Password:');
 const submitButton = getByText('Login');

 fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
 fireEvent.change(passwordInput, { target: { value: 'test-password' } });

 fireEvent.click(submitButton);

 await waitFor(() => expect(axios.post).toHaveBeenCalledTimes(1));
});
