import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'app.dart';
import 'providers/auth_provider.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Load environment variables gracefully
  try {
    await dotenv.load(fileName: ".env");
  } catch (e) {
    debugPrint("Could not load .env file: $e");
  }
  
  // Initialize Firebase gracefully for Web
  try {
    await Firebase.initializeApp();
  } catch (e) {
    debugPrint("Firebase init failed (missing web config): $e");
  }
  
  // Initialize SharedPreferences globally
  final prefs = await SharedPreferences.getInstance();

  runApp(
    ProviderScope(
      overrides: [
        sharedPreferencesProvider.overrideWithValue(prefs),
      ],
      child: const DocBookApp(),
    ),
  );
}
