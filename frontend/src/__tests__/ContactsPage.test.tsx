import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import ContactsPage from '../ContactsPage';

const server = setupServer(
  rest.get('/api/contacts', (req, res, ctx) => {
    return res(
      ctx.json([
        { id: 1, name: 'John Doe', mobile: '1234567890' },
        { id: 2, name: 'Jane Doe', mobile: '9876543210' },
      ])
    );
  })
);

afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('renders contacts list', async () => {
  const { getAllByRole } = render(<ContactsPage />);
  await waitFor(() => expect(getAllByRole('listitem')).toHaveLength(2));
});

test('renders empty contacts list', async () => {
  server.use(
    rest.get('/api/contacts', (req, res, ctx) => {
      return res(ctx.json([]));
    })
  );
  const { queryAllByRole } = render(<ContactsPage />);
  await waitFor(() => expect(queryAllByRole('listitem')).toHaveLength(0));
});