class Slot {
  final String id;
  final String doctorId;
  final String date;
  final String startTime;
  final String endTime;
  final String status;

  Slot({
    required this.id,
    required this.doctorId,
    required this.date,
    required this.startTime,
    required this.endTime,
    required this.status,
  });

  factory Slot.fromJson(Map<String, dynamic> json) {
    return Slot(
      id: json['id'] as String,
      doctorId: json['doctor_id'] as String,
      date: json['date'] as String,
      startTime: json['start_time'] as String,
      endTime: json['end_time'] as String,
      status: json['status'] as String,
    );
  }
}
