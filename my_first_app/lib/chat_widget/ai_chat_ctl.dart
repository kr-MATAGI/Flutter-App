import 'package:flutter/material.dart';

import '../common/logger.dart';
import 'chat_model.dart';

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
  AIChatController._internal();

  // 채팅 메시지 목록
  final List<ChatModel> messages = [];

  // 사용자 메시지 추가 메서드
  void addMessage(String message) {
    messages.add(ChatModel(role: 'user', content: message));
    AppLogger.info('채팅 메시지 추가: $message');
    notifyListeners();
  }

  // AI 메시지 추가 메서드
  void listenAiResponse(String message) {
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
