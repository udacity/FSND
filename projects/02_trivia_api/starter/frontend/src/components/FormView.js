import React, { Component } from 'react';

import '../stylesheets/FormView.css';

class FormView extends Component {
  constructor(props){
    super();
    this.state = {
      question: "",
      answer: "",
      difficulty: 1,
      category: 1,
      categories: []
    }
  }

  componentDidMount(){
    fetch('/categories',{
      method: 'GET',
      headers: {
        'Content-Type': 'application/json;charset=utf-8'
      },
    }).then((res) => res.json())
    .then(({categories}) => {
      this.setState({categories});
    }).catch((error) => {
      alert('Unable to load categories. Please try your request again')
      return;
    })
  }

  submitQuestion = (event) => {
    event.preventDefault();
    fetch(`/questions`,{
      method: 'POST',
      headers: {
        'Content-Type': 'application/json;charset=utf-8'
      },
      body: JSON.stringify({
        question: this.state.question,
        answer: this.state.answer,
        difficulty: Number(this.state.difficulty),
        category: Number(this.state.category)
      }),
    })
    .then( () => {
      document.getElementById("add-question-form").reset();
      return;
    }).catch((error) => {
        alert('Unable to add question. Please try your request again')
        return;
    })
  }

  handleChange = (event) => {
    this.setState({[event.target.name]: event.target.value})
  }

  render() {
    return (
      <div id="add-form">
        <h2>Add a New Trivia Question</h2>
        <form className="form-view" id="add-question-form" onSubmit={this.submitQuestion}>
          <label>
            Question
            <input type="text" className="form-input" name="question" onChange={this.handleChange}/>
          </label>
          <label>
            Answer
            <input type="text"  className="form-input" name="answer" onChange={this.handleChange}/>
          </label>
          <label>
            Difficulty
            <select name="difficulty"  className="form-input" onChange={this.handleChange}>
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="4">4</option>
              <option value="5">5</option>
            </select>
          </label>
          <label>
            Category
            <select name="category"  className="form-input" onChange={this.handleChange}>
              {this.state.categories.map(({id, type}) => {
                  return (
                    <option key={id} value={id}>{type}</option>
                  )
                })}
            </select>
          </label>
          <input type="submit" className="button" value="Submit" />
        </form>
      </div>
    );
  }
}

export default FormView;
