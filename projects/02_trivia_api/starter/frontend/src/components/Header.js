import React, { Component } from 'react';
import '../stylesheets/Header.css';

class Header extends Component {

  navTo(uri){
    window.location.href = window.location.origin + uri;
  }

  render() {
    return (
      <div className="App-header">
        <h1 onClick={() => {this.navTo('')}}>
          <img src="udacity-logo.svg" className="udacity-logo" alt="udacity-logo" />
          Udacitrivia
        </h1>
        <h2 onClick={() => {this.navTo('')}}>List</h2>
        <h2 onClick={() => {this.navTo('/add')}}>Add</h2>
        <h2 onClick={() => {this.navTo('/play')}}>Play</h2>
      </div>
    );
  }
}

export default Header;
