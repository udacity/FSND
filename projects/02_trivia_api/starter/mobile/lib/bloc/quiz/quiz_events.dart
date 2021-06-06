import 'package:equatable/equatable.dart';

abstract class QuizEvent extends Equatable {
  const QuizEvent();
}

class NextQuestion extends QuizEvent {
  const NextQuestion();

  @override
  List<Object> get props => [];
}

class QuizAnswerEvent extends QuizEvent {
  final String answer;
  const QuizAnswerEvent(this.answer);

  @override
  List<Object> get props => [answer];
}
