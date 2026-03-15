// Implement tests for ContactsPage component
import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { ContactsPage } from '../ContactsPage';
test('renders contacts list', () => {
 const { getByText } = render(<ContactsPage contacts={[{ name: 'John Doe', mobile: '1234567890' }]} />);
 expect(getByText('John Doe')).toBeInTheDocument();
 expect(getByText('1234567890')).toBeInTheDocument();
});
test('renders empty state', () => {
 const { getByText } = render(<ContactsPage contacts={[]} />);
 expect(getByText('No contacts yet. Add your first contact!')).toBeInTheDocument();
});