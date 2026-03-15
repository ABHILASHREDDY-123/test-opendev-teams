// Implement tests for AddContactForm component
import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { AddContactForm } from '../AddContactForm';
test('renders add contact form', () => {
 const { getByPlaceholderText } = render(<AddContactForm />);
 expect(getByPlaceholderText('Name')).toBeInTheDocument();
 expect(getByPlaceholderText('Mobile Number')).toBeInTheDocument();
});
test('submits add contact form', () => {
 const server = setupServer(
 rest.post('/api/contacts', (req, res, ctx) => {
 return res(ctx.json({ id: 1, name: 'John Doe', mobile: '1234567890' }));
 })
 );
 const { getByPlaceholderText, getByText } = render(<AddContactForm />);
 const nameInput = getByPlaceholderText('Name');
 const mobileInput = getByPlaceholderText('Mobile Number');
 const submitButton = getByText('Add Contact');
 fireEvent.change(nameInput, { target: { value: 'John Doe' } });
 fireEvent.change(mobileInput, { target: { value: '1234567890' } });
 fireEvent.click(submitButton);
 waitFor(() => expect(server.handlers[0].ctx.request.body).toEqual({ name: 'John Doe', mobile: '1234567890' }));
});