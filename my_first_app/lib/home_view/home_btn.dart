import 'package:flutter/material.dart';

// 버튼 스타일을 정의하는 위젯
class HomeButton extends StatelessWidget {
  final VoidCallback onStyleButtonPressed;

  const HomeButton({
    super.key,
    required this.onStyleButtonPressed,
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