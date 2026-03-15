import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoginPage from './LoginPage';
import ContactsPage from './ContactsPage';
import AddContactForm from './AddContactForm';

const App = () => {
 return (
 <BrowserRouter>
 <Routes>
 <Route path='/login' element={<LoginPage />} />
 <Route path='/contacts' element={<ContactsPage />} />
 <Route path='/add-contact' element={<AddContactForm />} />
 </Routes>
 </BrowserRouter>
 );
};

export default App;
