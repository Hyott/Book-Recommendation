// import 'package:flutter/material.dart';
// import 'package:project/selected_book.dart';
//
//
// class RecommendationPage extends StatelessWidget {
//   final List<String> selectedTags;
//
//   const RecommendationPage({Key? key, required this.selectedTags})
//       : super(key: key);
//
//   @override
//   Widget build(BuildContext context) {
//     // 임시 데이터: 해시태그별 관련 문장
//     final Map<String, List<String>> bookSentences = {
//       "행복": [
//         "행복은 멀리 있는 것이 아니라 바로 눈앞에 있다.",
//         "매일 아침 웃음으로 시작하는 하루가 행복의 비결이다.",
//         "행복은 공유될 때 배가 된다."
//       ],
//       "여행": [
//         "여행은 자신을 재발견하는 가장 좋은 방법이다.",
//         "길 위에서 우리는 잊었던 자유를 되찾는다.",
//         "여행이란 목적지가 아니라 여정 그 자체다."
//       ],
//       "기쁨": [
//         "작은 성공도 기쁨으로 받아들이자.",
//         "기쁨은 삶에 활력을 불어넣는다.",
//       ],
//       "힐링": [
//         "힐링이란 스스로를 사랑하는 시간입니다.",
//         "자연 속에서의 시간이 힐링의 시작입니다.",
//       ],
//     };
//
//     // 선택한 해시태그에 따라 관련 문장 가져오기
//     List<String> sentences = selectedTags
//         .expand((tag) => bookSentences[tag] ?? ["관련 문장이 없습니다."])
//         .toList();
//
//     return Scaffold(
//       appBar: AppBar(
//         title: const Text('추천 결과'),
//         // leading: IconButton(
//         //   icon: const Icon(Icons.home),
//         //   onPressed: () {
//         //     // 홈 화면으로 이동
//         //     Navigator.popUntil(context, (route) => route.isFirst);
//         //   },
//         // ),
//       ),
//       body: Padding(
//         padding: const EdgeInsets.all(20.0),
//         child: Column(
//           crossAxisAlignment: CrossAxisAlignment.start,
//           children: [
//             const Text(
//               '선택한 해시태그:',
//               style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
//             ),
//             const SizedBox(height: 10),
//             Wrap(
//               spacing: 10,
//               children: selectedTags
//                   .map((tag) => Chip(label: Text(tag)))
//                   .toList(),
//             ),
//             const SizedBox(height: 20),
//             const Text(
//               '추천 문장:',
//               style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
//             ),
//             const SizedBox(height: 10),
//             ...sentences.map((sentence) => Text(
//               '- $sentence',
//               style: const TextStyle(fontSize: 16),
//             )),
//             ElevatedButton(
//               onPressed: () {
//                 Navigator.push(
//                   context,
//                   MaterialPageRoute(
//                     builder: (context) => BookDetailPage(),
//                   ),
//                 );
//               },
//               child: const Text("이 책 더 보기"),
//             ),
//             const SizedBox(height: 10),
//             ElevatedButton(
//               onPressed: () {
//                 // setState(() {
//                 //   currentIndex = (currentIndex + 1) % recommendations.length;
//                 // });
//               },
//               child: const Text("관심 없음"),
//             ),
//           ],
//         ),
//       ),
//     );
//   }
// }

import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:project/selected_book.dart';

class RecommendationPage extends StatefulWidget {
  final List<String> selectedTags;

  const RecommendationPage({Key? key, required this.selectedTags})
      : super(key: key);

  @override
  State<RecommendationPage> createState() => _RecommendationPageState();
}

class _RecommendationPageState extends State<RecommendationPage> {
  List<dynamic> recommendations = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    fetchRecommendations();
  }

  Future<void> fetchRecommendations() async {
    final url = Uri.parse('http://176.16.0.19:8000/recommendations/');
    final response = await http.get(
      url.replace(queryParameters: {'tags': widget.selectedTags}),
    );

    if (response.statusCode == 200) {
      setState(() {
        recommendations = json.decode(response.body);
        isLoading = false;
      });
    } else {
      setState(() {
        isLoading = false;
      });
      throw Exception("Failed to load recommendations");
    }
  }


  // @override
  // void initState() {
  //   super.initState();
  //   _recommendations = fetchRecommendations(widget.selectedTags);
  // }

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('추천 결과'),
        ),
        body: const Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('추천 결과'),
      ),
      body: ListView.builder(
        itemCount: recommendations.length,
        itemBuilder: (context, index) {
          final book = recommendations[index];
          return Card(
            child: ListTile(
              leading: Image.network(book['image']),
              title: Text(book['title']),
              subtitle: Text(book['key_sentences']),
              onTap: () {
                // 책 상세 화면으로 이동
              },
            ),
          );
        },
      ),
    );
  }
}

//   @override
//   Widget build(BuildContext context) {
//     return Scaffold(
//       appBar: AppBar(
//         title: const Text('추천 문장'),
//       ),
//       body: FutureBuilder<List<dynamic>>(
//         future: _recommendations,
//         builder: (context, snapshot) {
//           if (snapshot.connectionState == ConnectionState.waiting) {
//             return const Center(child: CircularProgressIndicator());
//           } else if (snapshot.hasError) {
//             return Center(
//               child: Text('오류 발생: ${snapshot.error}'),
//             );
//           } else if (snapshot.hasData) {
//             final books = snapshot.data!;
//             return ListView.builder(
//               itemCount: books.length,
//               itemBuilder: (context, index) {
//                 final book = books[index];
//                 return Card(
//                   margin: const EdgeInsets.symmetric(vertical: 10, horizontal: 20),
//                   child: ListTile(
//                     leading: Image.network(
//                       book['image'],
//                       width: 50,
//                       height: 50,
//                       fit: BoxFit.cover,
//                     ),
//                     title: Text(book['title']),
//                     subtitle: Text(book['key_sentences']),
//                     onTap: () {
//                       Navigator.push(
//                         context,
//                         MaterialPageRoute(
//                           builder: (context) => BookDetailPage(book: book),
//                         ),
//                       );
//                     },
//                   ),
//                 );
//               },
//             );
//           } else {
//             return const Center(
//               child: Text('추천된 책이 없습니다.'),
//             );
//           }
//         },
//       ),
//     );
//   }
// }


