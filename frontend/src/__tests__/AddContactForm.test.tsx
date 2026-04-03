import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import AddContactForm from '../AddContactForm';
import { addContact } from '../api';

jest.mock('../api');

beforeEach(() => {
  localStorage.setItem('token', 'test-token');
});

describe('AddContactForm', () => {
  it('renders form fields', () => {
    const { getByLabelText } = render(<AddContactForm onAddContact={jest.fn()} />);
    expect(getByLabelText('Name:')).toBeInTheDocument();
    expect(getByLabelText('Mobile:')).toBeInTheDocument();
  });

  it('validates name field', async () => {
    const { getByText, getByLabelText } = render(<AddContactForm onAddContact={jest.fn()} />);
    const nameInput = getByLabelText('Name:');
    const mobileInput = getByLabelText('Mobile:');
    fireEvent.change(nameInput, { target: { value: '' } });
    fireEvent.change(mobileInput, { target: { value: '1234567890' } });
    fireEvent.click(getByText('Add Contact'));
    await waitFor(() => expect(getByText('Name must be at least 2 characters')).toBeInTheDocument());
  });

  it('validates mobile field', async () => {
    const { getByText, getByLabelText } = render(<AddContactForm onAddContact={jest.fn()} />);
    const nameInput = getByLabelText('Name:');
    const mobileInput = getByLabelText('Mobile:');
    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(mobileInput, { target: { value: '123' } });
    fireEvent.click(getByText('Add Contact'));
    await waitFor(() => expect(getByText('Invalid mobile number')).toBeInTheDocument());
  });
});