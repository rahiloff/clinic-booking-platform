import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/api_client.dart';
import '../models/appointment.dart';

final appointmentServiceProvider = Provider<AppointmentService>((ref) {
  final dio = ref.watch(apiClientProvider);
  return AppointmentService(dio);
});

class AppointmentService {
  final Dio _dio;

  AppointmentService(this._dio);

  Future<List<Appointment>> getMyAppointments({int skip = 0, int limit = 50}) async {
    final response = await _dio.get('/appointments/', queryParameters: {
      'skip': skip,
      'limit': limit,
    });
    
    if (response.data['success'] == true) {
      final List data = response.data['data'];
      return data.map((e) => Appointment.fromJson(e)).toList();
    }
    throw Exception(response.data['message']);
  }

  Future<String> bookAppointment(String slotId, {String? reason}) async {
    try {
      final response = await _dio.post('/appointments/', data: {
        'slot_id': slotId,
        'reason': reason,
      });
      
      if (response.data['success'] == true) {
        return response.data['data']['appointment_id'];
      }
      throw Exception(response.data['message']);
    } on DioException catch (e) {
      // Specifically handle SlotConflictError (409) passed from backend
      if (e.response?.statusCode == 409) {
        throw Exception("This slot was just booked by someone else. Please select another slot.");
      }
      throw Exception(e.response?.data['message'] ?? e.message);
    }
  }

  Future<void> cancelAppointment(String appointmentId, String reason) async {
    final response = await _dio.patch('/appointments/$appointmentId/cancel', data: {
      'cancellation_reason': reason,
    });
    
    if (response.data['success'] != true) {
      throw Exception(response.data['message']);
    }
  }
}
