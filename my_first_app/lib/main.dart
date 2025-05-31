import 'package:flutter/material.dart';
import 'home_view/home_view.dart';
import 'common/ws_connt.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

Future<void> main() async {
  // Load dotenv
  await dotenv.load(fileName: ".env");

  // Initialize WebSocket connection
  
  final wsUrl = "ws://${dotenv.env['WEB_SOCKET_HOST']}:${dotenv.env['WEB_SOCKET_PORT']}";
  final wsConnection = WsConnection(WebSocketChannel.connect(Uri.parse(wsUrl)));

  // Connect to WebSocket
  wsConnection.connect("ai_chat");

  // Run the app
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI 채팅 앱',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const HomeView(),
    );
  }
}
