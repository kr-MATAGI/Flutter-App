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

        try {
            // .env 파일에서 API 키와 모델명 로드
            final envApiKey = dotenv.env['OPENAI_API_KEY'];
            final envModelName = dotenv.env['AI_MODEL_NAME'];

            if (envApiKey == null || envApiKey.isEmpty) {
                throw Exception("API 키가 설정되지 않았습니다.");
            }

            if (envModelName == null || envModelName.isEmpty) {
                throw Exception("모델 이름이 설정되지 않았습니다.");
            }

            _apiKey = envApiKey;
            _modelName = envModelName;
            _isInitialized = true;

            notifyListeners();
        } catch (e) {
            debugPrint("AIChatController 초기화 실패: $e");
            rethrow;
        }
    }

    // AI 채팅 화면 열기
    void onOpenAIChatView() {
        if (!_isInitialized) {
            throw Exception("컨트롤러가 초기화되지 않았습니다.");
        }
        notifyListeners();
    }
}