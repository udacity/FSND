// import React from 'react';
// import { BrowserRouter as Router, Route, Switch } from 'react-router-dom'; // import logo from './logo.svg';

// import './stylesheets/App.css';
// import FormView from './components/FormView';
// import QuestionView from './components/QuestionView';
// import Header from './components/Header';
// import QuizView from './components/QuizView';

// class App extends React.Component {
//   render() {
//     return /*#__PURE__*/React.createElement("div", {
//       className: "App"
//     }, /*#__PURE__*/React.createElement(Header, {
//       path: true
//     }), /*#__PURE__*/React.createElement(Router, null, /*#__PURE__*/React.createElement(Switch, null, /*#__PURE__*/React.createElement(Route, {
//       path: "/",
//       exact: true,
//       component: QuestionView
//     }), /*#__PURE__*/React.createElement(Route, {
//       path: "/add",
//       component: FormView
//     }), /*#__PURE__*/React.createElement(Route, {
//       path: "/play",
//       component: QuizView
//     }), /*#__PURE__*/React.createElement(Route, {
//       component: QuestionView
//     }))));
//   }

// }

// export default App;


import React, { Component } from 'react';
import {
  BrowserRouter as Router,
  Route,
  Switch
} from 'react-router-dom'

// import logo from './logo.svg';
import './stylesheets/App.css';
import FormView from './components/FormView';
import QuestionView from './components/QuestionView';
import Header from './components/Header';
import QuizView from './components/QuizView';


class App extends Component {
  render() {
    return (
    <div className="App">
      <Header path />
      <Router>
        <Switch>
          <Route path="/" exact component={QuestionView} />
          <Route path="/add" component={FormView} />
          <Route path="/play" component={QuizView} />
          <Route component={QuestionView} />
        </Switch>
      </Router>
    </div>
  );

  }
}

export default App;
