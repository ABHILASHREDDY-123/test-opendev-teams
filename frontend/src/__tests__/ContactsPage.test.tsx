import React from 'react';
import { render, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import ContactsPage from '../ContactsPage';
import { getContacts } from '../api';

jest.mock('../api');

const mockContacts = [
  { id: '1', name: 'John Doe', mobile: '1234567890' },
  { id: '2', name: 'Jane Doe', mobile: '0987654321' },
];

beforeEach(() => {
  localStorage.setItem('token', 'test-token');
});

describe('ContactsPage', () => {
  it('renders contacts list', async () => {
    (getContacts as jest.Mock).mockResolvedValue(mockContacts);
    const { getByText } = render(
      <MemoryRouter>
        <ContactsPage />
      </MemoryRouter>
    );
    await waitFor(() => expect(getByText('John Doe')).toBeInTheDocument());
    expect(getByText('Jane Doe')).toBeInTheDocument();
  });

  it('shows empty state when no contacts', async () => {
    (getContacts as jest.Mock).mockResolvedValue([]);
    const { getByText } = render(
      <MemoryRouter>
        <ContactsPage />
      </MemoryRouter>
    );
    await waitFor(() => expect(getByText('No contacts yet. Add your first contact!')).toBeInTheDocument());
  });
});