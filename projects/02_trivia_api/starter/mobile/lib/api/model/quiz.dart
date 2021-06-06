import 'package:equatable/equatable.dart';

class Question extends Equatable {
  final id;
  final String question;
  final String answer;
  final int category;
  final int difficulty;

  Question(this.id, this.question, this.answer, this.category, this.difficulty);

  @override
  List<Object> get props => [id, question, answer, category, difficulty];

  static Question fromJson(dynamic json) {
    return Question(json['id'], json['question'], json['answer'],
        json['category'], json['difficulty']);
  }

  @override
  String toString() => 'Quiz { id: $id }';
}
