import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/appointment_provider.dart';
import '../widgets/appointment/appointment_card.dart';
import '../widgets/common/loading_view.dart';
import '../widgets/common/error_view.dart';

class MyAppointmentsScreen extends ConsumerWidget {
  const MyAppointmentsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appointmentsAsync = ref.watch(myAppointmentsProvider);
    final bookingState = ref.watch(bookingProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Appointments'),
      ),
      body: RefreshIndicator(
        onRefresh: () async => ref.refresh(myAppointmentsProvider.future),
        child: appointmentsAsync.when(
          loading: () => const LoadingView(message: 'Loading appointments...'),
          error: (e, st) => ErrorView(message: e.toString(), onRetry: () => ref.refresh(myAppointmentsProvider)),
          data: (appointments) {
            if (appointments.isEmpty) {
              return const ErrorView(message: 'You have no appointments booked.');
            }
            
            return ListView.builder(
              padding: const EdgeInsets.all(16.0),
              itemCount: appointments.length,
              itemBuilder: (context, index) {
                final appt = appointments[index];
                return AppointmentCard(
                  appointment: appt,
                  isCancelling: bookingState.isLoading, // Simple global loading state for MVP
                  onCancel: () async {
                    final confirm = await showDialog<bool>(
                      context: context,
                      builder: (c) => AlertDialog(
                        title: const Text('Cancel Appointment'),
                        content: const Text('Are you sure you want to cancel this appointment?'),
                        actions: [
                          TextButton(onPressed: () => Navigator.pop(c, false), child: const Text('No')),
                          TextButton(onPressed: () => Navigator.pop(c, true), child: const Text('Yes, Cancel')),
                        ],
                      ),
                    );
                    
                    if (confirm == true) {
                      await ref.read(bookingProvider.notifier).cancelAppointment(appt.id, 'Patient cancelled');
                    }
                  },
                );
              },
            );
          },
        ),
      ),
    );
  }
}
