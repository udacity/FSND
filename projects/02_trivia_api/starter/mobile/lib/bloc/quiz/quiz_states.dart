import 'package:equatable/equatable.dart';
import 'package:mobile/api/model/quiz.dart';

abstract class QuizState extends Equatable {
  const QuizState();

  @override
  List<Object> get props => [];
}

class QuizEmpty extends QuizState {}

class QuizLoading extends QuizState {}

class QuizLoaded extends QuizState {
  final Question question;

  const QuizLoaded(this.question);

  @override
  List<Object> get props => [question];
}

class QuizAnwserState extends QuizState {
  final Question question;
  final bool isCorrect;
  final String answer;
  const QuizAnwserState(this.question, this.isCorrect, this.answer);

  @override
  List<Object> get props => [isCorrect, answer];
}

class QuizError extends QuizState {}

class QuizDone extends QuizState {
  final int score;
  QuizDone(this.score);

  @override
  List<Object> get props => [score];
}
