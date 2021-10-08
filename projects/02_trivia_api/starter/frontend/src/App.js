import React, { Component } from 'react';
import {
  BrowserRouter as Router,
  Route,
  Switch
} from 'react-router-dom'
import './stylesheets/App.css';
import FormView from './components/FormView';
import QuestionView from './components/QuestionView';
import Header from './components/Header';
import QuizView from './components/QuizView';


class App extends Component {



  render (){
    return (
      <div className="App">
        <Header path />
        <Router>
          <Switch>
            <Route path="/" exact>
              <QuestionView />
            </Route>
            <Route path="/add">
              <FormView/>
            </Route>
            <Route path="/play">
              <QuizView />
            </Route>
            <Route>
              <QuestionView />
            </Route>
          </Switch>
        </Router>
      </div>
  );
  }

}

export default App;
