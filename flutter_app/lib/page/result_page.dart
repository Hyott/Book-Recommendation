import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:provider/provider.dart';
import 'package:share_plus/share_plus.dart';
import 'package:smooth_page_indicator/smooth_page_indicator.dart';
import '../main.dart';
import 'creator_page.dart';


class ResultScreen extends StatefulWidget {
  final String userId;

  ResultScreen({required this.userId});

  @override
  _ResultScreenState createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  static const String baseUrl = String.fromEnvironment(
    'BASE_URL',
    defaultValue: 'https://fromsentence.com/api',
  );
  List<Map<String, dynamic>> bookDetails = [];
  int _currentBookIndex = 0;  // 현재 선택된 책의 인덱스

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

        if (response.statusCode == 200) {
          final data = json.decode(response.body);
          tempDetails.add({
            "isbn": data["isbn"],
            "image_url": data["image_url"] ?? "이미지 없음",
            "title": data["title"] ?? "제목 없음",
            "author": data["author"] ?? "작가 미상",
            "tags": (data["tags"] as List<dynamic>?)
                ?.map((tag) => "#$tag") // 각 태그 앞에 #을 붙임
                .join(" ") ?? "태그 없음",// 태그들을 공백으로 구분하여 하나의 문자열로 결합
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
      body: Container(
        height: double.infinity, // 화면 전체를 차지하도록 설정
        width: double.infinity,  // 가로도 꽉 차게 설정
        child: PageView(
          scrollDirection: Axis.vertical,
          controller: _verticalPageController,
          children: [
            _buildRecommendationPage(),
            _buildDetailPageView(),
          ],
        ),
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
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const SizedBox(height: 4),
                            Text(
                              'To. $userName',
                              style: const TextStyle
                                (
                                  fontFamily: 'GowunBatang',
                                  fontSize: 14,
                                  color: Colors.black
                              ),
                            ),
                            Text(
                              "\n${bookDetails[index]['letter']}",
                              style: const TextStyle(
                                fontFamily: 'GowunBatang',
                                fontSize: 12  ,
                                height: 1.5,     // 줄 간격 (글자 크기의 1.5배)
                                fontWeight: FontWeight.bold,
                                color: Colors.black,
                                letterSpacing: 2.0, // 자간을 넓히는 부분 (값을 조정 가능)
                                
                              ),
                              textAlign: TextAlign.left,
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),
                    Transform.rotate(
                      angle: 4.7124, 
                      child: Text(
                        "⟩",
                        style: TextStyle
                          (
                            fontFamily: 'JejuMyeongjo',
                            fontSize: 16,
                        ),
                      ),
                    ),
                    Text(
                      "올려보세요",
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
      body: bookDetails.isEmpty
          ? const Center(child: CircularProgressIndicator())
          : PageView.builder(
        physics: const NeverScrollableScrollPhysics(), // 상세페이지에서 옆으로 스와이프 방지
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
                        Transform.rotate(
                          angle: 1.5708, 
                          child: Text(
                            "⟩",
                            style: TextStyle
                              (
                              fontFamily: 'JejuMyeongjo',
                              fontSize: 16,
                            ),
                          ),
                        ),
                        Text(
                          "다른 편지 보기",
                          style: TextStyle
                            (
                            fontFamily: 'JejuMyeongjo',
                            fontSize: 16,
                          ),
                        ),
                        const SizedBox(height: 24),
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
                                Image(
                                  image: AssetImage(
                                    book['isbn'] != null
                                        ? 'assets/images/books/${book['isbn']}.jpg'
                                        : 'assets/images/none_book_image.png', // ISBN이 없으면 기본 이미지 사용
                                  ),
                                  width: 160,
                                  height: 210,
                                  fit: BoxFit.cover,
                                  errorBuilder: (context, error, stackTrace) {
                                    return Image.asset(
                                      'assets/images/none_book_image.png', // 오류 발생시 기본 이미지
                                      width: 160,
                                      height: 210,
                                      fit: BoxFit.cover,
                                    );
                                  },
                                ),
                                const SizedBox(height: 8),
                                RichText(
                                  text: TextSpan(
                                    text: '$userName에게 추천하고 싶은 책은 ',
                                    style: const TextStyle(
                                      fontFamily: 'GowunBatang',
                                      fontSize: 12,
                                      color: Colors.black,
                                    ),
                                    children: <TextSpan>[
                                      TextSpan(
                                        text: '${book['title']} ',
                                        style: const TextStyle(
                                          fontFamily: 'GowunBatang',
                                          fontSize: 12,
                                          color: Colors.black,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      TextSpan(
                                        text: '(${book['author']}) 입니다.',
                                        style: const TextStyle(
                                          fontFamily: 'GowunBatang',
                                          fontSize: 12,
                                          color: Colors.black,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                const SizedBox(height: 11),
                                Text(
                                  book['tags'],
                                  style: _getDynamicTextStyle(book['title'], book['tags']),
                                ),
                                const SizedBox(height: 18),
                                Align(
                                  alignment: Alignment.centerRight,
                                  child: Text(
                                    "From. Sentence",
                                    style: const TextStyle(
                                      fontFamily: 'GowunBatang',
                                      fontSize: 14,
                                      color: Colors.black,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                        const SizedBox(height: 20),
                        // 버튼 영역
                        Column(
                          children: [
                            // 공유하기 & 다시하기 버튼
                            Row(
                              mainAxisAlignment: MainAxisAlignment.center,
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
                                const SizedBox(width: 10),
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
                                // "만든 이들" 페이지로 이동
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(builder: (context) => CreatorScreen()),
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
                            const SizedBox(height: 14),
                            // 만든 이들 버튼
                            // TextButton(
                            //   onPressed: () {
                            //     // "만든 이들" 페이지로 이동
                            //     Navigator.push(
                            //       context,
                            //       MaterialPageRoute(builder: (context) => CreatorScreen()),
                            //     );
                            //   },
                            //   child: const Text(
                            //     '만든 이들',
                            //     style: TextStyle(
                            //         fontFamily: 'JejuMyeongjo',
                            //         fontSize: 20,
                            //         color: Color(0xFF2A0606)
                            //     ),
                            //   ),
                            // ),
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

  TextStyle _getDynamicTextStyle(String text1, String text2) {
    print("title length: ${text1.length}, hashtag length: ${text2.length}");
    print("Total length: ${text1.length + text2.length}");
    return TextStyle(
      fontSize: text1.length + text2.length > 90 ? 10 : 12, // 90글자 이상이면 폰트 크기를 줄이기
      fontWeight: FontWeight.bold,
      fontFamily: 'GowunBatang',
      color: Colors.black,
    );
  }

}
