// Main app with routing
import React from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import LoginPage from './LoginPage';
import ContactsPage from './ContactsPage';

const App = () => {
 return (
 <BrowserRouter>
 <Routes>
 <Route path="/" element={<LoginPage />} />
 <Route path="/contacts" element={<ContactsPage />} />
 </Routes>
 </BrowserRouter>
 );
};

export default App;