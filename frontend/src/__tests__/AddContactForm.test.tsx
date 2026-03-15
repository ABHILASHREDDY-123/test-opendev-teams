import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import AddContactForm from '../AddContactForm';

const server = setupServer(
 rest.post('/api/contacts', (req, res, ctx) => {
 return res(ctx.json({ id: 1, name: 'John Doe', mobile: '1234567890' }));
 })
);

describe('AddContactForm', () => {
 afterEach(() => server.resetHandlers());

 it('renders add contact form', () => {
 const { getByText } = render(<AddContactForm />);
 expect(getByText('Name')).toBeInTheDocument();
 expect(getByText('Mobile')).toBeInTheDocument();
 expect(getByText('Add Contact')).toBeInTheDocument();
 });

 it('submits add contact form', async () => {
 const { getByText, getByLabelText } = render(<AddContactForm />);
 const nameInput = getByLabelText('Name');
 const mobileInput = getByLabelText('Mobile');
 const addContactButton = getByText('Add Contact');

 fireEvent.change(nameInput, { target: { value: 'John Doe' } });
 fireEvent.change(mobileInput, { target: { value: '1234567890' } });
 fireEvent.click(addContactButton);

 await waitFor(() => expect(server.handlers[0].ctx.request.body).toEqual({ name: 'John Doe', mobile: '1234567890' }));
 });
});
