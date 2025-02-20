import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:fromSentence/page/question_page.dart';
import 'package:fromSentence/page/result_page.dart'; // 결과 페이지 추가
import 'package:provider/provider.dart';

// 색상 팔레트 정의
Map<int, Color> colorSwatch = {
  50: Color(0xFFF0D8D7),
  100: Color(0xFFD99E9D),
  200: Color(0xFFB87776),
  300: Color(0xFF9F4F4F),
  400: Color(0xFF8A3838),
  500: Color(0xFF6D0003), // 기본 색상
  600: Color(0xFF660002),
  700: Color(0xFF550001),
  800: Color(0xFF440001),
  900: Color(0xFF330000),
};

// MaterialColor로 만든 팔레트
MaterialColor primarySwatch = MaterialColor(0xFF6D0003, colorSwatch);

void main() {
  const String baseUrl = String.fromEnvironment(
    'BASE_URL',
    defaultValue: 'https://fromsentence.com/api', // 기본값 확인
  );

  print("현재 사용 중인 API URL: $baseUrl");  // 🚀 여기에 배치해야 오류 없음.

  runApp(
    ChangeNotifierProvider(
      create: (context) => UserNameProvider(),
      child: MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData(
        useMaterial3: false,
        primarySwatch: primarySwatch, // 정의한 MaterialColor 사용
        fontFamily: 'JejuMyeongjo',
      ),
      debugShowCheckedModeBanner: false,
      onGenerateRoute: (settings) {
        Uri uri = Uri.parse(settings.name ?? "");

        if (uri.pathSegments.isNotEmpty && uri.pathSegments[0] == 'final_recommendation') {
          // URL에서 userId 추출
          String userId = uri.pathSegments.length > 1 ? uri.pathSegments[1] : "";
          
          return MaterialPageRoute(
            builder: (context) => ResultScreen(userId: userId),
          );
        }

        // 기본적으로 홈 화면으로 이동
        return MaterialPageRoute(builder: (context) => NameInputScreen());
      },
      home: NameInputScreen(), // 기존 홈 화면 유지
    );
  }
}

class UserNameProvider extends ChangeNotifier {
  String _userName = '당신'; // 기본값 설정

  String get userName => _userName;

  void updateUserName(String name) {
    // 빈 문자열 처리
    _userName = name.isNotEmpty ? name : '당신';
    notifyListeners();
  }
}

class NameInputScreen extends StatelessWidget {
  final TextEditingController _nameController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
            child: Column(
              children: [
                SizedBox(height: 10),
                Center(),
                SizedBox(height: 100),
                Image.asset('assets/images/main_logo_image.png',  
                width: 355, // 원하는 너비
                height: 120, // 원하는 높이
                fit: BoxFit.contain), // 비율을 유지하며 이미지가 컨테이너 안에 들어가도록 함),
                const SizedBox(height: 30),
                Text(
                  '문장으로부터\n책으로 이끄는 순간까지',
                  style: TextStyle(fontSize: 22, fontWeight: FontWeight.normal),
                  textAlign: TextAlign.center,
                ),
                SizedBox(height: 100),
                SizedBox(
                  width: 355,
                  height: 60,
                  child: TextField(
                    controller: _nameController,
                    inputFormatters: [LengthLimitingTextInputFormatter(10)], // 최대 10자 제한
                    decoration: InputDecoration(
                        hintText: '이름 입력하기',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(20),
                        ),
                      counterText: "", // 기본 글자 수 카운터 숨기기
                    ),
                    style: TextStyle(fontFamily: 'Inter', fontSize: 24),
                    textAlign: TextAlign.center,
                  ),
                ),
                SizedBox(height: 20),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    minimumSize: Size(355, 70),
                    backgroundColor: Color(0xFFF8F8F8),
                    side: BorderSide(color: Color(0xFF484637), width: 0.5),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(20)
                    )
                  ),
                  onPressed: () {
                    final userName = _nameController.text;
                    Provider.of<UserNameProvider>(context, listen: false)
                        .updateUserName(userName);
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => QuestionScreen()),
                    );
                  },
                  child: Text(
                    '시작',
                    style: TextStyle(fontSize: 30, color: Color(0xFF280404)),
                  ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
