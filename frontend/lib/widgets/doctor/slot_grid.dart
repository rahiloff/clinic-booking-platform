import 'package:flutter/material.dart';
import '../../models/slot.dart';

class SlotGrid extends StatelessWidget {
  final List<Slot> slots;
  final String? selectedSlotId;
  final Function(Slot) onSlotSelected;

  const SlotGrid({
    super.key,
    required this.slots,
    this.selectedSlotId,
    required this.onSlotSelected,
  });

  @override
  Widget build(BuildContext context) {
    if (slots.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Text(
            'No slots available for this date.',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          ),
        ),
      );
    }

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
        maxCrossAxisExtent: 120,
        childAspectRatio: 2.2,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
      ),
      itemCount: slots.length,
      itemBuilder: (context, index) {
        final slot = slots[index];
        final isAvailable = slot.status == 'available';
        final isSelected = slot.id == selectedSlotId;

        // Strip seconds from "10:30:00" backend format
        final displayTime = slot.startTime.length >= 5 
            ? slot.startTime.substring(0, 5) 
            : slot.startTime;

        return Material(
          color: isSelected 
              ? Theme.of(context).colorScheme.primary 
              : (isAvailable ? Theme.of(context).colorScheme.surface : Colors.grey.shade100),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
            side: BorderSide(
              color: isSelected 
                  ? Theme.of(context).colorScheme.primary 
                  : (isAvailable ? Colors.grey.shade300 : Colors.transparent),
            ),
          ),
          child: InkWell(
            onTap: isAvailable ? () => onSlotSelected(slot) : null,
            borderRadius: BorderRadius.circular(8),
            child: Center(
              child: Text(
                displayTime,
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  color: isSelected 
                      ? Colors.white 
                      : (isAvailable ? Theme.of(context).colorScheme.onSurface : Colors.grey.shade400),
                  decoration: isAvailable ? TextDecoration.none : TextDecoration.lineThrough,
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}
