import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

// Provides synchronous access to SharedPreferences across the app.
// It is overridden in main.dart after SharedPreferences.getInstance() is awaited.
final sharedPreferencesProvider = Provider<SharedPreferences>((ref) {
  throw UnimplementedError('sharedPreferencesProvider must be overridden in main.dart');
});

class AuthState {
  final bool isAuthenticated;
  final String? token;
  final String? role;

  AuthState({this.isAuthenticated = false, this.token, this.role});

  AuthState copyWith({bool? isAuthenticated, String? token, String? role}) {
    return AuthState(
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      token: token ?? this.token,
      role: role ?? this.role,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final SharedPreferences _prefs;

  AuthNotifier(this._prefs) : super(AuthState()) {
    _loadSession();
  }

  static const _tokenKey = 'jwt_token';
  static const _roleKey = 'user_role';

  void _loadSession() {
    final token = _prefs.getString(_tokenKey);
    final role = _prefs.getString(_roleKey);
    if (token != null && token.isNotEmpty) {
      state = AuthState(isAuthenticated: true, token: token, role: role);
    }
  }

  Future<void> login(String token, String role) async {
    await _prefs.setString(_tokenKey, token);
    await _prefs.setString(_roleKey, role);
    state = AuthState(isAuthenticated: true, token: token, role: role);
  }

  Future<void> logout() async {
    await _prefs.remove(_tokenKey);
    await _prefs.remove(_roleKey);
    state = AuthState(isAuthenticated: false);
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final prefs = ref.watch(sharedPreferencesProvider);
  return AuthNotifier(prefs);
});
