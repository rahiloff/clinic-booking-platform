import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../providers/dashboard_provider.dart';
import '../common/loading_view.dart';
import '../common/error_view.dart';
import '../common/app_button.dart';
import 'schedule_card.dart';

class DoctorScheduleManagementView extends ConsumerStatefulWidget {
  const DoctorScheduleManagementView({super.key});

  @override
  ConsumerState<DoctorScheduleManagementView> createState() => _DoctorScheduleManagementViewState();
}

class _DoctorScheduleManagementViewState extends ConsumerState<DoctorScheduleManagementView> {
  // Simple form state for MVP add schedule
  int _selectedDay = 0; // Monday
  TimeOfDay _startTime = const TimeOfDay(hour: 9, minute: 0);
  TimeOfDay _endTime = const TimeOfDay(hour: 17, minute: 0);
  int _slotDuration = 30;

  final _days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  void _addSchedule() async {
    final startStr = '${_startTime.hour.toString().padLeft(2, '0')}:${_startTime.minute.toString().padLeft(2, '0')}';
    final endStr = '${_endTime.hour.toString().padLeft(2, '0')}:${_endTime.minute.toString().padLeft(2, '0')}';

    final success = await ref.read(dashboardActionsProvider.notifier)
        .createSchedule(_selectedDay, startStr, endStr, _slotDuration);
    
    if (mounted && !success) {
      final err = ref.read(dashboardActionsProvider).error.toString();
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(err), backgroundColor: Colors.red));
    }
  }

  void _generateSlots() async {
    final success = await ref.read(dashboardActionsProvider.notifier).generateSlots(4);
    if (mounted) {
      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Generated successfully!'), backgroundColor: Colors.green));
      } else {
        final err = ref.read(dashboardActionsProvider).error.toString();
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(err), backgroundColor: Colors.red));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final schedulesAsync = ref.watch(doctorSchedulesProvider);
    final actionState = ref.watch(dashboardActionsProvider);

    return RefreshIndicator(
      onRefresh: () async => ref.refresh(doctorSchedulesProvider.future),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Generate Slots Action Card
            Card(
              color: Theme.of(context).colorScheme.primaryContainer,
              elevation: 0,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Slot Generation Engine', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
                    const SizedBox(height: 8),
                    Text(
                      'Trigger backend background workers to automatically build highly available slot blocks based on your schedules below.',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                    const SizedBox(height: 16),
                    AppButton(
                      label: 'Generate Next 4 Weeks',
                      isLoading: actionState.isLoading,
                      onPressed: _generateSlots,
                    )
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            
            Text('Active Schedules', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 16),

            schedulesAsync.when(
              loading: () => const LoadingView(),
              error: (e, st) => ErrorView(message: e.toString(), onRetry: () => ref.refresh(doctorSchedulesProvider)),
              data: (schedules) {
                if (schedules.isEmpty) return const Text('No schedules defined. Add one below.');
                return Column(
                  children: schedules.map((s) => ScheduleCard(
                    schedule: s,
                    isDeleting: actionState.isLoading,
                    onDelete: () => ref.read(dashboardActionsProvider.notifier).deleteSchedule(s.id),
                  )).toList(),
                );
              },
            ),
            
            const SizedBox(height: 32),
            const Divider(),
            const SizedBox(height: 16),
            Text('Add New Schedule', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 16),

            // Add Schedule Form Form
            DropdownButtonFormField<int>(
              initialValue: _selectedDay,
              decoration: const InputDecoration(labelText: 'Day of Week'),
              items: List.generate(7, (i) => DropdownMenuItem(value: i, child: Text(_days[i]))),
              onChanged: (v) => setState(() => _selectedDay = v!),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: InkWell(
                    onTap: () async {
                      final t = await showTimePicker(context: context, initialTime: _startTime);
                      if (t != null) setState(() => _startTime = t);
                    },
                    child: InputDecorator(
                      decoration: const InputDecoration(labelText: 'Start Time'),
                      child: Text(_startTime.format(context)),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: InkWell(
                    onTap: () async {
                      final t = await showTimePicker(context: context, initialTime: _endTime);
                      if (t != null) setState(() => _endTime = t);
                    },
                    child: InputDecorator(
                      decoration: const InputDecoration(labelText: 'End Time'),
                      child: Text(_endTime.format(context)),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<int>(
              initialValue: _slotDuration,
              decoration: const InputDecoration(labelText: 'Slot Duration (minutes)'),
              items: const [
                DropdownMenuItem(value: 15, child: Text('15 Minutes')),
                DropdownMenuItem(value: 30, child: Text('30 Minutes')),
                DropdownMenuItem(value: 60, child: Text('60 Minutes')),
              ],
              onChanged: (v) => setState(() => _slotDuration = v!),
            ),
            const SizedBox(height: 24),
            AppButton(
              label: 'Add Schedule',
              isLoading: actionState.isLoading,
              onPressed: _addSchedule,
            ),
            const SizedBox(height: 48), // Padding
          ],
        ),
      ),
    );
  }
}
