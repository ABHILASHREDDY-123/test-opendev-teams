import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import LoginPage from './LoginPage';
import ProfilePage from './ProfilePage';

const App: React.FC = () => {
  return (
    <Router>
      <Switch>
        <Route path="/login" component={LoginPage} />
        <Route path="/profile" component={ProfilePage} />
        <Route path="/" exact component={LoginPage} />
      </Switch>
    </Router>
  );
};

export default App;
