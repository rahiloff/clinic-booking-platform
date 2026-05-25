import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/dashboard_service.dart';
import '../models/schedule.dart';
import '../models/appointment.dart';

// Provides reactive clinic appointments list
final dashboardAppointmentsProvider = FutureProvider.autoDispose<List<Appointment>>((ref) async {
  final service = ref.watch(dashboardServiceProvider);
  return service.getClinicAppointments();
});

// Provides reactive schedules list
final doctorSchedulesProvider = FutureProvider.autoDispose<List<Schedule>>((ref) async {
  final service = ref.watch(dashboardServiceProvider);
  return service.getSchedules();
});

// StateNotifier for imperative dashboard actions
class DashboardActionsNotifier extends StateNotifier<AsyncValue<void>> {
  final DashboardService _service;
  final Ref _ref;

  DashboardActionsNotifier(this._service, this._ref) : super(const AsyncData(null));

  Future<bool> createSchedule(int dayOfWeek, String startTime, String endTime, int slotDuration) async {
    state = const AsyncLoading();
    try {
      await _service.createSchedule(
        dayOfWeek: dayOfWeek,
        startTime: startTime,
        endTime: endTime,
        slotDuration: slotDuration,
      );
      state = const AsyncData(null);
      _ref.invalidate(doctorSchedulesProvider);
      return true;
    } catch (e, st) {
      state = AsyncError(e, st);
      return false;
    }
  }

  Future<bool> deleteSchedule(String id) async {
    state = const AsyncLoading();
    try {
      await _service.deleteSchedule(id);
      state = const AsyncData(null);
      _ref.invalidate(doctorSchedulesProvider);
      return true;
    } catch (e, st) {
      state = AsyncError(e, st);
      return false;
    }
  }

  Future<bool> generateSlots(int weeks) async {
    state = const AsyncLoading();
    try {
      final msg = await _service.generateSlots(weeks);
      // We pass the success message back inside the data payload dynamically for the UI
      state = const AsyncData(null); 
      return true;
    } catch (e, st) {
      state = AsyncError(e, st);
      return false;
    }
  }
}

final dashboardActionsProvider = StateNotifierProvider<DashboardActionsNotifier, AsyncValue<void>>((ref) {
  final service = ref.watch(dashboardServiceProvider);
  return DashboardActionsNotifier(service, ref);
});
