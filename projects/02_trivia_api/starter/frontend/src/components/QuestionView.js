import React, { Component } from 'react';

import '../stylesheets/App.css';
import Question from './Question';
import Search from './Search';
import _ from 'lodash'

class QuestionView extends Component {
  constructor(){
    super();
    this.state = {
      questions: [],
      page: 1,
      totalQuestions: 0,
      categories: [],
      currentCategory: null,
    }
  }

  componentDidMount() {
    this.getQuestions();
    this.getCategories();
  }

  getCategories =  () => {
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

  getQuestions = () => {
    fetch(`/questions?page=${this.state.page}`,{
      method: 'GET',
      headers: {
        'Content-Type': 'application/json;charset=utf-8'
      },
    }).then((res) => res.json())
      .then(({questions, total_questions, current_category}) => {
        this.setState({
            questions: questions,
            totalQuestions: total_questions,
            currentCategory: current_category })
      }).catch((error) => {
        alert('Unable to load questions. Please try your request again')
      return;
    })
  }

  selectPage(num) {
    this.setState({page: num}, () => this.getQuestions());
  }

  createPagination(){
    let pageNumbers = [];
    let maxPage = Math.ceil(this.state.totalQuestions / 10)
    for (let i = 1; i <= maxPage; i++) {
      pageNumbers.push(
        <span
          key={i}
          className={`page-num ${i === this.state.page ? 'active' : ''}`}
          onClick={() => {this.selectPage(i)}}>{i}
        </span>)
    }
    return pageNumbers;
  }

  getByCategory= (id) => {
    fetch(`/categories/${id}/questions`,{
      method: 'GET',
      headers: {
        'Content-Type': 'application/json;charset=utf-8'
      },
    }).then((res) => res.json())
    .then(({questions, total_questions, current_category}) => {
      this.setState({
          questions: questions,
          totalQuestions: total_questions,
          currentCategory: current_category })
    }).catch((error) => {
        alert('Unable to load questions. Please try your request again')
      return;
    })
  }

  submitSearch = (searchTerm) => {
    fetch(`/questions/search`,{
      method: 'POST',
      headers: {
        'Content-Type': 'application/json;charset=utf-8'
      },
      body: JSON.stringify({searchTerm: searchTerm}),
    }).then((res) => res.json())
    .then(({questions, total_questions, current_category}) => {
      this.setState({
          questions: questions,
          totalQuestions: total_questions,
          currentCategory: current_category })
    }).catch((error) => {
        alert('Unable to load questions. Please try your request again')
      return;
    })
  }

  questionAction = (id) => (action) => {
    if(action === 'DELETE') {
      if(window.confirm('are you sure you want to delete the question?')) {
        fetch(`/questions/${id}`,{
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json;charset=utf-8'
          },
        })
        .then(() => {
          this.getQuestions();
        }).catch((error) => {
            alert('Unable to load questions. Please try your request again')
        return;
      })
      }
    }
  }

  render() {

    return (
      <>
      <div className="question-view">
        <div className="categories-list">
          <h2 onClick={this.getQuestions}>Categories</h2>
          <ul>
            {this.state.categories.map(({id, type}) => (
              <li key={id} onClick={() => {this.getByCategory(id)}}>
                <img className="category" alt={`category-${type.toLowerCase()}`} src={`${type.toLowerCase()}.svg`}/>
                {type}
              </li>
            ))}
          </ul>
        </div>
        <div className="questions-list">
          <h2>Questions</h2>
            <div>
              <Search submitSearch={this.submitSearch}/>
            </div>
            <div class="question-container">
              {!_.isEmpty(this.state.categories) && this.state.questions.map((q) => {
            return (
              <Question
                key={q.id}
                question={q.question}
                answer={q.answer}

                category={this.state.categories.find((c) => c.id == q.category)['type']} 
                difficulty={q.difficulty}
                questionAction={this.questionAction(q.id)}
              />
            )})}
            </div>
          <div className="pagination-menu">
            {this.createPagination()}
          </div>
        </div>

      </div>
      </>
    );
  }
}

export default QuestionView;
