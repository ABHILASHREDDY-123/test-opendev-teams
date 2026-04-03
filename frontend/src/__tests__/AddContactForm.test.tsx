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
});