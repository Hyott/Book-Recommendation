import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:provider/provider.dart';
import '../main.dart';

class ResultScreen extends StatefulWidget {
  final String userId;

  ResultScreen({required this.userId});

  @override
  _ResultScreenState createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  final String baseUrl = "http://127.0.0.1:8000";
  List<Map<String, dynamic>> bookDetails = [];
  // PageController _verticalPageController = PageController();
  // PageController _horizontalPageController = PageController();
  int _currentBookIndex = 0;  // 현재 선택된 책의 인덱스를 추적

  late PageController _verticalPageController;
  late PageController _horizontalPageController;

  @override
  void initState() {
    super.initState();
    _verticalPageController = PageController();
    _horizontalPageController = PageController();
    fetchRecommendations();
  }

  @override
  void dispose() {
    _verticalPageController.dispose();
    _horizontalPageController.dispose();
    super.dispose();
  }


  // 추천 도서 ISBN 목록 가져오기
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
        await fetchBookDetails(isbnList);
      } else {
        throw Exception("추천 결과를 불러오는 데 실패했습니다.");
      }
    } catch (e) {
      print("Error fetching recommendations: $e");
    }
  }

  // 각 도서의 문장 및 상세정보 가져오기
  Future<void> fetchBookDetails(List<dynamic> isbnList) async {
    List<Map<String, dynamic>> tempDetails = [];

    for (String isbn in isbnList) {
      try {
        final response = await http.get(Uri.parse("$baseUrl/books/$isbn"));

        print("HTTP 요청 URL: $baseUrl/books/$isbn");
        print("HTTP 응답 코드: ${response.statusCode}");
        print("HTTP 응답 본문: ${response.body}");

        if (response.statusCode == 200) {
          final data = json.decode(response.body);
          tempDetails.add({
            "image_url": data["image_url"] ?? "이미지 없음",
            "author": data["author"] ?? "작가 미상",
            "tags": (data["tags"] as List<dynamic>)
                .map((tag) => "#$tag") // 각 태그 앞에 #을 붙임
                .join(" "), // 태그들을 공백으로 구분하여 하나의 문자열로 결합
            "sentence": data["sentence"] ?? "문장 없음",
            "letter": data["letter"] ?? "편지 없음",
          });
        }
      } catch (e) {
        print("Error fetching book details for ISBN $isbn: $e");
      }
    }

    setState(() {
      bookDetails = tempDetails;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: PageView(
        scrollDirection: Axis.vertical,
        controller: _verticalPageController,
        children: [
          _buildRecommendationPage(),
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
          if (bookDetails.isEmpty)
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
                  itemCount: bookDetails.length,
                  onPageChanged: (index) {
                    setState(() {
                      _currentBookIndex = index;  // 책 인덱스 변경
                    });
                  },
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
                                bookDetails[index]["sentence"],
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

  // 도서 상세보기 페이지
  Widget _buildDetailPageView() {
    // UserNameProvider를 사용하여 사용자 이름 가져오기
    final userName = Provider.of<UserNameProvider>(context).userName;


    return bookDetails.isEmpty
        ? const Center(child: CircularProgressIndicator())
        : PageView.builder(
      itemCount: bookDetails.length,
      onPageChanged: (index) {
        setState(() {
          _currentBookIndex = index;
        });
      },
      itemBuilder: (context, index) {
        final book = bookDetails[_currentBookIndex];  // 선택된 책 정보
        return GestureDetector(
          onVerticalDragUpdate: (details) {
            _verticalPageController.previousPage(
              duration: Duration(milliseconds: 300),
              curve: Curves.easeOut,
            );
            Future.delayed(Duration(milliseconds: 100), () {
              _horizontalPageController.jumpToPage(_currentBookIndex); // 사용자가 보던 책 위치로 이동
            });
          },
          child: Container(
            color: Colors.grey[200],  // 배경색을 설정
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
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          width: 300,
                          height: 400,
                          decoration: BoxDecoration(
                            image: DecorationImage(
                              image: AssetImage('assets/images/result_page_image.jpg'),
                              fit: BoxFit.cover,
                            ),
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
                            padding: const EdgeInsets.all(16.0),
                            child: Column(
                              // crossAxisAlignment: CrossAxisAlignment.center,
                              children: [
                                // 사용자 이름을 포함하여 문구 출력
                                Text(
                                  'To. $userName',
                                  style: TextStyle(fontSize: 14, color: Colors.black),
                                ),
                                // // 책 이미지
                                // Image.network(
                                //   book['image_url']!,
                                //   width: 141,
                                //   height: 210,
                                //   fit: BoxFit.cover,
                                // ),
                                const SizedBox(height: 16),
                                // 저자
                                Text(
                                  "${book['author']}",
                                  style: const TextStyle(
                                    fontSize: 15,
                                    color: Colors.black,
                                    decoration: TextDecoration.underline
                                  ),
                                ),
                                const SizedBox(height: 8),
                                // 태그
                                Text(
                                  "${book['tags']}",
                                  style: const TextStyle(fontSize: 12, color: Colors.black),
                                ),
                                const SizedBox(height: 8),
                                // 편지 내용
                                Text(
                                  "\n${book['letter']}",
                                  style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.black),
                                  textAlign: TextAlign.center, // 편지 내용 가운데 정렬
                                ),
                                const SizedBox(height: 12),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                  // 공유 및 다시보기 버튼
                  Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                      ElevatedButton(
                      onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text("공유하기 기능 준비 중")),
                );
                },
                  child: const Text("공유하기"),
                ),
                ElevatedButton(
                onPressed: () {

                },
                child: const Text("다시하기"),
                ),
                ElevatedButton(
                onPressed: () {

                },
                child: const Text("만든 이들"),
                ),
                ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }


}
