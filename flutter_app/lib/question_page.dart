import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:uuid/uuid.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

import 'main.dart';

class RecommendationScreen extends StatefulWidget {
  @override
  _RecommendationScreenState createState() => _RecommendationScreenState();
}

class _RecommendationScreenState extends State<RecommendationScreen> {
  final baseUrl = dotenv.env['API_BASE_URL'] ?? 'https://localhost';
  final String userId = const Uuid().v4(); // UUID 생성
  // int questionNumber = 0; // 현재 질문 번호

  String? sentenceA;
  String? sentenceB;
  String? bookAIsbn;
  String? bookBIsbn;
  String? sentenceA_id;
  String? sentenceB_id;
  // int sentenceA_id = 0;
  // int sentenceB_id = 0;
  // late int questionA_num;
  // late int questionB_num;
  late int question_number;
  // int questionA_num = 0;
  // int questionB_num = 0;

  @override
  void initState() {
    super.initState();
    fetchRecommendations(); // 첫 번째 추천 가져오기
  }

  Future<void> fetchRecommendations() async {
    try {
      final response = await http.get(
        Uri.parse("$baseUrl/recommendation/$userId"),
      );

      print("HTTP 요청 URL: $baseUrl/recommendation/$userId");
      print("HTTP 응답 코드: ${response.statusCode}");
      print("HTTP 응답 본문: ${response.body}");

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          // questionA_num = data["bookA"]["question_num"];
          // questionB_num = data["bookB"]["question_num"];
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
        fetchRecommendations(); // 🔹 이후 새로운 질문 불러오기
      } else {
        print("Failed to save response.");
      }
    } catch (e) {
      print("Error sending user response: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    // 화면의 너비를 가져옴
    double screenWidth = MediaQuery.of(context).size.width;

    return Scaffold(
      appBar: PreferredSize(
        preferredSize: Size.fromHeight(100),
        child: AppBar(
          title: null,
          automaticallyImplyLeading: false,
          backgroundColor: primarySwatch,
          flexibleSpace: Center(
            child: Text(
                "from\n    Sentence",
                style: TextStyle(fontSize: 36, color: Color(0xFFF8F8F8))
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
            Text("$question_number / 10", style: TextStyle(fontSize: 24, color: Color(0xFFB4A69B))),
            SizedBox(height: 20),
            Text("      마음에 머무는\n문장은 무엇인가요?", style: TextStyle(fontSize: 27, color: Color(0xFF280404))),
            SizedBox(height: 50),
            Padding(
              padding: EdgeInsets.all(10),
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  padding: EdgeInsets.all(30),
                  backgroundColor: Color(0xFFEADACD),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                  // minimumSize: Size(screenWidth * 0.8, 50), // 버튼 너비는 화면의 80%로 설정
                  minimumSize: Size(355, 70), // 고정된 크기
                ),
                onPressed: () => sendUserResponse(bookAIsbn!),
                child: IntrinsicHeight(
                  child: Center(
                    child: Text(
                      sentenceA!,
                      style: TextStyle(fontSize: 18, color: Color(0xFF280404)),
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
                  // minimumSize: Size(screenWidth * 0.8, 50), // 버튼 너비는 화면의 80%로 설정
                  minimumSize: Size(355, 70), // 고정된 크기
                ),
                onPressed: () => sendUserResponse(bookBIsbn!),
                child: IntrinsicHeight(
                  child: Center(
                    child: Text(
                      sentenceB!,
                      style: TextStyle(fontSize: 18, color: Color(0xFF280404)),
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
