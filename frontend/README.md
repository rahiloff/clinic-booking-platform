# Doctor Booking Platform — Frontend

## Technology

- **Framework**: Flutter Web (Dart)
- **State Management**: Riverpod
- **HTTP Client**: Dio
- **Routing**: GoRouter

## Setup

### Prerequisites

- Flutter SDK 3.x installed
- Chrome browser for web development

### Initialize

```bash
# Create Flutter project (run once)
flutter create --project-name docbook_frontend --platforms web .

# Get dependencies
flutter pub get

# Run development server
flutter run -d chrome --web-port 3000
```

### Structure (will be created in Phase 5)

```
lib/
├── main.dart
├── screens/        # Full-page screens
├── widgets/        # Reusable UI components
├── services/       # API communication layer
├── providers/      # Riverpod state providers
├── models/         # Dart data models
└── utils/          # Constants, helpers, theme
```

## Notes

This directory will be initialized as a Flutter project in Phase 5.
The Flutter SDK must be installed first.
