import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../main.dart';

class ResultScreen extends StatefulWidget {
  final String userId; // 사용자 ID

  ResultScreen({required this.userId});

  @override
  _ResultScreenState createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  final String baseUrl = "http://127.0.0.1:8000";
  List<String> sentences = [];
  PageController _pageController = PageController();

  @override
  void initState() {
    super.initState();
    fetchRecommendations();
  }

  Future<void> fetchRecommendations() async {
    try {
      final response = await http.get(
        Uri.parse("$baseUrl/final_recommendation/${widget.userId}"),
      );

      print("HTTP 요청 URL: $baseUrl/final_recommendation/${widget.userId}");
      print("HTTP 응답 코드: ${response.statusCode}");
      print("HTTP 응답 본문: ${response.body}");

      if (response.statusCode == 200) {
        List<dynamic> isbnList = json.decode(response.body);
        fetchSentences(isbnList);
      } else {
        throw Exception("추천 결과를 불러오는 데 실패했습니다.");
      }
    } catch (e) {
      print("Error fetching recommendations: $e");
    }
  }

  Future<void> fetchSentences(List<dynamic> isbnList) async {
    List<String> tempSentences = [];

    for (String isbn in isbnList) {
      try {
        final response = await http.get(Uri.parse("$baseUrl/sentences/$isbn"));

        print("HTTP 요청 URL: $baseUrl/sentences/$isbn");
        print("HTTP 응답 코드: ${response.statusCode}");
        print("HTTP 응답 본문: ${response.body}");

        if (response.statusCode == 200) {
          final data = json.decode(response.body);
          tempSentences.add(data["isbn"]); // JSON에서 문장 가져오기
        } else {
          print("문장 데이터를 불러올 수 없습니다.");
        }
      } catch (e) {
        print("Error fetching sentence for ISBN $isbn: $e");
      }
    }

    setState(() {
      sentences = tempSentences;
    });
  }

  @override
  Widget build(BuildContext context) {
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
              style: TextStyle(fontSize: 36, color: Color(0xFFF8F8F8)),
            ),
          ),
        ),
      ),
      body: sentences.isEmpty
          ? Center(child: CircularProgressIndicator())
          : PageView.builder(
        controller: _pageController,
        itemCount: sentences.length,
        itemBuilder: (context, index) {
          return Center(
            child: Padding(
              padding: EdgeInsets.all(20),
              child: Text(
                sentences[index],
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
            ),
          );
        },
      ),
    );
  }
}