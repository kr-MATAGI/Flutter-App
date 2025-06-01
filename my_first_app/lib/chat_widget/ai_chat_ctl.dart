import 'package:flutter/material.dart';

import '../common/logger.dart';
import 'chat_model.dart';

import '../common/ws_conn.dart';

/*
 * ChangeNotifier: 상태 관리 클래스
 *  - 상태가 변경되었음을 위젯에게 알려주는 역할
*/

/// AI 채팅 컨트롤러 - 싱글톤 패턴 적용
class AIChatController extends ChangeNotifier {
  // 싱글톤 인스턴스
  static final AIChatController _instance = AIChatController._internal();

  // 팩토리 생성자
  factory AIChatController() => _instance;

  // 내부 생성자
  AIChatController._internal() {
    _wsConnector.messageStream.listen((message) {
      listenAiResponse(message);
    });
  }

  // WebSocket 객체
  final WebSocketConnector _wsConnector = WebSocketConnector();

  // 채팅 메시지 목록
  final List<ChatModel> messages = [];

  // 사용자 메시지 추가 메서드
  void addMessage(String message) {
    // 사용자 메시지 추가
    ChatModel userMessage = ChatModel(role: 'user', content: message);
    messages.add(userMessage);

    // 빈 AI 응답 메시지 추가 (로딩 표시용)
    messages.add(ChatModel(role: 'assistant', content: ''));

    // 메시지 전송
    _wsConnector.sendMessage(userMessage.toJson().toString());
    AppLogger.info('채팅 메시지 추가: $userMessage');

    notifyListeners();
  }

  // AI 메시지 추가 메서드
  void listenAiResponse(String message) {
    // 마지막 메시지가 빈 assistant 메시지인 경우 제거
    if (messages.isNotEmpty &&
        messages.last.role == 'assistant' &&
        messages.last.content.isEmpty) {
      messages.removeLast();
    }

    // AI 응답 메시지 추가
    messages.add(ChatModel(role: 'assistant', content: message));
    AppLogger.info('AI 메시지 추가: $message');

    notifyListeners();
  }

  // 모든 메시지 삭제 메서드
  void clearMessages() {
    messages.clear();

    notifyListeners();
  }
}
