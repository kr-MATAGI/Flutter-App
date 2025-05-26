import 'package:flutter/material.dart';

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

  // 그라데이션 버튼 동작: +2
  void onGradientButtonPressed() {
    _counter += 2;
    notifyListeners();
  }

  // 아웃라인 버튼 동작: ×2
  void onOutlinedButtonPressed() {
    _counter *= 2;
    notifyListeners();
  }

  // 리셋 버튼 동작: 0으로 초기화
  void onResetButtonPressed() {
    _counter = 0;
    notifyListeners();
  }
}
