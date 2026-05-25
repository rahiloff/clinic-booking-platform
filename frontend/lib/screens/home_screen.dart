import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../providers/auth_provider.dart';
import '../providers/doctor_provider.dart';
import '../widgets/doctor/doctor_card.dart';
import '../widgets/common/loading_view.dart';
import '../widgets/common/error_view.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final doctorsAsync = ref.watch(doctorsProvider);
    final authState = ref.watch(authProvider);
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: theme.colorScheme.surface,
      appBar: AppBar(
        title: const Text('Find a Doctor', style: TextStyle(fontWeight: FontWeight.w600)),
        actions: [
          if (authState.role == 'doctor')
            IconButton(
              icon: const Icon(Icons.admin_panel_settings),
              tooltip: 'Doctor Dashboard',
              onPressed: () => context.push('/dashboard'),
            ),
          IconButton(
            icon: const Icon(Icons.calendar_today_outlined),
            tooltip: 'My Appointments',
            onPressed: () => context.push('/appointments'),
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Logout',
            onPressed: () => ref.read(authProvider.notifier).logout(),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async => ref.refresh(doctorsProvider.future),
        child: doctorsAsync.when(
          loading: () => const LoadingView(message: 'Loading doctors...'),
          error: (err, stack) => ErrorView(
            message: err.toString(),
            onRetry: () => ref.refresh(doctorsProvider),
          ),
          data: (doctors) {
            if (doctors.isEmpty) {
              return const ErrorView(message: 'No doctors found.');
            }
            return ListView.builder(
              padding: const EdgeInsets.all(16.0),
              itemCount: doctors.length,
              itemBuilder: (context, index) {
                final doc = doctors[index];
                return DoctorCard(
                  doctor: doc,
                  onTap: () => context.push('/doctor/${doc.id}', extra: doc),
                );
              },
            );
          },
        ),
      ),
    );
  }
}
