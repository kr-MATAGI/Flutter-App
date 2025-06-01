import 'package:flutter/material.dart';

/// 로딩 애니메이션 위젯
class LoadingDots extends StatefulWidget {
  const LoadingDots({super.key});

  @override
  State<LoadingDots> createState() => _LoadingDotsState();
}

class _LoadingDotsState extends State<LoadingDots>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  int _currentDots = 0;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    )..addStatusListener((status) {
        if (status == AnimationStatus.completed) {
          _controller.reset();
          _controller.forward();
          setState(() {
            _currentDots = (_currentDots + 1) % 4;
          });
        }
      });
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(top: 2.0),
        child: Text(
          '.' * _currentDots,
          style: const TextStyle(
            fontSize: 16.0,
            height: 0.5,
            fontWeight: FontWeight.bold,
          ),
        ),
      );
}
