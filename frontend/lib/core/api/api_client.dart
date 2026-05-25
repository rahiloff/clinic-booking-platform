import 'package:dio/dio.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/auth_provider.dart';

final apiClientProvider = Provider<Dio>((ref) {
  final authState = ref.watch(authProvider);
  
  final baseUrl = dotenv.env['API_BASE_URL'] ?? 'http://localhost:8000/api/v1';
  
  final dio = Dio(
    BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ),
  );

  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (options, handler) {
        if (authState.isAuthenticated && authState.token != null) {
          options.headers['Authorization'] = 'Bearer ${authState.token}';
        }
        return handler.next(options);
      },
      onError: (DioException e, handler) async {
        // Automatically logout on 401
        if (e.response?.statusCode == 401) {
          await ref.read(authProvider.notifier).logout();
        }
        return handler.next(e);
      },
    ),
  );

  return dio;
});
