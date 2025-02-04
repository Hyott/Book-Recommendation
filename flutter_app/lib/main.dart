import 'dart:collection';

import 'package:flutter/material.dart';
import 'package:project/loading.dart';
import 'package:project/question_page.dart';
import 'package:provider/provider.dart';

// void main() {
//   runApp(
//     ChangeNotifierProvider(
//       create: (context) => UserNameProvider(),
//       child: MyApp(),
//     ),
//   );
// }
//
// class UserNameProvider extends ChangeNotifier {
//   String _userName = '';
//
//   String get userName => _userName;
//
//   void updateUserName(String name) {
//     _userName = name;
//     notifyListeners();
//   }
// }
//
//
// class MyApp extends StatelessWidget {
//   // const MyApp({Key? key}) : super(key: key);
//   @override
//   Widget build(BuildContext context) {
//     return MaterialApp(
//       title: '도서 추천 서비스',
//       theme: ThemeData(
//         primarySwatch: Colors.blue,
//       ),
//       debugShowCheckedModeBanner: false,
//       home: MyHomePage(),
//     );
//   }
// }
//
// class MyHomePage extends StatelessWidget {
//   const MyHomePage({super.key});
//
//   @override
//   Widget build(BuildContext context) {
//     return Scaffold(
//       // appBar: AppBar(
//       //   title: const Text('도서 추천 서비스'),
//       // ),
//       body: Container(
//         margin: const EdgeInsets.all(10),
//         child: Column(
//           crossAxisAlignment: CrossAxisAlignment.start,
//           children: [
//             const Text(
//               '안녕하세요, 지금부터 당신의 에세이 취향 테스트를 시작하겠습니다.',
//               style: TextStyle(fontSize: 16),
//             ),
//             Expanded(child: TextFormFieldExample()),
//           ],
//         ),
//       ),
//     );
//   }
// }


void main() {
  runApp(
    ChangeNotifierProvider(
      create: (context) => UserNameProvider(),
      child: MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      // title: '사용자 이름 저장 앱',
      theme: ThemeData(
        useMaterial3: false,
        primarySwatch: Colors.amber,
      ),
      home: NameInputScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class UserNameProvider extends ChangeNotifier {
  String _userName = '사용자'; // 기본값 설정

  String get userName => _userName;

  void updateUserName(String name) {
    // 빈 문자열 처리
    _userName = name.isNotEmpty ? name : '사용자';
    notifyListeners();
  }
}

class NameInputScreen extends StatelessWidget {
  final TextEditingController _nameController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('도서 추천 서비스'),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
            child: Column(
              // crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                SizedBox(height: 10),
                Center(
                  child: Text(
                    '안녕하세요, 지금부터 당신의 에세이 취향을 알아보겠습니다.',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                ),
                SizedBox(height: 150),
                Text(
                  '이름을 입력해주세요. 입력하고 싶지 않으면 바로 시작하기 버튼을 누르세요.',
                  style: TextStyle(fontSize: 15, fontWeight: FontWeight.normal),
                ),
                SizedBox(height: 10),
                TextField(
                  controller: _nameController,
                  decoration: InputDecoration(
                    hintText: '이름을 입력하세요',
                    border: OutlineInputBorder(),
                  ),
                ),
                SizedBox(height: 20),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    minimumSize: Size(300, 50),
                  ),
                  onPressed: () {
                    final userName = _nameController.text;
                    Provider.of<UserNameProvider>(context, listen: false)
                        .updateUserName(userName);
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => ChooseMessageScreen()),
                    );
                  },
                  child: Text('시작하기'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}




















// class FilterChipExample extends StatefulWidget {
//   const FilterChipExample({super.key});
//
//   @override
//   State<FilterChipExample> createState() => _FilterChipExampleState();
// }
//
// class _FilterChipExampleState extends State<FilterChipExample> {
//   final Map<String, List<String>> categories = {
//     '감정': ['행복', '기쁨', '슬픔', '차분'],
//     '가족': ['엄마', '아빠', '형제', '자매'],
//     '쉼': ['여행', '여가활동', '힐링', '소풍'],
//   };
//
//   final Map<String, Set<String>> selectedFilters = {};
//
//   @override
//   void initState() {
//     super.initState();
//     for (var category in categories.keys) {
//       selectedFilters[category] = <String>{};
//     }
//   }
//
//   @override
//   Widget build(BuildContext context) {
//     return Column(
//       children: [
//         Expanded(
//           child: ListView(
//             children: categories.entries.map((entry) {
//               String category = entry.key;
//               List<String> filters = entry.value;
//
//               return Column(
//                 crossAxisAlignment: CrossAxisAlignment.start,
//                 children: [
//                   Text(
//                     category,
//                     style: Theme.of(context).textTheme.titleLarge,
//                   ),
//                   const SizedBox(height: 10),
//                   Wrap(
//                     spacing: 5.0,
//                     children: filters.map((String filter) {
//                       return FilterChip(
//                         label: Text(filter),
//                         selected: selectedFilters[category]?.contains(filter) ?? false,
//                         onSelected: (bool selected) {
//                           setState(() {
//                             if (selected) {
//                               selectedFilters[category]?.add(filter);
//                             } else {
//                               selectedFilters[category]?.remove(filter);
//                             }
//                           });
//                         },
//                       );
//                     }).toList(),
//                   ),
//                   const SizedBox(height: 20),
//                 ],
//               );
//             }).toList(),
//           ),
//         ),
//         Center(
//           child: TextButton(
//             onPressed: () {
//               // 선택한 모든 해시태그를 리스트로 변환
//               final selectedTags = selectedFilters.values.expand((set) => set).toList();
//               if (selectedTags.isNotEmpty) {
//                 Navigator.push(
//                   context,
//                   MaterialPageRoute(
//                     builder: (context) => Loading(selectedTags: selectedTags),
//                   ),
//                 );
//               } else {
//                 ScaffoldMessenger.of(context).showSnackBar(
//                   const SnackBar(content: Text('해시태그를 선택해주세요!')),
//                 );
//               }
//             },
//             child: const Text('선택 완료', style: TextStyle(fontSize: 16)),
//           ),
//         ),
//       ],
//     );
//   }
// }

// Text(
//   '${filters.map((ExerciseFilter e) => filterNames[e]).join(', ')}을 선택하셨습니다.',
//   style: textTheme.labelLarge,
// ),