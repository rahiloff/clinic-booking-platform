import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/doctor_service.dart';
import '../models/doctor.dart';
import '../models/slot.dart';

import '../models/user.dart';

// Provides a list of all doctors. Automatically caches and handles async states.
final doctorsProvider = FutureProvider.autoDispose<List<Doctor>>((ref) async {
  // MOCK DATA FOR UI TESTING
  return [
    Doctor(
      id: 'doc1',
      userId: 'user1',
      specialization: 'Cardiologist',
      bio: 'Expert in heart diseases.',
      consultationFee: 15000,
      experienceYears: 10,
      isAvailable: true,
      user: User(id: 'user1', phone: '1234567890', fullName: 'Dr. Gregory House', role: 'doctor'),
    ),
    Doctor(
      id: 'doc2',
      userId: 'user2',
      specialization: 'Neurologist',
      bio: 'Brain and nervous system specialist.',
      consultationFee: 20000,
      experienceYears: 15,
      isAvailable: true,
      user: User(id: 'user2', phone: '0987654321', fullName: 'Dr. Stephen Strange', role: 'doctor'),
    ),
  ];
});

// Provides a specific doctor's profile.
final doctorDetailProvider = FutureProvider.family.autoDispose<Doctor, String>((ref, id) async {
  final doctors = await ref.watch(doctorsProvider.future);
  return doctors.firstWhere((d) => d.id == id, orElse: () => doctors.first);
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
  // Return empty list for now
  return [];
});
