import 'package:equatable/equatable.dart';

abstract class CategoryEvent extends Equatable {
  const CategoryEvent();
}

class FetchCategory extends CategoryEvent {
  const FetchCategory();

  @override
  List<Object> get props => [];
}
