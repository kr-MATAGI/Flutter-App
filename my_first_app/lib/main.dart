import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

import 'common/logger.dart';
import 'common/ws_conn.dart';
import 'home_widget/home_widget.dart';

Future<void> main() async {
  try {
    // Flutter 바인딩 초기화
    WidgetsFlutterBinding.ensureInitialized();

    // 환경 변수 로드
    await dotenv.load(fileName: ".env");
    AppLogger.info('환경 변수 로드 완료');

    // WebSocket 연결 시도
    final wsConnector = WebSocketConnector();
    await wsConnector.connect();

    // 앱 실행
    runApp(const MyApp());
  } catch (e) {
    AppLogger.error('앱 초기화 중 오류 발생', e);
    // 오류가 발생해도 앱은 실행
    runApp(const MyApp());
  }
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'AI 채팅 앱',
        home: Scaffold(
          appBar: AppBar(
            title: const Text('홈 화면'),
            backgroundColor: Colors.blue,
          ),
          body: const Center(
            child: AiChatButton(
              buttonText: "AI 채팅",
            ),
          ),
        ),
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
          useMaterial3: true,
        ),
      );
}
