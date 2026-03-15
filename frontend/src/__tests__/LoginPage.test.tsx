import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import axios from 'axios';
import LoginPage from '../LoginPage';

const server = setupServer(
 rest.post('/api/login', (req, res, ctx) => {
 return res(ctx.json({ token: 'test-token' }));
 }),
);

afterAll(() => server.close());

test('renders login page', () => {
 const { getByText } = render(<LoginPage />);
 expect(getByText('Login Page')).toBeInTheDocument();
});

test('submits login form', async () => {
 const { getByLabelText, getByText } = render(<LoginPage />);
 const emailInput = getByLabelText('Email:');
 const passwordInput = getByLabelText('Password:');
 const submitButton = getByText('Login');

 fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
 fireEvent.change(passwordInput, { target: { value: 'test-password' } });

 fireEvent.click(submitButton);

 await waitFor(() => expect(axios.post).toHaveBeenCalledTimes(1));
});
