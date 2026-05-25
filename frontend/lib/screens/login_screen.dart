import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/auth_provider.dart';
import '../services/auth_service.dart';
import '../widgets/common/app_button.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _phoneController = TextEditingController();
  final _otpController = TextEditingController();
  bool _isOtpSent = false;
  bool _isLoading = false;

  void _requestOtp() async {
    if (_phoneController.text.length < 10) return;
    setState(() => _isLoading = true);
    
    // Simulate Firebase OTP trigger
    await Future.delayed(const Duration(seconds: 1));
    
    if (mounted) {
      setState(() {
        _isLoading = false;
        _isOtpSent = true;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Test OTP Sent. Enter anything to login.')),
      );
    }
  }

  void _verifyOtpAndLogin() async {
    setState(() => _isLoading = true);
    
    try {
      // In production, this verifies with Firebase, gets the Firebase JWT,
      // and passes it to our backend. For MVP demo purposes:
      final authService = ref.read(authServiceProvider);
      // We send a mock token to the backend that should be handled by our mock auth flow
      final tokenData = await authService.loginWithFirebaseToken('mock_firebase_token');
      
      final accessToken = tokenData['access_token'];
      // The backend should return the role. We'll default to patient if missing.
      final role = tokenData['role'] ?? 'patient';
      
      await ref.read(authProvider.notifier).login(accessToken, role);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.toString()), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: theme.colorScheme.surface,
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Icon(Icons.local_hospital, size: 64, color: theme.colorScheme.primary),
                const SizedBox(height: 24),
                Text(
                  'Welcome to DocBook',
                  style: theme.textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 8),
                Text(
                  'Sign in to book and manage your appointments securely.',
                  style: theme.textTheme.bodyLarge?.copyWith(color: theme.colorScheme.onSurfaceVariant),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 48),
                
                TextField(
                  controller: _phoneController,
                  enabled: !_isOtpSent,
                  decoration: const InputDecoration(
                    labelText: 'Phone Number',
                    prefixIcon: Icon(Icons.phone),
                    hintText: '+1 234 567 8900',
                  ),
                  keyboardType: TextInputType.phone,
                ),
                const SizedBox(height: 16),
                
                if (_isOtpSent) ...[
                  TextField(
                    controller: _otpController,
                    decoration: const InputDecoration(
                      labelText: 'One-Time Password',
                      prefixIcon: Icon(Icons.lock_outline),
                    ),
                    keyboardType: TextInputType.number,
                  ),
                  const SizedBox(height: 24),
                  AppButton(
                    label: 'Verify & Login',
                    isLoading: _isLoading,
                    onPressed: _verifyOtpAndLogin,
                  ),
                  const SizedBox(height: 16),
                  TextButton(
                    onPressed: () => setState(() => _isOtpSent = false),
                    child: const Text('Use a different phone number'),
                  )
                ] else ...[
                  const SizedBox(height: 8),
                  AppButton(
                    label: 'Send OTP',
                    isLoading: _isLoading,
                    onPressed: _requestOtp,
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}
