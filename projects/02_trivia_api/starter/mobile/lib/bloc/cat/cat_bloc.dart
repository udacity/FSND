import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:mobile/api/client/category_client.dart';
import 'package:mobile/api/model/category.dart';
import 'package:mobile/bloc/cat/cat_events.dart';
import 'package:mobile/bloc/cat/cat_states.dart';

class CategoryBloc extends Bloc<CategoryEvent, CategoryState> {
  final CategoryApiClient apiClient;

  CategoryBloc(this.apiClient) : super(CategoryEmpty());

  @override
  Stream<CategoryState> mapEventToState(CategoryEvent event) async* {
    if (event is FetchCategory) {
      yield CategoryLoading();
      try {
        final categories = await apiClient.fetchCategories();
        categories.insert(0, new Category(0, "ALL"));
        yield CategoryLoaded(categories);
      } catch (_) {
        yield CategoryError();
      }
    }
  }
}
