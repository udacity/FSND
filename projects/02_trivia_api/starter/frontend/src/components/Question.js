import React, { Component } from 'react';
import '../stylesheets/Question.css';

class Question extends Component {
  constructor(){
    super();
    this.state = {
      visibleAnswer: false
    }
  }

  flipVisibility() {
    this.setState({visibleAnswer: !this.state.visibleAnswer});
  }

  render() {
    const { question, answer, category, difficulty } = this.props;

    return (
      <div className="Question-holder">
        <div className="question-category">
          <img className="category" alt="category" src={`${category.toLowerCase()}.svg`}/>
          <div className="Question">{question}</div>
          <div className="question-actions">
            <div className="difficulty">
              <img className="category" alt="category" src="progress-bar.png"/>
              Difficulty: {difficulty}
            </div>
            <div
              onClick={() => this.flipVisibility()}>
              <img src={this.state.visibleAnswer?'no-visible.png':'visible.png'} className="visible" alt="visibility" />
            </div>
            <img src="delete.svg" className="delete" alt="delete"  onClick={() => this.props.questionAction('DELETE')}/>
          </div>
        </div>
        
        <div className="answer-holder">
          <span style={{"visibility": this.state.visibleAnswer ? 'visible' : 'hidden'}}>Answer: {answer}</span>
        </div>
      </div>
    );
  }
}

export default Question;
