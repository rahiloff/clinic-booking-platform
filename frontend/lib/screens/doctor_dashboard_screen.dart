import 'package:flutter/material.dart';
import '../widgets/dashboard/doctor_appointments_view.dart';
import '../widgets/dashboard/doctor_schedule_management_view.dart';

class DoctorDashboardScreen extends StatefulWidget {
  const DoctorDashboardScreen({super.key});

  @override
  State<DoctorDashboardScreen> createState() => _DoctorDashboardScreenState();
}

class _DoctorDashboardScreenState extends State<DoctorDashboardScreen> {
  int _currentIndex = 0;

  final _views = [
    const DoctorAppointmentsView(),
    const DoctorScheduleManagementView(),
  ];

  @override
  Widget build(BuildContext context) {
    // For wider screens, we could use a Row with NavigationRail.
    // For MVP, BottomNavigationBar handles mobile/tablets well.
    return Scaffold(
      appBar: AppBar(
        title: const Text('Doctor Dashboard'),
      ),
      body: IndexedStack(
        index: _currentIndex,
        children: _views,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.people_outline),
            activeIcon: Icon(Icons.people),
            label: 'Appointments',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.calendar_month_outlined),
            activeIcon: Icon(Icons.calendar_month),
            label: 'Schedules',
          ),
        ],
      ),
    );
  }
}
