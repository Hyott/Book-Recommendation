import 'package:flutter/material.dart';
import 'package:fromSentence/page/result_page.dart';
import 'package:lottie/lottie.dart';

class LoadingScreen extends StatelessWidget {
  final String userId; // 사용자 ID

  LoadingScreen({required this.userId});

  @override
  Widget build(BuildContext context) {
    Future.delayed(const Duration(seconds: 3), () {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => ResultScreen(userId: userId),
        ),
      );
    });

    return Scaffold(
  body: Container(
    height: double.infinity, // 전체 화면을 차지하도록 설정
    child: Center(
      child: Lottie.asset('assets/loading_animation.json'),
    ),
  ),
);

  } // <- 중괄호 닫기 추가
}