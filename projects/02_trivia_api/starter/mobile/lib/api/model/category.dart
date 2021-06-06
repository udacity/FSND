import 'package:equatable/equatable.dart';

class Category extends Equatable {
  final id;
  final String type;

  Category(this.id, this.type);

  @override
  List<Object> get props => [id, type];

  static Category fromJson(dynamic json) {
    return Category(json['id'], json['type']);
  }

  @override
  String toString() => 'Category { id: $id }';
}
