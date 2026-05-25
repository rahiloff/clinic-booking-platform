class Schedule {
  final String id;
  final String doctorId;
  final int dayOfWeek;
  final String startTime;
  final String endTime;
  final int slotDuration;

  Schedule({
    required this.id,
    required this.doctorId,
    required this.dayOfWeek,
    required this.startTime,
    required this.endTime,
    required this.slotDuration,
  });

  factory Schedule.fromJson(Map<String, dynamic> json) {
    return Schedule(
      id: json['id'] as String,
      doctorId: json['doctor_id'] as String,
      dayOfWeek: json['day_of_week'] as int,
      startTime: json['start_time'] as String,
      endTime: json['end_time'] as String,
      slotDuration: json['slot_duration'] as int,
    );
  }

  String get dayName {
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    if (dayOfWeek >= 0 && dayOfWeek < 7) {
      return days[dayOfWeek];
    }
    return 'Unknown';
  }
}
