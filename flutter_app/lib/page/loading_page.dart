import 'package:flutter/material.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'package:project/page/result_page.dart';

class LoadingScreen extends StatelessWidget {
  final String userId; // 사용자 ID

  LoadingScreen({required this.userId});

  @override
  Widget build(BuildContext context) {
    Future.delayed(const Duration(seconds: 2), () {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => ResultScreen(userId: userId),
        ),
      );
    });

    return Scaffold(
      backgroundColor: const Color(0xffF49B33),
      body: const Center(
        child: SpinKitPumpingHeart(
          color: Colors.white,
          size: 80.0,
        ),
      ),
    );
  }
}
