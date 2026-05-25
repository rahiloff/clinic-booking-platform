import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/doctor_service.dart';
import '../models/doctor.dart';
import '../models/slot.dart';

// Provides a list of all doctors. Automatically caches and handles async states.
final doctorsProvider = FutureProvider.autoDispose<List<Doctor>>((ref) async {
  final service = ref.watch(doctorServiceProvider);
  return service.getDoctors();
});

// Provides a specific doctor's profile.
final doctorDetailProvider = FutureProvider.family.autoDispose<Doctor, String>((ref, id) async {
  final service = ref.watch(doctorServiceProvider);
  return service.getDoctorById(id);
});

// A parameter class for the family provider since it needs both doctorId and date
class SlotQuery {
  final String doctorId;
  final String date;

  SlotQuery(this.doctorId, this.date);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is SlotQuery && doctorId == other.doctorId && date == other.date;

  @override
  int get hashCode => doctorId.hashCode ^ date.hashCode;
}

// Provides available slots for a specific doctor on a specific date
final doctorSlotsProvider = FutureProvider.family.autoDispose<List<Slot>, SlotQuery>((ref, query) async {
  final service = ref.watch(doctorServiceProvider);
  return service.getDoctorSlots(query.doctorId, query.date);
});
