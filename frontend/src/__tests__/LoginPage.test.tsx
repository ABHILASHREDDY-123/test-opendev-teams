// Implement tests for LoginPage component
import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { LoginPage } from '../LoginPage';
test('renders login form', () => {
  const { getByPlaceholderText } = render(<LoginPage />);
  expect(getByPlaceholderText('Mobile Number')).toBeInTheDocument();
  expect(getByPlaceholderText('Password')).toBeInTheDocument();
});
test('submits login form', () => {
  const server = setupServer(
    rest.post('/api/auth/login', (req, res, ctx) => {
      return res(ctx.json({ token: 'example-token' }));
    })
  );
  const { getByPlaceholderText, getByText } = render(<LoginPage />);
  const mobileInput = getByPlaceholderText('Mobile Number');
  const passwordInput = getByPlaceholderText('Password');
  const submitButton = getByText('Login');
  fireEvent.change(mobileInput, { target: { value: '1234567890' } });
  fireEvent.change(passwordInput, { target: { value: 'password123' } });
  fireEvent.click(submitButton);
  waitFor(() => expect(server.handlers[0].ctx.request.body).toEqual({ mobile: '1234567890', password: 'password123' }));
});