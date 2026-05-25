import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/api_client.dart';
import '../models/schedule.dart';
import '../models/appointment.dart';

final dashboardServiceProvider = Provider<DashboardService>((ref) {
  final dio = ref.watch(apiClientProvider);
  return DashboardService(dio);
});

class DashboardService {
  final Dio _dio;

  DashboardService(this._dio);

  Future<List<Appointment>> getClinicAppointments({int skip = 0, int limit = 50}) async {
    final response = await _dio.get('/doctor/appointments', queryParameters: {
      'skip': skip,
      'limit': limit,
    });
    
    if (response.data['success'] == true) {
      final List data = response.data['data'];
      return data.map((e) => Appointment.fromJson(e)).toList();
    }
    throw Exception(response.data['message']);
  }

  Future<List<Schedule>> getSchedules() async {
    final response = await _dio.get('/doctor/schedules');
    if (response.data['success'] == true) {
      final List data = response.data['data'];
      return data.map((e) => Schedule.fromJson(e)).toList();
    }
    throw Exception(response.data['message']);
  }

  Future<Schedule> createSchedule({
    required int dayOfWeek,
    required String startTime,
    required String endTime,
    required int slotDuration,
  }) async {
    try {
      final response = await _dio.post('/doctor/schedules', data: {
        'day_of_week': dayOfWeek,
        'start_time': startTime,
        'end_time': endTime,
        'slot_duration': slotDuration,
      });
      
      if (response.data['success'] == true) {
        return Schedule.fromJson(response.data['data']);
      }
      throw Exception(response.data['message']);
    } on DioException catch (e) {
      throw Exception(e.response?.data['message'] ?? e.message);
    }
  }

  Future<void> deleteSchedule(String scheduleId) async {
    try {
      final response = await _dio.delete('/doctor/schedules/$scheduleId');
      if (response.data['success'] != true) {
        throw Exception(response.data['message']);
      }
    } on DioException catch (e) {
      throw Exception(e.response?.data['message'] ?? e.message);
    }
  }

  Future<String> generateSlots(int weeks) async {
    try {
      final response = await _dio.post('/doctor/generate-slots', queryParameters: {
        'weeks': weeks,
      });
      if (response.data['success'] == true) {
        return response.data['message'] ?? 'Slots generated successfully';
      }
      throw Exception(response.data['message']);
    } on DioException catch (e) {
      throw Exception(e.response?.data['message'] ?? e.message);
    }
  }
}
