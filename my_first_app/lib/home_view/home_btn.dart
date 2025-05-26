import 'package:flutter/material.dart';

// 버튼 스타일을 정의하는 위젯
class HomeButton extends StatelessWidget {
  final VoidCallback onStyleButtonPressed;
  final VoidCallback onGradientButtonPressed;
  final VoidCallback onOutlinedButtonPressed;
  final VoidCallback onResetButtonPressed;

  const HomeButton({
    super.key,
    required this.onStyleButtonPressed,
    required this.onGradientButtonPressed,
    required this.onOutlinedButtonPressed,
    required this.onResetButtonPressed,
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

  // 그라데이션 효과가 있는 버튼
  Widget _buildGradientButton() {
    return Container(
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Colors.purple, Colors.blue],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(30),
      ),
      child: ElevatedButton(
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.transparent,
          foregroundColor: Colors.white,
          shadowColor: Colors.transparent,
          padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 15),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(30),
          ),
        ),
        onPressed: onGradientButtonPressed,
        child: const Text('그라데이션 버튼'),
      ),
    );
  }

  // 아웃라인이 있는 버튼
  Widget _buildOutlinedButton() {
    return OutlinedButton.icon(
      style: OutlinedButton.styleFrom(
        foregroundColor: Colors.purple,
        side: const BorderSide(color: Colors.purple, width: 2),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
      ),
      onPressed: onOutlinedButtonPressed,
      icon: const Icon(Icons.double_arrow),
      label: const Text('2배로 증가'),
    );
  }

  // 리셋 버튼
  Widget _buildResetButton() {
    return InkWell(
      onTap: onResetButtonPressed,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 25, vertical: 10),
        decoration: BoxDecoration(
          color: Colors.red.shade100,
          borderRadius: BorderRadius.circular(15),
          boxShadow: [
            BoxShadow(
              color: Colors.red.withOpacity(0.3),
              spreadRadius: 1,
              blurRadius: 5,
              offset: const Offset(0, 3),
            ),
          ],
        ),
        child: const Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.refresh, color: Colors.red),
            SizedBox(width: 8),
            Text('초기화', style: TextStyle(color: Colors.red)),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        _buildStyledButton(),
        const SizedBox(height: 15),
        _buildGradientButton(),
        const SizedBox(height: 15),
        _buildOutlinedButton(),
        const SizedBox(height: 15),
        _buildResetButton(),
      ],
    );
  }
}