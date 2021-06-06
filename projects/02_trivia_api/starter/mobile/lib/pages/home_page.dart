import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:mobile/bloc/cat/cat_bloc.dart';
import 'package:mobile/bloc/cat/cat_events.dart';
import 'package:mobile/bloc/cat/cat_states.dart';
import 'package:mobile/pages/quizzes_page.dart';

class HomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return BlocBuilder<CategoryBloc, CategoryState>(
      builder: (context, state) {
        if (state is CategoryEmpty) {
          BlocProvider.of<CategoryBloc>(context).add(FetchCategory());
        }
        if (state is CategoryError) {
          return CircularProgressIndicator();
        }
        if (state is CategoryLoaded) {
          return ListView.builder(
            itemCount: state.categories.length,
            itemBuilder: (context, index) {
              final item = state.categories[index];

              return ListTile(
                title: Text(item.type),
                onTap: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(builder: (context) => QuizPage(item)),
                  );
                },
              );
            },
          );
        }
        return Center(
          child: CircularProgressIndicator(),
        );
      },
    );
  }
}
