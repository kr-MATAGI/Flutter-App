import 'package:flutter/material.dart';
import '../common/logger.dart';

/// AI 채팅 하단 시트 위젯
class AiChatBottomSheet extends StatelessWidget {
  // 생성자
  const AiChatBottomSheet({super.key});

  @override
  Widget build(BuildContext context) {
    // 화면 크기 정보 가져오기
    final screenHeight = MediaQuery.of(context).size.height;
    // 키보드 높이 가져오기
    final bottomInset = MediaQuery.of(context).viewInsets.bottom;

    return Padding(
      // 키보드 높이만큼 패딩 추가
      padding: EdgeInsets.only(bottom: bottomInset),
      child: Container(
        height: screenHeight / 3, // 화면 높이의 1/3 크기
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.only(
            topLeft: Radius.circular(20),
            topRight: Radius.circular(20),
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black12,
              blurRadius: 10,
              spreadRadius: 5,
            )
          ],
        ),
        child: Column(
          children: [
            // 상단 드래그 핸들
            Container(
              margin: const EdgeInsets.symmetric(vertical: 10),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            // 채팅방 제목
            const Padding(
              padding: EdgeInsets.all(16.0),
              child: Text(
                'AI 채팅',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            // 채팅 내용이 표시될 영역
            Expanded(
              child: Container(
                padding: const EdgeInsets.all(16.0),
                child: const Center(
                  child: Text('채팅 내용이 여기에 표시됩니다'),
                ),
              ),
            ),
            // 입력 필드는 하단에 고정
            const SafeArea(
              child: Padding(
                padding: EdgeInsets.fromLTRB(10, 0, 10, 0),
                child: UserChatInputField(),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// 사용자 채팅 입력 위젯
class UserChatInputField extends StatelessWidget {
  // 생성자
  const UserChatInputField({super.key});

  @override
  Widget build(BuildContext context) => TextField(
        decoration: InputDecoration(
          hintText: '메시지를 입력하세요',
          filled: true,
          fillColor: Colors.grey[100],
          suffixIcon: IconButton(
            icon: const Icon(Icons.send),
            onPressed: () {
              // TODO: 메시지 전송 처리
              AppLogger.info('메시지 전송 버튼이 클릭되었습니다');
            },
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(20),
            borderSide: BorderSide.none,
          ),
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 20,
            vertical: 10,
          ),
        ),
      );
}
