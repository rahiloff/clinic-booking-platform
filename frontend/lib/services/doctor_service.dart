import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/api_client.dart';
import '../models/doctor.dart';
import '../models/slot.dart';

final doctorServiceProvider = Provider<DoctorService>((ref) {
  final dio = ref.watch(apiClientProvider);
  return DoctorService(dio);
});

class DoctorService {
  final Dio _dio;

  DoctorService(this._dio);

  Future<List<Doctor>> getDoctors({int skip = 0, int limit = 50}) async {
    final response = await _dio.get('/doctors/', queryParameters: {
      'skip': skip,
      'limit': limit,
    });
    
    if (response.data['success'] == true) {
      final List data = response.data['data'];
      return data.map((e) => Doctor.fromJson(e)).toList();
    }
    throw Exception(response.data['message']);
  }

  Future<Doctor> getDoctorById(String id) async {
    final response = await _dio.get('/doctors/$id');
    if (response.data['success'] == true) {
      return Doctor.fromJson(response.data['data']);
    }
    throw Exception(response.data['message']);
  }

  Future<List<Slot>> getDoctorSlots(String doctorId, String date) async {
    final response = await _dio.get('/doctors/$doctorId/slots', queryParameters: {
      'date': date,
    });
    
    if (response.data['success'] == true) {
      final List data = response.data['data'];
      return data.map((e) => Slot.fromJson(e)).toList();
    }
    throw Exception(response.data['message']);
  }
}
