import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import '../common/logger.dart';
import '../common/ws_connt.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

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
  late final WsConnection _wsConnection;

  AIChatController() {
    _initializeWebSocket();
  }

  void _initializeWebSocket() {
    final wsUrl = "ws://${dotenv.env['WEB_SOCKET_HOST']}:${dotenv.env['WEB_SOCKET_PORT']}/ws/chat";
    _wsConnection = WsConnection(WebSocketChannel.connect(Uri.parse(wsUrl)));
    
    // WebSocket 연결 및 채팅방 입장
    _wsConnection.connect("ai_chat");
    
    // 메시지 수신 리스너 설정
    _wsConnection.stream.listen(
      (message) {
        try {
          final decodedMessage = json.decode(message);
          _handleReceivedMessage(decodedMessage);
        } catch (e) {
          AppLogger.error('WebSocket 메시지 처리 중 오류 발생', e);
          _addErrorMessage('메시지 처리 중 오류가 발생했습니다.');
        }
      },
    );
  }

  void _handleReceivedMessage(Map<String, dynamic> message) {
    if (message['type'] == 'chat_response' && message.containsKey('message')) {
      _messages.add(ChatMessage(
        content: message['message'],
        isUser: false,
      ));
      notifyListeners();
    }
  }

  void _addErrorMessage(String content) {
    _messages.add(ChatMessage(
      content: content,
      isUser: false,
    ));
    notifyListeners();
  }

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
      // WebSocket을 통해 메시지 전송
      final messageData = {
        'type': 'ai_chat',
        'message': message,
        'user_id': '1', // 임시 사용자 ID
      };
      
      _wsConnection.send(json.encode(messageData));
    } catch (e) {
      AppLogger.error('메시지 전송 중 오류 발생', e);
      _addErrorMessage('메시지 전송에 실패했습니다.');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  @override
  void dispose() {
    _wsConnection.close();
    super.dispose();
  }
} 