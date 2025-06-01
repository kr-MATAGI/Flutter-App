import 'package:logger/logger.dart';

class AppLogger {
  static final Logger _logger = Logger(
    printer: SimplePrinter(colors: true),
  );

  static void debug(dynamic message) {
    _logger.d('🔍 $message');
  }

  static void info(dynamic message) {
    _logger.i('💡 $message');
  }

  static void error(dynamic message, [dynamic error, StackTrace? stackTrace]) {
    _logger.e('❌ $message', error: error, stackTrace: stackTrace);
  }
}
