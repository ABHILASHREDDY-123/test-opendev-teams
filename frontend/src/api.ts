import fetch from 'node-fetch';

const apiURL = 'https://example.com/api';

const login = async (mobile: string, password: string) => {
 const response = await fetch(
 `${apiURL}/auth/login`,
 {
 method: 'POST',
 headers: {
 'Content-Type': 'application/json',
 },
 body: JSON.stringify({ mobile, password }),
 }
 );
 const data = await response.json();
 return data;
};

const getContacts = async (token: string) => {
 const response = await fetch(`${apiURL}/contacts`, {
 method: 'GET',
 headers: {
 Authorization: `Bearer ${token}`,
 },
 });
 const data = await response.json();
 return data;
};

const addContact = async (token: string, name: string, mobile: string) => {
 const response = await fetch(`${apiURL}/contacts`, {
 method: 'POST',
 headers: {
 'Content-Type': 'application/json',
 Authorization: `Bearer ${token}`,
 },
 body: JSON.stringify({ name, mobile }),
 });
 const data = await response.json();
 return data;
};

const updateContact = async (token: string, id: string, data: any) => {
 const response = await fetch(`${apiURL}/contacts/${id}`, {
 method: 'PUT',
 headers: {
 'Content-Type': 'application/json',
 Authorization: `Bearer ${token}`,
 },
 body: JSON.stringify(data),
 });
 const jsonData = await response.json();
 return jsonData;
};

const deleteContact = async (token: string, id: string) => {
 const response = await fetch(`${apiURL}/contacts/${id}`, {
 method: 'DELETE',
 headers: {
 Authorization: `Bearer ${token}`,
 },
 });
 return response.status;
};

export { login, getContacts, addContact, updateContact, deleteContact };
