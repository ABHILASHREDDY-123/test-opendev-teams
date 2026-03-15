import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import LoginForm from './LoginForm';

describe('LoginForm', () => {
 it('renders correctly', () => {
 const { getByText } = render(<LoginForm onSubmit={() => {}} />);
 expect(getByText('Username:')).toBeInTheDocument();
 expect(getByText('Password:')).toBeInTheDocument();
 expect(getByText('Login')).toBeInTheDocument();
 });

 it('submits form with username and password', () => {
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

 it('displays error message when form is incomplete', () => {
 const { getByText, queryByText } = render(<LoginForm onSubmit={() => {}} />);
 const submitButton = getByText('Login');

 fireEvent.click(submitButton);

 expect(getByText('Please fill in all fields')).toBeInTheDocument();
 });

 it('displays loading state when submitting', () => {
 const { getByText, queryByText } = render(<LoginForm onSubmit={() => {}} />);
 const submitButton = getByText('Login');

 fireEvent.click(subButton);

 expect(getByText('Loading...')).toBeInTheDocument();
 });
});
