import 'package:flutter/material.dart';
import '../common/logger.dart';
import '../chat_widget/ai_chat_widget.dart';

/// AI 채팅 버튼 위젯
class AiChatButton extends StatelessWidget {
  // 버튼 텍스트를 받는 변수
  final String buttonText;

  // 생성자
  const AiChatButton({Key? key, required this.buttonText}) : super(key: key);

  /// AI 채팅방을 여는 함수
  void onPressedOpenAiChat(BuildContext context) {
    AppLogger.info('AI 채팅 버튼이 클릭되었습니다');

    // 하단 시트로 채팅방 표시
    showModalBottomSheet<void>(
      context: context,
      // 배경을 투명하게 설정
      backgroundColor: Colors.transparent,
      // 드래그로 닫을 수 있도록 설정
      isDismissible: true,
      // 하단 시트가 나타날 때 애니메이션 설정
      isScrollControlled: true,
      builder: (context) => const AiChatBottomSheet(),
    );
  }

  @override
  Widget build(BuildContext context) => ElevatedButton(
        onPressed: () => onPressedOpenAiChat(context),
        style: ElevatedButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          backgroundColor: Colors.blue,
          foregroundColor: Colors.white,
        ),
        child: Text(buttonText),
      );
}
