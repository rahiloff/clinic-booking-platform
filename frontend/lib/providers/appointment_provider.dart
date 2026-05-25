import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/appointment_service.dart';
import '../models/appointment.dart';

import '../models/doctor.dart';
import '../models/user.dart';

// Provides a reactive list of the patient's appointments
final myAppointmentsProvider = FutureProvider.autoDispose<List<Appointment>>((ref) async {
  // MOCK APPOINTMENTS FOR UI TESTING
  return [
    Appointment(
      id: 'app1',
      patientId: 'patient1',
      doctorId: 'doc1',
      slotId: 'slot1',
      slotDate: '2026-05-30',
      slotTime: '09:00:00',
      status: 'confirmed',
      doctorName: 'Dr. Gregory House',
      patientName: 'John Doe',
    ),
  ];
});

// StateNotifier for imperative booking actions (handling loading state during POST)
class BookingNotifier extends StateNotifier<AsyncValue<void>> {
  final AppointmentService _service;
  final Ref _ref;

  BookingNotifier(this._service, this._ref) : super(const AsyncData(null));

  Future<bool> bookSlot(String slotId, {String? reason}) async {
    state = const AsyncLoading();
    try {
      // MOCK BOOKING FOR UI TESTING
      await Future.delayed(const Duration(seconds: 1));
      state = const AsyncData(null);
      _ref.invalidate(myAppointmentsProvider);
      return true;
    } catch (e, st) {
      state = AsyncError(e, st);
      return false;
    }
  }

  Future<bool> cancelAppointment(String appointmentId, String reason) async {
    state = const AsyncLoading();
    try {
      await _service.cancelAppointment(appointmentId, reason);
      state = const AsyncData(null);
      _ref.invalidate(myAppointmentsProvider);
      return true;
    } catch (e, st) {
      state = AsyncError(e, st);
      return false;
    }
  }
}

final bookingProvider = StateNotifierProvider<BookingNotifier, AsyncValue<void>>((ref) {
  final service = ref.watch(appointmentServiceProvider);
  return BookingNotifier(service, ref);
});
