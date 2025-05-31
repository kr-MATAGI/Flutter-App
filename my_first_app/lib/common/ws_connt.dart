import 'dart:async';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:flutter/foundation.dart';
import 'logger.dart';

class WsConnection {
  final WebSocketChannel _channel;
  final _messageController = StreamController<dynamic>.broadcast();
  bool _isConnected = false;
  String _currentRoom = '';

  WsConnection(this._channel) {
    // WebSocket 메시지 리스닝 시작
    _channel.stream.listen(
      (message) {
        _messageController.add(message);
        AppLogger.debug('WebSocket 메시지 수신: $message');
      },
      onError: (error) {
        AppLogger.error('WebSocket 에러 발생', error);
        _isConnected = false;
      },
      onDone: () {
        AppLogger.info('WebSocket 연결 종료');
        _isConnected = false;
      },
    );
  }

  // 메시지 스트림 getter
  Stream<dynamic> get stream => _messageController.stream;

  // 연결 상태 getter
  bool get isConnected => _isConnected;

  // 현재 연결된 방 getter
  String get currentRoom => _currentRoom;

  // WebSocket 연결 및 방 입장
  void connect(String room) {
    if (_isConnected) {
      AppLogger.warning('이미 WebSocket에 연결되어 있습니다.');
      return;
    }

    try {
      _currentRoom = room;
      _isConnected = true;
      
      // 방 입장 메시지 전송
      send({
        'type': 'join_room',
        'room': room,
      });
      
      AppLogger.info('WebSocket 연결 성공: $room 방에 입장');
    } catch (e) {
      AppLogger.error('WebSocket 연결 실패', e);
      _isConnected = false;
      rethrow;
    }
  }

  // 메시지 전송
  void send(dynamic message) {
    if (!_isConnected) {
      AppLogger.warning('WebSocket이 연결되어 있지 않습니다.');
      return;
    }

    try {
      _channel.sink.add(message);
      AppLogger.debug('WebSocket 메시지 전송: $message');
    } catch (e) {
      AppLogger.error('메시지 전송 실패', e);
      rethrow;
    }
  }

  // 방 나가기
  void leaveRoom() {
    if (!_isConnected || _currentRoom.isEmpty) return;

    try {
      send({
        'type': 'leave_room',
        'room': _currentRoom,
      });
      _currentRoom = '';
      AppLogger.info('방 나가기 성공');
    } catch (e) {
      AppLogger.error('방 나가기 실패', e);
      rethrow;
    }
  }

  // WebSocket 연결 종료
  void close() {
    if (_isConnected) {
      leaveRoom();
    }
    
    _channel.sink.close();
    _messageController.close();
    _isConnected = false;
    AppLogger.info('WebSocket 연결 종료됨');
  }
}