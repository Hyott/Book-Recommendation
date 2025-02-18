import 'package:flutter/material.dart';
import 'package:project/page/result_page.dart';
import 'package:lottie/lottie.dart';


class LoadingScreen extends StatelessWidget {
  final String userId; // 사용자 ID

  LoadingScreen({required this.userId});

  @override
  Widget build(BuildContext context) {
    Future.delayed(const Duration(seconds: 5), () {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => ResultScreen(userId: userId),
        ),
      );
    });

    return Scaffold(
      body: Center(
        child: Lottie.asset('assets/loading_animation.json'),
      ),
    );
  }
}
