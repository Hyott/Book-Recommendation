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
  List<Map<String, dynamic>> bookDetails = [];
  PageController _verticalPageController = PageController();
  PageController _horizontalPageController = PageController();

  @override
  void initState() {
    super.initState();
    fetchRecommendations();
  }

  // 추천 도서 ISBN 목록 가져오기
  Future<void> fetchRecommendations() async {
    try {
      final response = await http.get(
        Uri.parse("$baseUrl/final_recommendation/${widget.userId}"),
      );
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
          tempSentences.add(data["sentence"]); // JSON에서 문장 가져오기
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

  // bookDetails[index]['sentence']

  // // 각 도서의 문장 및 상세정보 가져오기
  // Future<void> fetchBookDetails(List<dynamic> isbnList) async {
  //   List<Map<String, dynamic>> tempDetails = [];
  //
  //   for (String isbn in isbnList) {
  //     try {
  //       final response = await http.get(Uri.parse("$baseUrl/sentences/$isbn"));
  //       if (response.statusCode == 200) {
  //         final data = json.decode(response.body);
  //         tempDetails.add({
  //           "isbn": isbn,
  //           "sentence": data["sentence"],
  //           "title": data["title"] ?? "제목 없음",
  //           "author": data["author"] ?? "작가 미상",
  //           "description": data["description"] ?? "소개 없음"
  //         });
  //       }
  //     } catch (e) {
  //       print("Error fetching sentence for ISBN $isbn: $e");
  //     }
  //   }
  //
  //   setState(() {
  //     bookDetails = tempDetails;
  //   });
  // }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: PageView(
        scrollDirection: Axis.vertical,
        controller: _verticalPageController,
        children: [
          // 추천도서 목록 페이지
          _buildRecommendationPage(),
          // 추천도서 상세보기 페이지 (PageView)
          _buildDetailPageView(),
        ],
      ),
    );
  }

  // 추천 도서 목록 페이지
  Widget _buildRecommendationPage() {
    return Container(
      color: Colors.grey[200],
      child: Column(
        children: [
          Container(
            color: primarySwatch,
            height: 100,
            child: const Center(
              child: Text(
                "from\nSentence",
                style: TextStyle(fontSize: 36, color: Colors.white),
                textAlign: TextAlign.center,
              ),
            ),
          ),
          if (sentences.isEmpty)
            const Expanded(child: Center(child: CircularProgressIndicator()))
          else
            Expanded(
              child: GestureDetector(
                onHorizontalDragUpdate: (details) {
                  if (details.primaryDelta! < -10) {
                    _horizontalPageController.nextPage(
                      duration: const Duration(milliseconds: 300),
                      curve: Curves.easeOut,
                    );
                  } else if (details.primaryDelta! > 10) {
                    _horizontalPageController.previousPage(
                      duration: const Duration(milliseconds: 300),
                      curve: Curves.easeOut,
                    );
                  }
                },
                onVerticalDragUpdate: (details) {
                  if (details.primaryDelta! < -10) {
                    _verticalPageController.nextPage(
                      duration: const Duration(milliseconds: 300),
                      curve: Curves.easeOut,
                    );
                  }
                },
                child: PageView.builder(
                  controller: _horizontalPageController,
                  itemCount: sentences.length,
                  itemBuilder: (context, index) {
                    return Container(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Container(
                            width: 300,
                            height: 400,
                            decoration: BoxDecoration(
                              image: const DecorationImage(
                                image: AssetImage('assets/images/result_page_image.jpg'),
                                fit: BoxFit.cover,
                              ),
                              // borderRadius: BorderRadius.circular(12),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black26,
                                  blurRadius: 10,
                                  spreadRadius: 2,
                                ),
                              ],
                            ),
                            alignment: Alignment.center,
                            child: Padding(
                              padding: const EdgeInsets.all(20.0),
                              child: Text(
                                sentences[index],
                                style: const TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.black,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ),
                          ),
                          const SizedBox(height: 24),
                          const Text(
                            "⬆️ 당겨보세요",
                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ),
            ),
        ],
      ),
    );
  }

  // 도서 상세보기 페이지 (PageView)
  Widget _buildDetailPageView() {
    return bookDetails.isEmpty
        ? const Center(child: CircularProgressIndicator())
        : PageView.builder(
      scrollDirection: Axis.horizontal,
      physics: const NeverScrollableScrollPhysics(), // ⛔ 스와이프 비활성화
      itemCount: bookDetails.length,
      itemBuilder: (context, index) {
        final book = bookDetails[index];
        return GestureDetector(
          onVerticalDragUpdate: (details) {
            if (details.primaryDelta! > 10) {
              // 아래로 스와이프 시 추천도서 목록으로 복귀
              _verticalPageController.animateToPage(
                0,
                duration: const Duration(milliseconds: 300),
                curve: Curves.easeOut,
              );
            }
          },
          child: Scaffold(
            appBar: AppBar(
              backgroundColor: primarySwatch,
              title: const Text(
                "from Sentence",
                style: TextStyle(fontSize: 20, color: Colors.white),
              ),
              automaticallyImplyLeading: false,
            ),
            body: SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 책 제목
                  Text(
                    book['title'],
                    style: const TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  // 저자
                  Text(
                    "저자: ${book['author']}",
                    style: const TextStyle(
                      fontSize: 16,
                      color: Colors.grey,
                    ),
                  ),
                  const SizedBox(height: 16),
                  // 도서 추천 문장
                  Text(
                    "\"${book['sentence']}\"",
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w500,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                  const SizedBox(height: 24),
                  // 도서 설명
                  Text(
                    book['description'],
                    style: const TextStyle(fontSize: 16),
                  ),
                  const SizedBox(height: 24),
                  // 공유 및 다시보기 버튼
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      ElevatedButton(
                        onPressed: () {
                          // 공유 기능
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text("공유하기 기능 준비 중")),
                          );
                        },
                        child: const Text("공유하기"),
                      ),
                      ElevatedButton(
                        onPressed: () {
                          // 다시보기: 목록으로 돌아가기
                          _verticalPageController.animateToPage(
                            0,
                            duration: const Duration(milliseconds: 300),
                            curve: Curves.easeOut,
                          );
                        },
                        child: const Text("다시보기"),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}

