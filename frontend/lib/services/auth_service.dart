import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/api_client.dart';

final authServiceProvider = Provider<AuthService>((ref) {
  final dio = ref.watch(apiClientProvider);
  return AuthService(dio);
});

class AuthService {
  final Dio _dio;

  AuthService(this._dio);

  /// Authenticate using a Firebase ID token
  Future<Map<String, dynamic>> loginWithFirebaseToken(String firebaseToken) async {
    try {
      final response = await _dio.post('/auth/login', data: {
        'firebase_token': firebaseToken,
      });
      
      final data = response.data;
      if (data['success'] == true) {
        return data['data']; // Returns { "access_token": "...", "token_type": "bearer" }
      } else {
        throw Exception(data['message'] ?? 'Login failed');
      }
    } on DioException catch (e) {
      final errorMsg = e.response?.data['message'] ?? e.message;
      throw Exception(errorMsg);
    }
  }

  /// Get current user profile
  Future<Map<String, dynamic>> getCurrentUser() async {
    try {
      final response = await _dio.get('/auth/me');
      if (response.data['success'] == true) {
        return response.data['data']; // User JSON
      }
      throw Exception('Failed to fetch user');
    } catch (e) {
      throw Exception(e.toString());
    }
  }
}
