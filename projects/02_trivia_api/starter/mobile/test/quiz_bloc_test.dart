import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/api/client/quiz_client.dart';
import 'package:mobile/api/model/category.dart';
import 'package:mobile/api/model/quiz.dart';
import 'package:mobile/bloc/cat/cat_states.dart';
import 'package:mobile/bloc/quiz/quiz_bloc.dart';
import 'package:mobile/bloc/quiz/quiz_events.dart';
import 'package:mobile/bloc/quiz/quiz_states.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';

import 'quiz_bloc_test.mocks.dart';

@GenerateMocks([QuizApiClient])
void main() {
  group('Quiz bloc', () {
    blocTest<QuizBloc, QuizState>(
      'test next question',
      build: () {
        final client = MockQuizApiClient();
        final cat = Category(0, "type");
        final bloc = QuizBloc(client, cat);
        final Question question = new Question(0, 'question', 'answer', 0, 0);
        when(client.nextQuestion([], 0)).thenAnswer((_) async => question);
        return bloc;
      },
      act: (bloc) => bloc.add(NextQuestion()),
      expect: () => [
        QuizLoading(),
        QuizLoaded(new Question(0, 'question', 'answer', 0, 0))
      ],
    );
    blocTest<QuizBloc, QuizState>(
      'test next question with exception',
      build: () {
        final client = MockQuizApiClient();
        final cat = Category(0, "type");
        final bloc = QuizBloc(client, cat);
        when(client.nextQuestion([], 0)).thenThrow(Exception());
        return bloc;
      },
      act: (bloc) => bloc.add(NextQuestion()),
      expect: () => [QuizLoading(), QuizError()],
    );
    blocTest<QuizBloc, QuizState>(
      'test quiz done',
      build: () {
        final client = MockQuizApiClient();
        final cat = Category(0, "type");
        final bloc = QuizBloc(client, cat);
        when(client.nextQuestion([], 0))
            .thenThrow(QuizNotContentException(402));
        return bloc;
      },
      act: (bloc) => bloc.add(NextQuestion()),
      expect: () => [QuizLoading(), QuizDone(0)],
    );
    blocTest<QuizBloc, QuizState>(
      'test  wrong answer',
      build: () {
        final client = MockQuizApiClient();
        final cat = Category(0, "type");
        final bloc = QuizBloc(client, cat);
        bloc.currentQuestion = Question(0, 'question', 'answer', 0, 0);
        return bloc;
      },
      act: (bloc) => bloc.add(QuizAnswerEvent("a")),
      expect: () => [
        QuizAnwserState(Question(0, 'question', 'answer', 0, 0), false, 'a')
      ],
    );
    blocTest<QuizBloc, QuizState>(
      'test  correct answer',
      build: () {
        final client = MockQuizApiClient();
        final cat = Category(0, "type");
        final bloc = QuizBloc(client, cat);
        bloc.currentQuestion = Question(0, 'question', 'answer', 0, 0);
        return bloc;
      },
      act: (bloc) => bloc.add(QuizAnswerEvent("answer")),
      expect: () => [
        QuizAnwserState(Question(0, 'question', 'answer', 0, 0), true, 'answer')
      ],
    );
  });
}
