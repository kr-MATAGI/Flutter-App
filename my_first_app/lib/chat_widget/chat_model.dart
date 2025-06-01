class ChatModel {
  final String role;
  final String content;

  ChatModel({required this.role, required this.content});

  factory ChatModel.fromJson(Map<String, dynamic> json) => ChatModel(
        role: json['role'] as String,
        content: json['content'] as String,
      );

  Map<String, dynamic> toJson() => {
        'role': role,
        'content': content,
      };
}
