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
      date: '2026-05-30',
      startTime: '09:00:00',
      endTime: '09:30:00',
      status: 'confirmed',
      doctor: Doctor(
        id: 'doc1',
        userId: 'user1',
        specialization: 'Cardiologist',
        bio: 'Expert in heart diseases.',
        consultationFee: 15000,
        experienceYears: 10,
        isAvailable: true,
        user: User(id: 'user1', phone: '1234567890', fullName: 'Dr. Gregory House', role: 'doctor'),
      ),
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
