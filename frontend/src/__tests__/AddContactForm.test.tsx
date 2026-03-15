import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import AddContactForm from '../AddContactForm';
import { addContact } from '../api';

jest.mock('../api');

describe('AddContactForm', () => {
  it('renders form', () => {
    const { getByPlaceholderText, getByText } = render(
      <MemoryRouter>
        <AddContactForm />
      </MemoryRouter>
    );
    expect(getByPlaceholderText('Name')).toBeInTheDocument();
    expect(getByPlaceholderText('Mobile')).toBeInTheDocument();
    expect(getByText('Add Contact')).toBeInTheDocument();
  });

  it('shows success message on successful submission', async () => {
    (addContact as jest.Mock).mockResolvedValue({});
    const { getByText, getByPlaceholderText } = render(
      <MemoryRouter>
        <AddContactForm />
      </MemoryRouter>
    );
    const nameInput = getByPlaceholderText('Name');
    const mobileInput = getByPlaceholderText('Mobile');
    const submitButton = getByText('Add Contact');

    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(mobileInput, { target: { value: '1234567890' } });
    fireEvent.click(submitButton);

    await waitFor(() => expect(getByText('Contact added successfully!')).toBeInTheDocument());
  });
});