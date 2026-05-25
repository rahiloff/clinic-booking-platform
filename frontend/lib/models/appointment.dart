class Appointment {
  final String id;
  final String patientId;
  final String doctorId;
  final String slotId;
  final String status;
  final String? reason;
  
  // Joined fields for convenience
  final String? doctorName;
  final String? patientName;
  final String? slotDate;
  final String? slotTime;

  Appointment({
    required this.id,
    required this.patientId,
    required this.doctorId,
    required this.slotId,
    required this.status,
    this.reason,
    this.doctorName,
    this.patientName,
    this.slotDate,
    this.slotTime,
  });

  factory Appointment.fromJson(Map<String, dynamic> json) {
    return Appointment(
      id: json['id'] as String,
      patientId: json['patient_id'] as String,
      doctorId: json['doctor_id'] as String,
      slotId: json['slot_id'] as String,
      status: json['status'] as String,
      reason: json['reason'] as String?,
      doctorName: json['doctor_name'] as String?,
      patientName: json['patient_name'] as String?,
      slotDate: json['slot_date'] as String?,
      slotTime: json['slot_time'] as String?,
    );
  }
}
