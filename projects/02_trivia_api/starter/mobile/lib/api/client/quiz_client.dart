import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:mobile/api/model/quiz.dart';
import 'package:mobile/environment.dart';

class QuizNotContentException implements Exception {
  final int code;
  QuizNotContentException(this.code);
}

class QuizApiClient {
  Future<Question> nextQuestion(List<int> ids, int catId) async {
    var url = apiBaseUrl + '/quizzes';
    final response = await http.post(Uri.parse(url),
        headers: <String, String>{'Content-Type': 'application/json '},
        body: jsonEncode(<String, dynamic>{
          'previous_questions': ids,
          'quiz_category': catId.toString()
        }));

    if (response.statusCode == 200) {
      var body = jsonDecode(response.body);
      return Question.fromJson(body);
    }
    if (response.statusCode == 204) {
      throw QuizNotContentException(response.statusCode);
    }
    throw Exception('Failed to load album');
  }
}
