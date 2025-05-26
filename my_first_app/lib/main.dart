import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'home_view/home_btn.dart';
import 'home_view/home_ctl.dart';

void main() {
  runApp(
    ChangeNotifierProvider(
      create: (context) => HomeController(),
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // 이 위젯은 애플리케이션의 루트(최상위) 위젯입니다.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '플러터 데모',
      theme: ThemeData(
        // 애플리케이션의 테마를 설정합니다.
        //
        // 테스트: "flutter run"으로 애플리케이션을 실행하면
        // 보라색 툴바가 표시됩니다. 앱을 종료하지 않고
        // 아래 colorScheme의 seedColor를 Colors.green으로 변경하고
        // "hot reload"를 실행해보세요 (Flutter 지원 IDE에서 저장하거나
        // "hot reload" 버튼을 누르거나, 콘솔에서 'r'을 누르세요).
        //
        // 카운터가 0으로 초기화되지 않는 것을 확인하세요.
        // 리로드 중에는 애플리케이션의 상태가 유지됩니다.
        // 상태를 초기화하려면 hot restart를 사용하세요.
        //
        // 이는 값뿐만 아니라 코드에도 적용됩니다.
        // 대부분의 코드 변경사항은 hot reload로 테스트할 수 있습니다.
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const MyHomePage(title: '플러터 데모 홈페이지'),
    );
  }
}

class MyHomePage extends StatelessWidget {
  const MyHomePage({super.key, required this.title});

  // 이 위젯은 애플리케이션의 홈페이지입니다.
  // Stateful 위젯이므로, 위젯의 모양에 영향을 주는 필드를 포함하는
  // State 객체(아래에 정의됨)를 가집니다.

  // 이 클래스는 상태에 대한 구성입니다.
  // 부모(이 경우 App 위젯)가 제공한 값(이 경우 제목)을 보관하고
  // State의 build 메서드에서 사용합니다.
  // Widget 하위 클래스의 필드는 항상 "final"로 표시됩니다.

  final String title;

  @override
  Widget build(BuildContext context) {
    // 이 메서드는 setState가 호출될 때마다 다시 실행됩니다.
    // 예를 들어 위의 _incrementCounter 메서드에 의해 실행됩니다.
    //
    // Flutter 프레임워크는 build 메서드를 빠르게 다시 실행할 수 있도록
    // 최적화되어 있어, 위젯을 개별적으로 변경하는 대신
    // 업데이트가 필요한 모든 것을 다시 빌드할 수 있습니다.
    return Scaffold(
      appBar: AppBar(
        // 테스트: 여기서 색상을 특정 색상으로 변경해보세요
        // (예: Colors.amber)
        // hot reload를 실행하면 AppBar의 색상만 변경되고
        // 다른 색상은 그대로 유지되는 것을 확인할 수 있습니다.
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        // App.build 메서드에서 생성된 MyHomePage 객체에서
        // 값을 가져와 AppBar 제목을 설정합니다.
        title: Text(title),
      ),
      body: Center(
        // Center는 레이아웃 위젯입니다.
        // 하나의 자식을 받아 부모의 중앙에 배치합니다.
        child: Column(
          // Column도 레이아웃 위젯입니다.
          // 자식 위젯들의 목록을 받아 세로로 배열합니다.
          // 기본적으로 자식들의 가로 크기에 맞추고,
          // 부모의 높이만큼 세로로 확장됩니다.
          //
          // Column은 자신의 크기와 자식들의 위치를 제어하는
          // 여러 속성을 가집니다. 여기서는 mainAxisAlignment를 사용하여
          // 자식들을 세로축의 중앙에 배치합니다.
          // Column은 세로이므로 메인 축이 세로축입니다
          // (가로축이 교차축이 됩니다).
          //
          // 테스트: "디버그 페인팅"을 실행해보세요
          // (IDE에서 "Toggle Debug Paint" 액션을 선택하거나
          // 콘솔에서 "p"를 누르세요).
          // 각 위젯의 와이어프레임을 볼 수 있습니다.
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Text(
              '버튼을 눌러 카운터를 조작하세요:',
            ),
            Consumer<HomeController>(
              builder: (context, controller, child) => Text(
                '${controller.counter}',
                style: Theme.of(context).textTheme.headlineMedium,
              ),
            ),
            const SizedBox(height: 20),
            Consumer<HomeController>(
              builder: (context, controller, child) => HomeButton(
                onStyleButtonPressed: controller.onStyleButtonPressed,
                onGradientButtonPressed: controller.onGradientButtonPressed,
                onOutlinedButtonPressed: controller.onOutlinedButtonPressed,
                onResetButtonPressed: controller.onResetButtonPressed,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
