import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:mobile/api/client/quiz_client.dart';
import 'package:mobile/api/model/category.dart';
import 'package:mobile/bloc/quiz/quiz_bloc.dart';
import 'package:mobile/bloc/quiz/quiz_events.dart';
import 'package:mobile/bloc/quiz/quiz_states.dart';

class QuizPage extends StatelessWidget {
  final Category category;

  QuizPage(this.category);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Quiz'),
      ),
      body: BlocProvider(
        create: (context) => QuizBloc(QuizApiClient(), this.category),
        child: QuizWidget(),
      ),
    );
  }
}

class QuizWidget extends StatelessWidget {
  final answerTextController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<QuizBloc, QuizState>(
      builder: (context, state) {
        if (state is QuizEmpty) {
          BlocProvider.of<QuizBloc>(context).add(NextQuestion());
        }
        if (state is QuizError) {
          print(state);
          return Center(child: CircularProgressIndicator());
        }
        if (state is QuizLoaded) {
          return Padding(
              padding: const EdgeInsets.all(16.0),
              child: Center(
                child: Column(
                  children: [
                    Text(state.question.question),
                    TextField(
                      autofocus: true,
                      controller: answerTextController,
                    ),
                    TextButton(
                      style: ButtonStyle(
                        foregroundColor:
                            MaterialStateProperty.all<Color>(Colors.blue),
                      ),
                      onPressed: () {
                        BlocProvider.of<QuizBloc>(context)
                            .add(QuizAnswerEvent(answerTextController.text));
                        this.answerTextController.text = "";
                      },
                      child: Text('Submit Answer'),
                    )
                  ],
                ),
              ));
        } else if (state is QuizAnwserState) {
          return Padding(
              padding: const EdgeInsets.all(16.0),
              child: Center(
                child: Column(
                  children: [
                    Text(state.question.question),
                    Text(
                        state.isCorrect
                            ? "You were correct!"
                            : "You were incorrect",
                        style: TextStyle(
                            color:
                                state.isCorrect ? Colors.green : Colors.red)),
                    Text(state.question.answer,
                        style: TextStyle(fontStyle: FontStyle.italic)),
                    TextButton(
                      style: ButtonStyle(
                        foregroundColor:
                            MaterialStateProperty.all<Color>(Colors.blue),
                      ),
                      onPressed: () {
                        BlocProvider.of<QuizBloc>(context).add(NextQuestion());
                      },
                      child: Text('Next question'),
                    )
                  ],
                ),
              ));
        }
        if (state is QuizDone) {
          final score = state.score;
          return Padding(
              padding: const EdgeInsets.all(16.0),
              child: Center(
                child: Column(
                  children: [
                    Text("Your Final Score is $score"),
                    TextButton(
                      style: ButtonStyle(
                        foregroundColor:
                            MaterialStateProperty.all<Color>(Colors.blue),
                      ),
                      onPressed: () {
                        Navigator.pop(context);
                      },
                      child: Text('OK'),
                    )
                  ],
                ),
              ));
        }
        return Center(
          child: CircularProgressIndicator(),
        );
      },
    );
  }
}
