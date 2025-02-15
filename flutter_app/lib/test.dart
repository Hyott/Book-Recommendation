// import 'package:flutter/material.dart';
// import 'package:carousel_slider/carousel_slider.dart';
//
// void main() {
//   runApp(MyApp());
// }
//
// class MyApp extends StatelessWidget {
//   @override
//   Widget build(BuildContext context) {
//     return MaterialApp(
//       home: BookCarousel(),
//     );
//   }
// }
//
// class BookCarousel extends StatefulWidget {
//   @override
//   _BookCarouselState createState() => _BookCarouselState();
// }
//
// class _BookCarouselState extends State<BookCarousel> {
//   final List<String> books = [
//     'Book 1',
//     'Book 2',
//     'Book 3',
//     'Book 4',
//     'Book 5',
//   ];
//
//   int currentBookIndex = 0; // Track the currently selected book
//
//   @override
//   Widget build(BuildContext context) {
//     return Scaffold(
//       appBar: AppBar(
//         title: Text("Book Carousel"),
//       ),
//       body: Column(
//         children: [
//           // Carousel Slider for book titles
//           CarouselSlider(
//             items: books.map((book) {
//               return Builder(
//                 builder: (BuildContext context) {
//                   return GestureDetector(
//                     onTap: () {
//                       // When a book is tapped, show the bottom sheet with details
//                       _showBookDetails(book);
//                     },
//                     child: Container(
//                       padding: EdgeInsets.all(16),
//                       width: double.infinity,  // 전체 너비로 설정
//                       color: Colors.yellow[200], // 배경색을 추가하여 구분
//                       child: Text(
//                         book,
//                         style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
//                         textAlign: TextAlign.center, // 중앙 정렬
//                       ),
//                     ),
//                   );
//                 },
//               );
//             }).toList(),
//             options: CarouselOptions(
//               height: 150,
//               enlargeCenterPage: true,
//               autoPlay: false,
//               onPageChanged: (index, reason) {
//                 // Update currentBookIndex when the page changes
//                 setState(() {
//                   currentBookIndex = index;
//                 });
//               },
//             ),
//           ),
//           // Bottom section with "Pull up to view details"
//           GestureDetector(
//             onVerticalDragUpdate: (details) {
//               if (details.primaryDelta! < -10) {
//                 // If dragged upwards, show the bottom sheet
//                 _showBookDetails(books[currentBookIndex]);
//               }
//             },
//             child: Container(
//               width: double.infinity,  // 전체 너비로 설정
//               height: 500,  // 원하는 높이로 설정
//               color: Colors.grey[200],
//               child: Container(
//                 // padding: EdgeInsets.all(16),
//                 width: double.infinity,  // 전체 너비로 설정
//                 height: 500,  // 원하는 높이로 설정
//                 color: Colors.grey[200],
//                 child: Column(
//                   children: [
//                     Text(
//                       "       ⬆️\n당겨보세요",
//                       style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
//                     ),
//                   ],
//                 ),
//               ),
//               // child: Column(
//               //   // mainAxisAlignment: MainAxisAlignment.center,  // 수직 중앙 정렬
//               //   crossAxisAlignment: CrossAxisAlignment.center,  // 수평 중앙 정렬
//               //   children: [
//               //     Row(
//               //       mainAxisAlignment: MainAxisAlignment.center,  // 수평 중앙 정렬
//               //       children: [
//               //         Transform.rotate(
//               //           angle: 4.7124,  // 270도 회전
//               //           child: Text(
//               //             "⟩",
//               //             style: TextStyle(fontSize: 40),  // 크기 설정
//               //           ),
//               //         ),
//               //         Text(
//               //           "\n당겨보세요",
//               //           style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
//               //         ),
//               //       ],
//               //     ),
//               //   ],
//               // ),
//             ),
//           ),
//         ],
//       ),
//     );
//   }
//
//   void _showBookDetails(String book) {
//     showModalBottomSheet(
//       context: context,
//       isScrollControlled: true, // Enable full-screen BottomSheet
//       backgroundColor: Colors.transparent, // Optional: Make it transparent
//       builder: (BuildContext context) {
//         return FractionallySizedBox(
//           alignment: Alignment.bottomCenter,
//           widthFactor: 1.0,  // Make the BottomSheet take the full width
//           heightFactor: 1,   // This makes the BottomSheet take full height
//           child: Container(
//             color: Colors.white,
//             padding: const EdgeInsets.all(16.0),
//             width: double.infinity, // Make it take full width
//             child: Column(
//               children: [
//                 Text(
//                   "Details of $book",
//                   style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
//                 ),
//                 SizedBox(height: 20),
//                 Text("Here will be the details of the book."),
//                 SizedBox(height: 20),
//                 GestureDetector(
//                   onVerticalDragUpdate: (details) {
//                     if (details.primaryDelta! > 10) {
//                       // If dragged down, close the bottom sheet
//                       Navigator.pop(context);
//                     }
//                   },
//                   child: Text(
//                     "Pull down to close",
//                     style: TextStyle(fontSize: 16, color: Colors.blue),
//                   ),
//                 ),
//               ],
//             ),
//           ),
//         );
//       },
//     );
//   }
// }

import 'package:flutter/material.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: MyPageView(),
    );
  }
}

class MyPageView extends StatefulWidget {
  @override
  _MyPageViewState createState() => _MyPageViewState();
}

class _MyPageViewState extends State<MyPageView> {
  final List<String> items = ['Page 1', 'Page 2', 'Page 3'];
  final PageController _controller = PageController();

  double _start = 0.0;  // 드래그 시작 위치

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: GestureDetector(
        onHorizontalDragStart: (details) {
          _start = details.localPosition.dx;
        },
        onHorizontalDragUpdate: (details) {
          double offset = details.localPosition.dx - _start;
          if (offset > 50) {
            _controller.previousPage(duration: Duration(milliseconds: 300), curve: Curves.ease);
            _start = details.localPosition.dx; // 시작 위치 초기화
          } else if (offset < -50) {
            _controller.nextPage(duration: Duration(milliseconds: 300), curve: Curves.ease);
            _start = details.localPosition.dx; // 시작 위치 초기화
          }
        },
        child: PageView.builder(
          controller: _controller,
          itemCount: items.length,
          itemBuilder: (context, index) {
            return Center(
              child: Text(
                items[index],
                style: TextStyle(fontSize: 24),
              ),
            );
          },
        ),
      ),
    );
  }
}
