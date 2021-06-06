import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:mobile/api/model/category.dart';
import 'package:mobile/environment.dart';

class CategoryApiClient {
  Future<List<Category>> fetchCategories() async {
    var url = apiBaseUrl + '/categories';
    final response = await http.get(Uri.parse(url));

    if (response.statusCode == 200) {
      var body = jsonDecode(response.body);
      List<Category> result = [];
      for (var item in body['data']) {
        result.add(Category.fromJson(item));
      }
      return result;
    }
    throw Exception('Failed to load album');
  }
}
