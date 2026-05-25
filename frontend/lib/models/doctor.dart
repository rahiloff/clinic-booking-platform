import 'user.dart';

class Doctor {
  final String id;
  final String userId;
  final String specialization;
  final String? bio;
  final int consultationFee;
  final int experienceYears;
  final bool isAvailable;
  final User? user;

  Doctor({
    required this.id,
    required this.userId,
    required this.specialization,
    this.bio,
    required this.consultationFee,
    required this.experienceYears,
    required this.isAvailable,
    this.user,
  });

  factory Doctor.fromJson(Map<String, dynamic> json) {
    return Doctor(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      specialization: json['specialization'] as String,
      bio: json['bio'] as String?,
      consultationFee: json['consultation_fee'] as int,
      experienceYears: json['experience_years'] as int,
      isAvailable: json['is_available'] as bool,
      user: json['user'] != null ? User.fromJson(json['user']) : null,
    );
  }
}
