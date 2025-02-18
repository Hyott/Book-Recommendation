import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:uuid/uuid.dart';
import '../main.dart';
import 'loading_page.dart';

class QuestionScreen extends StatefulWidget {
  @override
  _QuestionScreenState createState() => _QuestionScreenState();
}

class _QuestionScreenState extends State<QuestionScreen> {
  static const String baseUrl = String.fromEnvironment(
    'BASE_URL',
    defaultValue: 'https://fromsentence.com/api',
  );
  final String userId = const Uuid().v4(); // UUID 생성

  String? sentenceA;
  String? sentenceB;
  String? bookAIsbn;
  String? bookBIsbn;
  String? sentenceA_id;
  String? sentenceB_id;
  // late int question_number;
  int question_number = 0;

  @override
  void initState() {
    super.initState();
    fetchRecommendations(); // 첫 번째 추천 가져오기
  }

  Future<void> fetchRecommendations() async {
    if (question_number >= 10) return;
    try {
      final response = await http.get(
        Uri.parse("$baseUrl/recommendation/$userId"),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          question_number = data["bookA"]["question_num"];
          bookAIsbn = data["bookA"]["isbn"];
          bookBIsbn = data["bookB"]["isbn"];
          sentenceA = data["bookA"]["sentence"]; // 백엔드에서 문장 데이터 가져오기
          sentenceB = data["bookB"]["sentence"];
          sentenceA_id = data["bookA"]["sentence_id"];
          sentenceB_id = data["bookB"]["sentence_id"];
        });
      } else {
        throw Exception("Failed to load recommendations");
      }
    } catch (e) {
      print("Error fetching recommendations: $e");
    }
  }


  Future<void> sendUserResponse(String selectedIsbn) async {
    bool isBookASelected = selectedIsbn == bookAIsbn;

    try {
      final responseA = await http.post(
        Uri.parse("$baseUrl/user_responses/"),
        headers: {"Content-Type": "application/json"},
        body: json.encode({
          "user_id": userId,
          "question_number": question_number,
          "sentence_id": sentenceA_id, // 책 A의 sentence_id 값 
          "is_positive": isBookASelected, // 책 A를 선택하면 true
          "datetime": DateTime.now().toIso8601String(),
        }),
      );

      final responseB = await http.post(
        Uri.parse("$baseUrl/user_responses/"),
        headers: {"Content-Type": "application/json"},
        body: json.encode({
          "user_id": userId,
          "question_number": question_number,
          "sentence_id": sentenceB_id, // 책 B의 sentence_id 값
          "is_positive": !isBookASelected, // 책 B는 선택되지 않으면 false
          "datetime": DateTime.now().toIso8601String(),
        }),
      );

      if (responseA.statusCode == 200 && responseB.statusCode == 200) {
        if (question_number == 10) {
          // 마지막 질문에서 결과 페이지로 이동
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => LoadingScreen(userId: userId)), // 로딩 화면으로 이동
          );
        } else {
          fetchRecommendations(); // 🔹 이후 새로운 질문 불러오기
        }
      } else {
        print("Failed to save response.");
      }
    } catch (e) {
      print("Error sending user response: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    double screenWidth = MediaQuery.of(context).size.width;

    return Scaffold(
      appBar: PreferredSize(
        preferredSize: Size.fromHeight(80),
        child: AppBar(
          title: null,
          automaticallyImplyLeading: false,
          backgroundColor: primarySwatch,
          flexibleSpace: Center(
            child: Text(
              "from\n    Sentence",
              style: TextStyle
                (
                  fontFamily: 'AbhayaLibre',
                  fontSize: 36,
                  color: Color(0xFFF8F8F8),
                  height: 0.6, // 줄 간격을 기본값보다 더 줄이기
              ),
            ),
          ),
        ),
      ),
      body: Center(
        child: sentenceA == null || sentenceB == null
            ? CircularProgressIndicator()
            : Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
                "$question_number / 10",
                style: TextStyle
                  (
                    fontFamily: 'Inter',
                    fontSize: 24,
                    color: Color(0xFFB4A69B)
                )
            ),
            SizedBox(height: 20),
            Text("      마음에 머무는\n문장은 무엇인가요?",
                style: TextStyle
                  (
                    fontFamily: 'JejuMyeongjo',
                    fontSize: 27,
                    color: Color(0xFF280404)
                )
            ),
            SizedBox(height: 50),
            Padding(
              padding: EdgeInsets.all(10),
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  padding: EdgeInsets.all(30),
                  backgroundColor: Color(0xFFEADACD),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                  minimumSize: Size(355, 70),
                ),
                onPressed: () => sendUserResponse(bookAIsbn!),
                child: IntrinsicHeight(
                  child: Center(
                    child: Text(
                      sentenceA!,
                      style: TextStyle
                        (
                          fontFamily: 'Roboto',
                          fontSize: 18,
                          color: Color(0xFF280404)
                      ),
                    ),
                  ),
                ),
              ),
            ),
            SizedBox(height: 20),
            Padding(
              padding: EdgeInsets.all(10),
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  padding: EdgeInsets.all(30),
                  backgroundColor: Color(0xFFEADACD),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                  minimumSize: Size(355, 70),
                ),
                onPressed: () => sendUserResponse(bookBIsbn!),
                child: IntrinsicHeight(
                  child: Center(
                    child: Text(
                      sentenceB!,
                      style: TextStyle
                        (
                          fontFamily: 'Roboto',
                          fontSize: 18,
                          color: Color(0xFF280404)
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}