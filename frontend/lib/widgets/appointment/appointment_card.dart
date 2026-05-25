import 'package:flutter/material.dart';
import '../../models/appointment.dart';
import 'package:intl/intl.dart';

class AppointmentCard extends StatelessWidget {
  final Appointment appointment;
  final VoidCallback? onCancel;
  final bool isCancelling;

  const AppointmentCard({
    super.key,
    required this.appointment,
    this.onCancel,
    this.isCancelling = false,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isBooked = appointment.status == 'booked';
    final isCancelled = appointment.status == 'cancelled';

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    appointment.doctorName ?? 'Doctor',
                    style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: isBooked ? Colors.blue.shade50 : (isCancelled ? Colors.red.shade50 : Colors.grey.shade50),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    appointment.status.toUpperCase(),
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: isBooked ? Colors.blue.shade700 : (isCancelled ? Colors.red.shade700 : Colors.grey.shade700),
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                )
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Icon(Icons.calendar_today, size: 16, color: theme.colorScheme.onSurfaceVariant),
                const SizedBox(width: 8),
                Text(
                  appointment.slotDate != null ? DateFormat('MMM dd, yyyy').format(DateTime.parse(appointment.slotDate!)) : 'Unknown Date',
                  style: theme.textTheme.bodyMedium,
                ),
                const SizedBox(width: 16),
                Icon(Icons.access_time, size: 16, color: theme.colorScheme.onSurfaceVariant),
                const SizedBox(width: 8),
                Text(
                  appointment.slotTime != null && appointment.slotTime!.length >= 5 
                      ? appointment.slotTime!.substring(0, 5) 
                      : 'Unknown',
                  style: theme.textTheme.bodyMedium,
                ),
              ],
            ),
            if (isBooked && onCancel != null) ...[
              const SizedBox(height: 16),
              Align(
                alignment: Alignment.centerRight,
                child: TextButton.icon(
                  onPressed: isCancelling ? null : onCancel,
                  icon: isCancelling 
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.cancel_outlined, color: Colors.red),
                  label: Text('Cancel Appointment', style: TextStyle(color: isCancelling ? Colors.grey : Colors.red)),
                ),
              )
            ]
          ],
        ),
      ),
    );
  }
}
