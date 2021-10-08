import React, { Component } from 'react';
import '../stylesheets/QuizView.css';

const questionsPerPlay = 5; 

class QuizView extends Component {

  constructor(){
    super();
    this.state = {
      quizCategory: null,
      previousQuestions: [],
      showAnswer: false,
      numCorrect: 0,
      currentQuestion: {},
      guess: '',
      forceEnd: null,
      categories: []
    }
  }

  componentDidMount() {
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

  selectCategory = async ({type, id=0}) => {
    await this.setState({ quizCategory : {type:type, id:id}})
    this.getNextQuestion()
  }

  handleChange = (event) => {
    this.setState({[event.target.name]: event.target.value})
  }

  getNextQuestion =  () => {
    if(this.state.currentQuestion.id) { this.state.previousQuestions.push(this.state.currentQuestion.id) }
    fetch('/quizzes',{
      method: 'POST',
      headers: {
        'Content-Type': 'application/json;charset=utf-8'
      },
      body: JSON.stringify({
        previous_questions: this.state.previousQuestions,
        quiz_category: this.state.quizCategory 
      })
    }).then((res) => res.json())
    .then( async ({question}) => {
      await this.setState({
        currentQuestion: question,
        showAnswer: false,
        previousQuestions: this.state.previousQuestions,
        guess: '',
        forceEnd: question ? false : true
      })
    }).catch((error) => {
      alert('Unable to load categories. Please try your request again')
      return;
    })
  }

  submitGuess = (event) => {
    event.preventDefault();
    this.state.guess.replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g,"").toLowerCase()
    let evaluate =   this.evaluateAnswer()
    this.setState({
      numCorrect: !evaluate ? this.state.numCorrect : this.state.numCorrect + 1,
      showAnswer: true
    })
  }

  restartGame = () => {
    this.setState({
      quizCategory: null,
      previousQuestions: [],
      showAnswer: false,
      numCorrect: 0,
      currentQuestion: null,
      guess: '',
      forceEnd: false
    })
  }


  renderPrePlay = () => (
          <div className="quiz-play-holder">
              <div className="choose-header">Choose Category</div>
              <div className="category-holder">
                  <div className="play-category" onClick={() => this.selectCategory({type:'all'})}>ALL</div>
                  {this.state.categories.map(({id, type}) => {
                  return (
                    <div
                      key={id}
                      value={id}
                      className="play-category"
                      onClick={() => this.selectCategory({type:type, id})}>
                      {type}
                    </div>
                  )
                })}
              </div>
          </div>
  )

  renderFinalScore = () => (
      <div className="quiz-play-holder">
        <div className="final-header"> Your Final Score is {this.state.numCorrect}</div>
        <div className="play-again button" onClick={ this.restartGame}> Play Again? </div>
      </div>
    )

  evaluateAnswer = () => {
    const formatGuess = this.state.guess.replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g,"").toLowerCase()
    return formatGuess === this.state.currentQuestion.answer.toLowerCase();
  }

  renderCorrectAnswer = () => {
    this.state.guess.replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g,"").toLowerCase()
    let evaluate =   this.evaluateAnswer()
    return(
      <div className="quiz-play-holder">
        <div className="quiz-question">{this.state.currentQuestion.question}</div>
        <div className={`${evaluate ? 'correct' : 'wrong'}`}>{evaluate ? "You were correct!" : "You were incorrect"}</div>
        <div className="quiz-answer">{this.state.currentQuestion.answer}</div>
        <div className="next-question button" onClick={this.getNextQuestion}> Next Question </div>
      </div>
    )
  }

  renderPlay = () => {
    return this.state.previousQuestions.length === questionsPerPlay || this.state.forceEnd
      ?  this.renderFinalScore()
      : this.state.showAnswer 
        ?  this.renderCorrectAnswer()
        : (
          <div className="quiz-play-holder">
            <div className="quiz-question">{this.state.currentQuestion && this.state.currentQuestion.question}</div>
            <form onSubmit={ this.submitGuess}>
              <input type="text" name="guess" className="form-input" onChange={this.handleChange}/>
              <input className="submit-guess button" type="submit" value="Submit Answer" />
            </form>
          </div>
        )
  };

  render(){
    return (
      <>
        {this.state.quizCategory ? this.renderPlay() : this.renderPrePlay()}
      </>
    )
  }
}

export default QuizView;
