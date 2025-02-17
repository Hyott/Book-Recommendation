import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:project/page/creator_page.dart';
import 'package:provider/provider.dart';
import 'package:share_plus/share_plus.dart';
import 'package:smooth_page_indicator/smooth_page_indicator.dart';
import '../main.dart';
import 'package:cached_network_image/cached_network_image.dart';


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

        // 이미지 경로 출력
        print("이미지 경로: assets/images/books/9788901131207.jpg");

        if (response.statusCode == 200) {
          final data = json.decode(response.body);
          print("ISBN: ${data['isbn']}");
          tempDetails.add({
            "isbn": data["isbn"] ?? "isbn 없음",
            "image_url": data["image_url"] ?? "이미지 없음",
            // "image_url": (data["image_url"] as String?)?.replaceFirst("https", "http") ?? "이미지 없음",
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
    final userName = Provider.of<UserNameProvider>(context).userName;

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
                  height: 0.6,
              ),
            ),
          ),
        ),
      ),
      body: Container(
        // color: Colors.grey[200],
        child: bookDetails.isEmpty
            ? const Center(child: CircularProgressIndicator())
            : GestureDetector(
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
                _currentBookIndex = index; // 책 인덱스 변경
              });
            },
            itemBuilder: (context, index) {
              return Container(
                padding: const EdgeInsets.all(16),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    SmoothPageIndicator(
                      controller: _horizontalPageController,
                      count: bookDetails.length,
                      effect: ScaleEffect(
                        dotHeight: 10,
                        dotWidth: 10,
                        activeDotColor: Color(0xFF6D0003), // 현재 페이지 색상
                        dotColor: Colors.grey.shade400, // 나머지 페이지 색상
                      ),
                    ),
                    const SizedBox(height: 20),
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
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          children: [
                            Text(
                              'To. $userName',
                              style: const TextStyle
                                (
                                  fontFamily: 'GowunBatang',
                                  fontSize: 14,
                                  color: Colors.black
                              ),
                              textAlign: TextAlign.start,
                            ),
                            const SizedBox(height: 8),
                            Text(
                              "\n${bookDetails[index]['letter']}",
                              style: const TextStyle(
                                fontFamily: 'GowunBatang',
                                fontSize: 14,
                                fontWeight: FontWeight.bold,
                                color: Colors.black,
                              ),
                              textAlign: TextAlign.center,
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),
                    Transform.rotate(
                      angle: 4.7124,  // 270도 회전
                      child: Text(
                        "⟩",
                        style: TextStyle
                          (
                            fontFamily: 'JejuMyeongjo',
                            fontSize: 16,
                        ),
                      ),
                    ),
                    // const SizedBox(height: 6),
                    Text(
                      "당겨보세요",
                      style: TextStyle
                        (
                          fontFamily: 'JejuMyeongjo',
                          fontSize: 16,
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        ),
      ),
    );
  }


  // 추천 도서 상세 페이지
  Widget _buildDetailPageView() {
    // final userName = Provider.of<UserNameProvider>(context).userName;

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
                  height: 0.6,
              ),
            ),
          ),
        ),
      ),
      body: bookDetails.isEmpty
          ? const Center(child: CircularProgressIndicator())
          : PageView.builder(
        itemCount: bookDetails.length,
        onPageChanged: (index) {
          setState(() {
            _currentBookIndex = index;
          });
        },
        itemBuilder: (context, index) {
          final book = bookDetails[_currentBookIndex];

          return GestureDetector(
            onVerticalDragUpdate: (details) {
              _verticalPageController.previousPage(
                duration: const Duration(milliseconds: 300),
                curve: Curves.easeOut,
              );
              Future.delayed(const Duration(milliseconds: 100), () {
                _horizontalPageController.jumpToPage(_currentBookIndex);
              });
            },
            child: Column(
              children: [
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        // 책 상세 정보 박스
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
                            padding: const EdgeInsets.all(16.0),
                            child: Column(
                              children: [
                                // 책 이미지 표시 코드
                                AssetImage(
                                  'assets/images/books/9788901131207.jpg',
                                  width: 150,
                                  height: 200,
                                  fit: BoxFit.cover,
                                  errorBuilder: (context, error, stackTrace) {
                                    return AssetImage(
                                      'assets/images/none_book_image.png', // 기본 이미지
                                      width: 150,
                                      height: 200,
                                      fit: BoxFit.cover,
                                    );
                                  },
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  book['tags'],
                                  style: const TextStyle
                                    (
                                      fontFamily: 'GowunBatang',
                                      fontSize: 12,
                                      color: Colors.black
                                  ),
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  "From. ${book['author']}",
                                  style: const TextStyle(
                                    fontFamily: 'GowunBatang',
                                    fontSize: 15,
                                    color: Colors.black,
                                    // decoration: TextDecoration.underline,
                                  ),
                                ),
                                const SizedBox(height: 12),
                              ],
                            ),
                          ),
                        ),
                        const SizedBox(height: 20), // 박스와 버튼 사이 여백

                        // 버튼 영역
                        Column(
                          children: [
                            // 공유하기 & 다시하기 버튼
                            Row(
                              mainAxisAlignment: MainAxisAlignment.center, // 간격 조절
                              children: [
                                ElevatedButton(
                                  style: ElevatedButton.styleFrom(
                                    minimumSize: Size(148, 39),
                                    backgroundColor: Color(0xFFF8F8F8),
                                    side: BorderSide(color: Color(0xFF50513F), width: 0.5),
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(20),
                                    ),
                                  ),
                                  onPressed: () {
                                    // ScaffoldMessenger.of(context).showSnackBar(
                                    //   const SnackBar(content: Text("공유하기 기능 준비 중")),
                                    // );
                                    Share.share('http://localhost:8080/');
                                  },
                                  child: const Text(
                                    '공유하기',
                                    style: TextStyle(
                                        fontFamily: 'JejuMyeongjo',
                                        fontSize: 20,
                                        color: Color(0xFF50513F)
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 10), // 간격 조절
                                ElevatedButton(
                                  style: ElevatedButton.styleFrom(
                                    minimumSize: Size(148, 39),
                                    backgroundColor: Color(0xFFF8F8F8),
                                    side: BorderSide(color: Color(0xFF50513F), width: 0.5),
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(20),
                                    ),
                                  ),
                                  onPressed: () {
                                    // 다시하기 기능 구현
                                    Navigator.pushReplacement(
                                      context,
                                      MaterialPageRoute(builder: (context) => MyApp()), // 시작화면 위젯으로 대체
                                    );
                                  },
                                  child: const Text(
                                    '다시하기',
                                    style: TextStyle(
                                        fontFamily: 'JejuMyeongjo',
                                        fontSize: 20,
                                        color: Color(0xFF50513F)
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 14), // 버튼 사이 여백

                            // 만든 이들 버튼
                            TextButton(
                              onPressed: () {
                                // "만든 이들" 페이지로 이동
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(builder: (context) => CreatorScreen()), // MakersPage로 이동
                                );
                              },
                              child: const Text(
                                '만든 이들',
                                style: TextStyle(
                                    fontFamily: 'JejuMyeongjo',
                                    fontSize: 20,
                                    color: Color(0xFF2A0606)
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }



}
