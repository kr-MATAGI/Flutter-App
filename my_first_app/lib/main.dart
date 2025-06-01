import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'home_widget/home_widget.dart';

Future<void> main() async {
  // Load dotenv
  await dotenv.load(fileName: ".env");

  // Run the app
  runApp(const MyApp());
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
          body: Center(
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
