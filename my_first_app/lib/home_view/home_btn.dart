import 'package:flutter/material.dart';

// 버튼 스타일을 정의하는 위젯
class HomeButton extends StatelessWidget {
  final VoidCallback onStyleButtonPressed;
  final VoidCallback onAIChatButtonPressed;

  const HomeButton({
    super.key,
    required this.onStyleButtonPressed,
    required this.onAIChatButtonPressed,
  });

  // 스타일이 적용된 기본 버튼
  Widget _buildStyledButton() {
    return ElevatedButton(
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 30, vertical: 15),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
      ),
      onPressed: onStyleButtonPressed,
      child: const Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.add),
          SizedBox(width: 8),
          Text('스타일 버튼'),
        ],
      ),
    );
  }

  // 아래 버튼을 누르면 AI 채팅 View Open
  Widget _buildAIChatButton() {
    return ElevatedButton(
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 30, vertical: 15),
      ),
      onPressed: onAIChatButtonPressed,
      child: const Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.chat),
          SizedBox(width: 8),
          Text('AI 채팅'),
        ],
      )
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        _buildStyledButton(),
      ],
    );
  }

}