import 'package:flutter/material.dart';
import '../chat_view/ai_chat_view.dart';

// 버튼 동작을 관리하는 컨트롤러
class HomeController extends ChangeNotifier {
    int _counter = 0;
  
    // 현재 카운터 값 getter
    int get counter => _counter;

    // 기본 스타일 버튼 동작: +1
    void onStyleButtonPressed() {
        _counter++;
        notifyListeners();
    }
  
    // AI 채팅 오픈
    void onOpenAIChatView() {
        
        notifyListeners();
    }
    
}
