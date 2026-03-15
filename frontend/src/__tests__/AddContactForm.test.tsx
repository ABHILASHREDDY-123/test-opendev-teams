// Test for add contact form
import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import AddContactForm from '../AddContactForm';

const server = setupServer(
 rest.post('/contacts', (req, res, ctx) => {
 return res(ctx.json({ id: 1, name: 'John Doe', mobile: '1234567890' }));
 })
);

describe('Add Contact Form', () => {
 afterEach(() => server.resetHandlers());

 it('renders form', () => {
 const { getByText } = render(<AddContactForm />);
 expect(getByText('Name')).toBeInTheDocument();
 expect(getByText('Mobile')).toBeInTheDocument();
 });

 it('submits form', async () => {
 const { getByText, getByLabelText } = render(<AddContactForm />);
 const nameInput = getByLabelText('Name');
 const mobileInput = getByLabelText('Mobile');
 const submitButton = getByText('Add Contact');

 fireEvent.change(nameInput, { target: { value: 'John Doe' } });
 fireEvent.change(mobileInput, { target: { value: '1234567890' } });
 fireEvent.click(submitButton);

 await waitFor(() => expect(submitButton).toBeDisabled());
 });
});
