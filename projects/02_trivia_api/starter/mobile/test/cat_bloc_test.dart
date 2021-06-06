import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/api/client/category_client.dart';
import 'package:mobile/api/model/category.dart';
import 'package:mobile/bloc/cat/cat_bloc.dart';
import 'package:mobile/bloc/cat/cat_events.dart';
import 'package:mobile/bloc/cat/cat_states.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';

import 'cat_bloc_test.mocks.dart';

@GenerateMocks([CategoryApiClient])
void main() {
  group('Caegory bloc', () {
    blocTest<CategoryBloc, CategoryState>(
      'test fetch category event',
      build: () {
        final client = MockCategoryApiClient();
        final bloc = CategoryBloc(client);
        final List<Category> categories = [new Category(1, "type")];
        when(client.fetchCategories()).thenAnswer((_) async => categories);
        return bloc;
      },
      act: (bloc) => bloc.add(FetchCategory()),
      expect: () => [
        CategoryLoading(),
        CategoryLoaded([new Category(0, "ALL"), new Category(1, "type")])
      ],
    );
    blocTest<CategoryBloc, CategoryState>(
      'test fetch category with exception in fetch',
      build: () {
        final client = MockCategoryApiClient();
        final bloc = CategoryBloc(client);
        when(client.fetchCategories()).thenThrow(Exception());
        return bloc;
      },
      act: (bloc) => bloc.add(FetchCategory()),
      expect: () => [CategoryLoading(), CategoryError()],
    );
  });
}
