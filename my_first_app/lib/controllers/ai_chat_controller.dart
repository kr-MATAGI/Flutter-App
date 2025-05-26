import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class ChatMessage {
  final String content;
  final bool isUser;
  final DateTime timestamp;

  ChatMessage({
    required this.content,
    required this.isUser,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();
}

class AIChatController extends ChangeNotifier {
  final List<ChatMessage> _messages = [];
  List<ChatMessage> get messages => _messages;
  bool _isLoading = false;
  bool get isLoading => _isLoading;

  // FastAPI 서버 URL
  static const String _baseUrl = 'http://localhost:8000/api/v1';

  Future<void> sendMessage(String message) async {
    if (message.trim().isEmpty) return;

    // 사용자 메시지 추가
    _messages.add(ChatMessage(
      content: message,
      isUser: true,
    ));
    notifyListeners();

    _isLoading = true;
    notifyListeners();

    try {
      // FastAPI 서버로 메시지 전송
      final response = await http.post(
        Uri.parse('$_baseUrl/chat'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'user_id': '1', // 임시 사용자 ID
          'message': message,
          'room_id': '1', // 임시 방 ID
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        // AI 응답 메시지 추가
        _messages.add(ChatMessage(
          content: data['data']['message'],
          isUser: false,
        ));
      } else {
        // 오류 메시지 추가
        _messages.add(ChatMessage(
          content: '죄송합니다. 오류가 발생했습니다.',
          isUser: false,
        ));
      }
    } catch (e) {
      // 네트워크 오류 메시지 추가
      _messages.add(ChatMessage(
        content: '네트워크 오류가 발생했습니다.',
        isUser: false,
      ));
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
} 