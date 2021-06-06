import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:mobile/api/client/quiz_client.dart';
import 'package:mobile/api/model/category.dart';
import 'package:mobile/api/model/quiz.dart';
import 'package:mobile/bloc/quiz/quiz_events.dart';
import 'package:mobile/bloc/quiz/quiz_states.dart';

class QuizBloc extends Bloc<QuizEvent, QuizState> {
  final QuizApiClient apiClient;

  final List<Question> quizDone = [];

  int score = 0;

  Category category;

  var currentQuestion;

  QuizBloc(this.apiClient, this.category) : super(QuizEmpty());

  @override
  Stream<QuizState> mapEventToState(QuizEvent event) async* {
    if (event is NextQuestion) {
      yield QuizLoading();
      try {
        final loaded = QuizLoaded(await apiClient.nextQuestion(
            this.quizDone.map<int>((e) => e.id).toList(), this.category.id));
        this.currentQuestion = loaded.question;
        yield loaded;
      } on QuizNotContentException {
        yield QuizDone(this.score);
      } catch (_) {
        yield QuizError();
      }
    } else if (event is QuizAnswerEvent) {
      this.quizDone.add(this.currentQuestion);
      final isCorrect = this.currentQuestion.answer == event.answer;
      if (isCorrect) {
        this.score += 1;
      }
      yield QuizAnwserState(this.currentQuestion, isCorrect, event.answer);
    }
  }
}
