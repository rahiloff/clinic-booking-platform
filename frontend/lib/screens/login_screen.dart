import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:firebase_auth/firebase_auth.dart';
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
  String _verificationId = '';

  void _requestOtp() async {
    final phone = _phoneController.text.trim();
    if (phone.length < 10) return;
    
    // Developer testing backdoor to bypass Firebase completely
    if (phone == '0000000000' || phone == '+10000000000') {
      setState(() => _isLoading = true);
      try {
        final authService = ref.read(authServiceProvider);
        final tokenData = await authService.loginWithFirebaseToken('test_token');
        await ref.read(authProvider.notifier).login(tokenData['access_token'], tokenData['role'] ?? 'patient');
      } catch (e) {
        if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString()), backgroundColor: Colors.red));
      } finally {
        if (mounted) setState(() => _isLoading = false);
      }
      return;
    }
    
    setState(() => _isLoading = true);
    
    try {
      await FirebaseAuth.instance.verifyPhoneNumber(
        phoneNumber: phone,
        verificationCompleted: (PhoneAuthCredential credential) async {
          // Auto-resolution on Android devices
          await _signInWithCredential(credential);
        },
        verificationFailed: (FirebaseAuthException e) {
          setState(() => _isLoading = false);
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message ?? 'Verification failed'), backgroundColor: Colors.red));
        },
        codeSent: (String verificationId, int? resendToken) {
          if (mounted) {
            setState(() {
              _verificationId = verificationId;
              _isOtpSent = true;
              _isLoading = false;
            });
            ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('OTP SMS Sent!')));
          }
        },
        codeAutoRetrievalTimeout: (String verificationId) {
          _verificationId = verificationId;
        },
      );
    } catch (e) {
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString()), backgroundColor: Colors.red));
    }
  }

  void _verifyOtpAndLogin() async {
    final smsCode = _otpController.text.trim();
    if (smsCode.length < 6) return;

    setState(() => _isLoading = true);
    try {
      final credential = PhoneAuthProvider.credential(
        verificationId: _verificationId,
        smsCode: smsCode,
      );
      await _signInWithCredential(credential);
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Invalid OTP Code'), backgroundColor: Colors.red));
      }
    }
  }

  Future<void> _signInWithCredential(PhoneAuthCredential credential) async {
    try {
      final userCredential = await FirebaseAuth.instance.signInWithCredential(credential);
      final idToken = await userCredential.user?.getIdToken();
      
      if (idToken == null) throw Exception("Failed to retrieve Firebase ID Token");

      // Exchange Firebase Token for Backend JWT
      final authService = ref.read(authServiceProvider);
      final tokenData = await authService.loginWithFirebaseToken(idToken);
      
      final accessToken = tokenData['access_token'];
      final role = tokenData['role'] ?? 'patient';
      
      await ref.read(authProvider.notifier).login(accessToken, role);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString()), backgroundColor: Colors.red));
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
