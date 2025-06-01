import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/io.dart';
import 'package:web_socket_channel/status.dart' as status;
import 'package:flutter_dotenv/flutter_dotenv.dart';

import 'logger.dart';

/// WebSocket 연결 상태를 나타내는 열거형
enum ConnectionState {
  disconnected, // 연결 해제 상태
  connecting, // 연결 시도 중
  connected, // 연결됨
}

/// WebSocket 연결 및 통신을 관리하는 클래스
class WebSocketConnector {
  // 싱글톤 패턴 구현
  static final WebSocketConnector _instance = WebSocketConnector._internal();
  factory WebSocketConnector() => _instance;
  WebSocketConnector._internal();

  // WebSocket 채널 인스턴스
  IOWebSocketChannel? _channel;

  // 현재 연결 상태
  ConnectionState _state = ConnectionState.disconnected;

  // 메시지 스트림 컨트롤러
  final _messageController = StreamController<String>.broadcast();

  /// 연결 상태 확인
  bool get isConnected => _state == ConnectionState.connected;

  /// 메시지 스트림 getter
  Stream<String> get messageStream => _messageController.stream;

  /// WebSocket 서버에 연결
  Future<void> connect() async {
    if (_state == ConnectionState.connected) {
      AppLogger.info('이미 WebSocket 서버에 연결되어 있습니다.');
      return;
    }

    try {
      // .env 파일에서 WebSocket 설정 가져오기
      final wsHost = dotenv.env['WS_HOST'] ?? 'localhost';
      final wsPort = dotenv.env['WS_PORT'] ?? '8001';
      final wsPrefix = dotenv.env['WS_PREFIX'] ?? 'api/v1/chat/ws';
      final wsPath = dotenv.env['WS_PATH'] ?? 'chat-test';

      // WebSocket URL 구성 (URI 클래스 사용)
      final uri = Uri(
        scheme: 'ws',
        host: wsHost,
        port: int.parse(wsPort),
        pathSegments: [...wsPrefix.split('/'), wsPath],
      );

      AppLogger.info('연결 시도할 WebSocket URL: ${uri.toString()}');

      _state = ConnectionState.connecting;
      AppLogger.info('WebSocket 서버 연결 시도 중...');

      // IOWebSocketChannel 사용하여 연결
      _channel = IOWebSocketChannel.connect(
        uri.toString(),
        headers: {
          'Connection': 'Upgrade',
          'Upgrade': 'websocket',
        },
      );

      // 메시지 수신 리스너 설정
      _channel!.stream.listen(
        (message) {
          // 수신된 메시지를 JSON으로 파싱
          final decodedMessage = utf8.decode(message.toString().codeUnits);
          final jsonData = jsonDecode(decodedMessage) as Map<String, dynamic>;

          // content 필드가 Map인 경우 message 추출
          String displayMessage = '';
          if (jsonData['content'] is Map) {
            displayMessage = (jsonData['content']
                as Map<String, dynamic>)['message'] as String;
          } else {
            displayMessage = jsonData['content'].toString();
          }

          _messageController.add(displayMessage);
          AppLogger.info('메시지 수신 및 파싱: $displayMessage');
        },
        onError: (Object error) {
          AppLogger.error('WebSocket 에러 발생: ${error.toString()}');
          disconnect();
        },
        onDone: () {
          AppLogger.info('WebSocket 연결 종료');
          disconnect();
        },
      );

      _state = ConnectionState.connected;
      AppLogger.info('WebSocket 서버 연결 성공');
    } catch (e) {
      AppLogger.error('WebSocket 연결 실패: ${e.toString()}');
      _state = ConnectionState.disconnected;
      rethrow;
    }
  }

  /// 서버로 메시지 전송
  Future<void> sendMessage(String message) async {
    if (!isConnected) {
      AppLogger.error('WebSocket이 연결되어 있지 않습니다.');
      throw Exception('WebSocket 연결이 필요합니다.');
    }

    try {
      // UTF-8 인코딩하여 메시지 전송
      final encodedMessage = utf8.encode({
        'role': 'user',
        'text': message,
      }.toString());
      _channel!.sink.add(encodedMessage);
      AppLogger.info('메시지 전송: $message');
    } catch (e) {
      AppLogger.error('메시지 전송 실패: ${e.toString()}');
      rethrow;
    }
  }

  /// WebSocket 연결 종료
  Future<void> disconnect() async {
    if (_channel != null) {
      try {
        await _channel!.sink.close(status.goingAway);
        _state = ConnectionState.disconnected;
        AppLogger.info('WebSocket 연결이 정상적으로 종료되었습니다.');
      } catch (e) {
        AppLogger.error('WebSocket 연결 종료 중 오류 발생: ${e.toString()}');
      } finally {
        _channel = null;
      }
    }
  }

  /// 리소스 해제
  void dispose() {
    disconnect();
    _messageController.close();
  }
}
