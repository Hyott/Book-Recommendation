import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:uuid/uuid.dart';

class RecommendationScreen extends StatefulWidget {
  @override
  _RecommendationScreenState createState() => _RecommendationScreenState();
}

class _RecommendationScreenState extends State<RecommendationScreen> {
  final String baseUrl = "http://127.0.0.1:8000"; // FastAPI 백엔드 주소
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
  late int questionA_num;
  late int questionB_num;
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
          questionA_num = data["bookA"]["question_num"];
          questionB_num = data["bookB"]["question_num"];
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
          "question_number": questionA_num,
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
          "question_number": questionA_num,
          "sentence_id": sentenceB_id, // 책 B의 sentence_id 값
          "is_positive": !isBookASelected, // 책 B는 선택되지 않으면 false
          "datetime": DateTime.now().toIso8601String(),
        }),
      );

      if (responseA.statusCode == 200 && responseB.statusCode == 200) {
        // setState(() {
        //   questionA_num++; // 🔹 먼저 증가
        //   // questionB_num++;
        // });
        // questionA_num++;
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
    return Scaffold(
      appBar: AppBar(title: Text("책 추천")),
      body: Center(
        child: sentenceA == null || sentenceB == null
            ? CircularProgressIndicator()
            : Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text("$questionA_num", style: TextStyle(fontSize: 18)),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () => sendUserResponse(bookAIsbn!),
              child: Text(sentenceA!),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () => sendUserResponse(bookBIsbn!),
              child: Text(sentenceB!),
            ),
          ],
        ),
      ),
    );
  }
}





// class NextScreen extends StatefulWidget {
//   @override
//   _NextScreenState createState() => _NextScreenState();
// }
//
// const String apiUrl = 'http://176.16.0.17:8000/newbooks/'; // FastAPI 서버 URL 설정
//
// class _NextScreenState extends State<NextScreen> {
//   late Future<List<Message>> _messages; // 메시지를 담을 변수
//
//   // API에서 message 가져오기
//   Future<List<Message>> fetchMessages({int skip = 0, int limit = 10}) async {
//     final response = await http.get(
//       Uri.parse('$apiUrl?skip=$skip&limit=$limit'),
//     );
//
//     // 상태 코드 로그
//     print('Response status code: ${response.statusCode}');
//
//     final decodedResponseBody = json.decode(utf8.decode(response.bodyBytes));
//
//     if (response.statusCode == 200) {
//       print('Response body: $decodedResponseBody');
//
//       // API 호출 성공 시 message 리스트 반환
//       final List<dynamic> data = decodedResponseBody;
//       return data.map((item) {
//         // item은 Map<String, dynamic> 타입이어야 함
//         return Message.fromJson(item);
//       }).toList();
//     } else {
//       // 실패 시 오류 로그
//       print('Failed to load books. Status code: ${response.statusCode}');
//
//       throw Exception('Failed to load messages: ${response.statusCode}');
//     }
//   }
//
//   @override
//   void initState() {
//     super.initState();
//     _messages = fetchMessages(); // 메시지 로드
//   }
//
//   @override
//   Widget build(BuildContext context) {
//     // UserNameProvider를 사용하여 사용자 이름 가져오기
//     final userName = Provider.of<UserNameProvider>(context).userName;
//
//     return Scaffold(
//       appBar: AppBar(
//         title: Text('도서 추천 서비스'),
//       ),
//       body: FutureBuilder<List<Message>>(
//         future: _messages, // fetchMessages()에서 받은 데이터를 기반으로 버튼 생성
//         builder: (context, snapshot) {
//           if (snapshot.connectionState == ConnectionState.waiting) {
//             return Center(child: CircularProgressIndicator());
//           } else if (snapshot.hasError) {
//             return Center(child: Text('Error: ${snapshot.error}'));
//           } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
//             return Center(child: Text('No books found'));
//           }
//
//           final messages = snapshot.data!;
//
//           return Center(
//             child: Column(
//               mainAxisAlignment: MainAxisAlignment.center,
//               children: [
//                 // 사용자 이름을 포함하여 문구 출력
//                 Text(
//                   '$userName님한테 더 마음이 가는 문장을 골라주세요.',
//                   style: TextStyle(fontSize: 24),
//                 ),
//                 SizedBox(height: 20),
//                 // 첫 번째 메시지 버튼
//                 TextButton(
//                   onPressed: () {
//                     // 첫 번째 메시지 선택 시 처리
//                     ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('첫 번째 문장 선택됨: ${messages[0].message}')));
//                   },
//                   child: Text(
//                     messages[0].message, // 첫 번째 메시지
//                     style: TextStyle(fontSize: 18, color: Colors.blue),
//                   ),
//                 ),
//                 SizedBox(height: 20),
//                 // 두 번째 메시지 버튼
//                 TextButton(
//                   onPressed: () {
//                     // 두 번째 메시지 선택 시 처리
//                     ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('두 번째 문장 선택됨: ${messages[1].message}')));
//                   },
//                   child: Text(
//                     messages[1].message, // 두 번째 메시지
//                     style: TextStyle(fontSize: 18, color: Colors.blue),
//                   ),
//                 ),
//               ],
//             ),
//           );
//         },
//       ),
//     );
//   }
// }
//
// class NextScreen extends StatelessWidget {
//   @override
//   Widget build(BuildContext context) {
//     final userName = Provider.of<UserNameProvider>(context).userName;
//
//     return Scaffold(
//       appBar: AppBar(
//         title: Text('도서 추천 서비스'),
//       ),
//       body: Center(
//         child: Text(
//           '$userName님한테 더 마음이 가는 문장을 골라주세요.',
//           style: TextStyle(fontSize: 24),
//         ),
//       ),
//     );
//   }
// }


// 책 리스트 조회
// const String apiUrl = 'http://127.0.0.1:8000/books/'; // FastAPI 서버 URL 설정
//
// Future<List<Book>> fetchBooks({int skip = 0, int limit = 10}) async {
//   final response = await http.get(
//     Uri.parse('$apiUrl?skip=$skip&limit=$limit'),
//   );
//
//   // 상태 코드 로그
//   print('Response status code: ${response.statusCode}');
//
//   final decodedResponseBody = json.decode(utf8.decode(response.bodyBytes));
//
//   if (response.statusCode == 200) {
//     // 성공 시 응답 데이터 로그
//     print('Response body: $decodedResponseBody');
//
//     final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
//     return data.map((json) => Book.fromJson(json)).toList();
//   } else {
//     // 실패 시 오류 로그
//     print('Failed to load books. Status code: ${response.statusCode}');
//     print('Response body: $decodedResponseBody');
//
//     throw Exception('Failed to load books: ${response.statusCode}');
//   }
// }
//
//
// class BookListPage extends StatefulWidget {
//   @override
//   _BookListPageState createState() => _BookListPageState();
// }
//
// class _BookListPageState extends State<BookListPage> {
//   late Future<List<Book>> books;
//
//   @override
//   void initState() {
//     super.initState();
//     books = fetchBooks();
//   }
//
//   @override
//   Widget build(BuildContext context) {
//     return Scaffold(
//       appBar: AppBar(
//         title: Text('Book List'),
//       ),
//       body: FutureBuilder<List<Book>>(
//         future: books,
//         builder: (context, snapshot) {
//           if (snapshot.connectionState == ConnectionState.waiting) {
//             return Center(child: CircularProgressIndicator());
//           } else if (snapshot.hasError) {
//             return Center(child: Text('Error: ${snapshot.error}'));
//           } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
//             return Center(child: Text('No books found'));
//           }
//           final books = snapshot.data!;
//           return ListView.builder(
//             itemCount: books.length,
//             itemBuilder: (context, index) {
//               final book = books[index];
//               return ListTile(
//                 leading: book.imageUrl != null
//                     ? Container(
//                   decoration: BoxDecoration(
//                     borderRadius: BorderRadius.circular(8.0),
//                     border: Border.all(
//                       color: Colors.amber,
//                       width: 1.0,
//                     ),
//                   ),
//                 child: ClipRRect(
//                   borderRadius: BorderRadius.circular(8.0),
//                   child: Image.network(
//                       book.imageUrl!,
//                       fit: BoxFit.cover,
//                     ),
//                   ),
//                 )
//                     : Icon(Icons.book),
//                 title: Text(book.title),
//                 subtitle: Text(book.author ?? 'Unknown Author'),
//               );
//             },
//           );
//         },
//       ),
//     );
//   }
// }
