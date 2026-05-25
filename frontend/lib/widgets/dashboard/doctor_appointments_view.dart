import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../providers/dashboard_provider.dart';
import '../appointment/appointment_card.dart';
import '../common/loading_view.dart';
import '../common/error_view.dart';

class DoctorAppointmentsView extends ConsumerWidget {
  const DoctorAppointmentsView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appointmentsAsync = ref.watch(dashboardAppointmentsProvider);

    return RefreshIndicator(
      onRefresh: () async => ref.refresh(dashboardAppointmentsProvider.future),
      child: appointmentsAsync.when(
        loading: () => const LoadingView(message: 'Loading clinic schedule...'),
        error: (e, st) => ErrorView(message: e.toString(), onRetry: () => ref.refresh(dashboardAppointmentsProvider)),
        data: (appointments) {
          if (appointments.isEmpty) {
            return const ErrorView(message: 'No appointments found for your clinic.');
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16.0),
            itemCount: appointments.length,
            itemBuilder: (context, index) {
              final appt = appointments[index];
              return AppointmentCard(
                appointment: appt,
                // Dashboard side doesn't implement patient cancellation directly inside the card natively, 
                // but could be expanded if a doctor needs to forcibly cancel.
              );
            },
          );
        },
      ),
    );
  }
}
