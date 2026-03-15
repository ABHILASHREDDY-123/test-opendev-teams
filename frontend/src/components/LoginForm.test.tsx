import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import LoginForm from './LoginForm';

describe('LoginForm component', () => {
 it('renders username and password fields', () => {
 const { getByLabelText } = render(<LoginForm onSubmit={() => {}} />);
 expect(getByLabelText('Username:')).toBeInTheDocument();
 expect(getByLabelText('Password:')).toBeInTheDocument();
 });

 it('submits the form with username and password', () => {
 const onSubmit = jest.fn();
 const { getByLabelText, getByText } = render(<LoginForm onSubmit={onSubmit} />);
 const usernameInput = getByLabelText('Username:');
 const passwordInput = getByLabelText('Password:');
 const submitButton = getByText('Login');

 fireEvent.change(usernameInput, { target: { value: 'testuser' } });
 fireEvent.change(passwordInput, { target: { value: 'testpassword' } });
 fireEvent.click(submitButton);

 expect(onSubmit).toHaveBeenCalledTimes(1);
 expect(onSubmit).toHaveBeenCalledWith('testuser', 'testpassword');
 });

 it('displays error message when username or password is missing', () => {
 const { getByLabelText, getByText, queryByText } = render(<LoginForm onSubmit={() => {}} />);
 const usernameInput = getByLabelText('Username:');
 const passwordInput = getByLabelText('Password:');
 const submitButton = getByText('Login');

 fireEvent.change(usernameInput, { target: { value: '' } });
 fireEvent.change(passwordInput, { target: { value: 'testpassword' } });
 fireEvent.click(submitButton);

 expect(getByText('Please fill in both username and password')).toBeInTheDocument();
 });
});
