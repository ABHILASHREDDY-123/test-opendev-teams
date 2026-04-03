import React from 'react';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import ContactsPage from '../ContactsPage';
import { getContacts } from '../api';

jest.mock('../api');

describe('ContactsPage', () => {
  it('renders contacts list', async () => {
    (getContacts as jest.Mock).mockResolvedValue([
      { id: '1', name: 'Test Contact', mobile: '1234567890', owner_id: 'user1' },
    ]);
    const { getByText } = render(
      <MemoryRouter>
        <ContactsPage />
      </MemoryRouter>
    );
    expect(getByText('Test Contact')).toBeInTheDocument();
  });
});