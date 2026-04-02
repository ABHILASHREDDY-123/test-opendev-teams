import React from 'react';
import { render, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import ContactsPage from '../ContactsPage';
import { getContacts } from '../api';

jest.mock('../api');

const mockContacts = [
  { id: '1', name: 'John Doe', mobile: '1234567890' },
  { id: '2', name: 'Jane Doe', mobile: '0987654321' }
];

describe('ContactsPage', () => {
  beforeEach(() => {
    localStorage.setItem('token', 'mock-token');
  });

  afterEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
  });

  it('renders contacts list', async () => {
    jest.mocked(getContacts).mockResolvedValue(mockContacts);
    const { getByText } = render(
      <MemoryRouter>
        <ContactsPage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(getByText('John Doe')).toBeInTheDocument();
      expect(getByText('1234567890')).toBeInTheDocument();
      expect(getByText('Jane Doe')).toBeInTheDocument();
      expect(getByText('0987654321')).toBeInTheDocument();
    });
  });

  it('shows empty state', async () => {
    jest.mocked(getContacts).mockResolvedValue([]);
    const { getByText } = render(
      <MemoryRouter>
        <ContactsPage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(getByText('No contacts yet. Add your first contact!')).toBeInTheDocument();
    });
  });
});