import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class AIChatController extends ChangeNotifier {
    String _modelName = "";
    String _apiKey = "";
    bool _isInitialized = false;
    
    // 초기화 상태 확인
    bool get isInitialized => _isInitialized;
    
    // API 키와 모델명 getter
    String get apiKey => _apiKey;
    String get modelName => _modelName;

    // 컨트롤러 초기화
    Future<void> initialize() async {
        if (_isInitialized) return;

        _isInitialized = true;
    }

    // AI 채팅 전달
    void onSendChatMessage(String message) {
        if (!_isInitialized) {
            throw Exception("컨트롤러가 초기화되지 않았습니다.");
        }
        notifyListeners();
    }
}