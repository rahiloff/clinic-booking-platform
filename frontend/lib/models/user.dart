class User {
  final String id;
  final String phone;
  final String fullName;
  final String role;

  User({
    required this.id,
    required this.phone,
    required this.fullName,
    required this.role,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      phone: json['phone'] as String,
      fullName: json['full_name'] as String,
      role: json['role'] as String,
    );
  }
}
