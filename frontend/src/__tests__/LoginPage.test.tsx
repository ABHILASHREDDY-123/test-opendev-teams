import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import LoginPage from '../LoginPage';

const server = setupServer(
 rest.post('/api/login', (req, res, ctx) => {
 return res(ctx.json({ token: 'test-token' }));
 })
);

afterEach(() => server.resetHandlers());

afterAll(() => server.close());

test('renders login form', () => {
 const { getByText } = render(<LoginPage />);
 expect(getByText('Login')).toBeInTheDocument();
});

test('submits login form', async () => {
 const { getByText, getByLabelText } = render(<LoginPage />);
 const mobileInput = getByLabelText('Mobile');
 const passwordInput = getByLabelText('Password');
 const submitButton = getByText('Login');

 fireEvent.change(mobileInput, { target: { value: '1234567890' } });
 fireEvent.change(passwordInput, { target: { value: 'password' } });
 fireEvent.click(submitButton);

 await waitFor(() => expect(getByText('Login')).toBeInTheDocument());
});
