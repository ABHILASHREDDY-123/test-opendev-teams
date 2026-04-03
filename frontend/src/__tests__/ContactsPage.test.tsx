import React from 'react';
import { render, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import ContactsPage from '../ContactsPage';
import { getContacts } from '../api';

jest.mock('../api');

const token = 'test-token';
localStorage.setItem('token', token);

describe('ContactsPage', () => {
  it('renders contacts list', async () => {
    getContacts.mockResolvedValue([
      { id: '1', name: 'John Doe', mobile: '1234567890' },
      { id: '2', name: 'Jane Doe', mobile: '0987654321' },
    ]);

    const { getByText } = render(
      <MemoryRouter>
        <ContactsPage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(getByText('John Doe - 1234567890')).toBeInTheDocument();
      expect(getByText('Jane Doe - 0987654321')).toBeInTheDocument();
    });
  });
});