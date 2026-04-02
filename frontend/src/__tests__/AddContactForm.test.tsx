import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import AddContactForm from '../AddContactForm';
import { addContact } from '../api';

jest.mock('../api');

describe('AddContactForm', () => {
  beforeEach(() => {
    localStorage.setItem('token', 'mock-token');
  });

  afterEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
  });

  it('renders form', () => {
    const { getByPlaceholderText, getByText } = render(
      <MemoryRouter>
        <AddContactForm />
      </MemoryRouter>
    );
    expect(getByPlaceholderText('Name')).toBeInTheDocument();
    expect(getByPlaceholderText('Mobile number')).toBeInTheDocument();
    expect(getByText('Add Contact')).toBeInTheDocument();
  });

  it('validates name', async () => {
    const { getByPlaceholderText, getByText } = render(
      <MemoryRouter>
        <AddContactForm />
      </MemoryRouter>
    );
    const nameInput = getByPlaceholderText('Name');
    const mobileInput = getByPlaceholderText('Mobile number');
    const submitButton = getByText('Add Contact');

    fireEvent.change(nameInput, { target: { value: '' } });
    fireEvent.change(mobileInput, { target: { value: '1234567890' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(addContact).not.toHaveBeenCalled();
    });
  });
});