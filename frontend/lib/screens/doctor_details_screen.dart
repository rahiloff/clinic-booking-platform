import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../models/doctor.dart';
import '../models/slot.dart';
import '../providers/doctor_provider.dart';
import '../providers/appointment_provider.dart';
import '../widgets/common/loading_view.dart';
import '../widgets/common/error_view.dart';
import '../widgets/common/app_button.dart';
import '../widgets/doctor/slot_grid.dart';

class DoctorDetailsScreen extends ConsumerStatefulWidget {
  final String doctorId;
  final Doctor? initialDoctor;

  const DoctorDetailsScreen({
    super.key,
    required this.doctorId,
    this.initialDoctor,
  });

  @override
  ConsumerState<DoctorDetailsScreen> createState() => _DoctorDetailsScreenState();
}

class _DoctorDetailsScreenState extends ConsumerState<DoctorDetailsScreen> {
  late DateTime selectedDate;
  Slot? selectedSlot;

  @override
  void initState() {
    super.initState();
    selectedDate = DateTime.now();
  }

  void _bookSlot() async {
    if (selectedSlot == null) return;
    
    final success = await ref.read(bookingProvider.notifier).bookSlot(selectedSlot!.id);
    if (!mounted) return;

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Appointment booked successfully!'), backgroundColor: Colors.green),
      );
      Navigator.of(context).pop();
    } else {
      final error = ref.read(bookingProvider).error.toString();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(error), backgroundColor: Theme.of(context).colorScheme.error),
      );
      // Conflict happened: refresh slots automatically to show the one just booked is gone
      final query = SlotQuery(widget.doctorId, DateFormat('yyyy-MM-dd').format(selectedDate));
      ref.invalidate(doctorSlotsProvider(query));
      setState(() => selectedSlot = null);
    }
  }

  @override
  Widget build(BuildContext context) {
    // If not passed via router extra, fetch it
    final doctorAsync = ref.watch(doctorDetailProvider(widget.doctorId));
    final dateStr = DateFormat('yyyy-MM-dd').format(selectedDate);
    final slotsAsync = ref.watch(doctorSlotsProvider(SlotQuery(widget.doctorId, dateStr)));
    final bookingState = ref.watch(bookingProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Doctor Profile')),
      bottomNavigationBar: selectedSlot != null
          ? SafeArea(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: AppButton(
                  label: 'Book for ${selectedSlot!.startTime.substring(0, 5)}',
                  isLoading: bookingState.isLoading,
                  onPressed: _bookSlot,
                ),
              ),
            )
          : null,
      body: doctorAsync.when(
        loading: () => const LoadingView(),
        error: (e, st) => ErrorView(message: e.toString()),
        data: (doctor) {
          final doc = widget.initialDoctor ?? doctor;
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Profile Header
                Row(
                  children: [
                    CircleAvatar(
                      radius: 40,
                      backgroundColor: theme.colorScheme.primary.withAlpha(25),
                      child: Text(
                        doc.user != null && doc.user!.fullName.isNotEmpty ? doc.user!.fullName.substring(0, 1) : 'D',
                        style: theme.textTheme.headlineMedium?.copyWith(color: theme.colorScheme.primary),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(doc.user?.fullName ?? 'Unknown', style: theme.textTheme.headlineSmall),
                          Text(doc.specialization, style: theme.textTheme.titleMedium?.copyWith(color: theme.colorScheme.primary)),
                          const SizedBox(height: 4),
                          Text('₹${doc.consultationFee / 100} Consultation Fee', style: theme.textTheme.bodyMedium),
                        ],
                      ),
                    )
                  ],
                ),
                const SizedBox(height: 24),
                if (doc.bio != null) ...[
                  Text('About', style: theme.textTheme.titleLarge),
                  const SizedBox(height: 8),
                  Text(doc.bio!, style: theme.textTheme.bodyMedium),
                  const SizedBox(height: 24),
                ],

                // Date Picker
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Select Date', style: theme.textTheme.titleLarge),
                    TextButton.icon(
                      icon: const Icon(Icons.calendar_month),
                      label: Text(DateFormat('MMM dd, yyyy').format(selectedDate)),
                      onPressed: () async {
                        final date = await showDatePicker(
                          context: context,
                          initialDate: selectedDate,
                          firstDate: DateTime.now(),
                          lastDate: DateTime.now().add(const Duration(days: 30)),
                        );
                        if (date != null) {
                          setState(() {
                            selectedDate = date;
                            selectedSlot = null; // reset selection
                          });
                        }
                      },
                    )
                  ],
                ),
                const SizedBox(height: 16),

                // Slots Grid
                slotsAsync.when(
                  loading: () => const SizedBox(height: 200, child: LoadingView()),
                  error: (e, st) => ErrorView(message: e.toString(), onRetry: () => ref.refresh(doctorSlotsProvider(SlotQuery(doc.id, dateStr)))),
                  data: (slots) => SlotGrid(
                    slots: slots,
                    selectedSlotId: selectedSlot?.id,
                    onSlotSelected: (slot) => setState(() => selectedSlot = slot),
                  ),
                ),
                const SizedBox(height: 80), // Padding for bottom bar
              ],
            ),
          );
        },
      ),
    );
  }
}
