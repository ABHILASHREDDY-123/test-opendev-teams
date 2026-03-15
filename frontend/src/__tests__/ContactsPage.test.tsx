// Test for contacts page
import React from 'react';
import { render, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import ContactsPage from '../ContactsPage';

const server = setupServer(
 rest.get('/contacts', (req, res, ctx) => {
 return res(ctx.json([
 { id: 1, name: 'John Doe', mobile: '1234567890' },
 { id: 2, name: 'Jane Doe', mobile: '9876543210' }
 ]));
 })
);

describe('Contacts Page', () => {
 afterEach(() => server.resetHandlers());

 it('renders contacts list', async () => {
 const { getAllByRole } = render(<ContactsPage />);
 await waitFor(() => expect(getAllByRole('listitem')).toHaveLength(2));
 });

 it('renders loading state', () => {
 const { queryAllByRole } = render(<ContactsPage />);
 expect(queryAllByRole('listitem')).toHaveLength(0);
 });
});
