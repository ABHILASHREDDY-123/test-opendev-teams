import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import AddContactForm from '../AddContactForm';
import { addContact } from '../api';

jest.mock('../api');

const token = 'test-token';
localStorage.setItem('token', token);

describe('AddContactForm', () => {
  it('renders form', () => {
    const { getByPlaceholderText } = render(<AddContactForm />);
    expect(getByPlaceholderText('Name')).toBeInTheDocument();
    expect(getByPlaceholderText('Mobile')).toBeInTheDocument();
  });

  it('validates name', async () => {
    const { getByText, getByPlaceholderText } = render(<AddContactForm />);
    const nameInput = getByPlaceholderText('Name');
    const mobileInput = getByPlaceholderText('Mobile');
    const submitButton = getByText('Add Contact');

    fireEvent.change(nameInput, { target: { value: '' } });
    fireEvent.change(mobileInput, { target: { value: '1234567890' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(addContact).not.toHaveBeenCalled();
    });
  });
});