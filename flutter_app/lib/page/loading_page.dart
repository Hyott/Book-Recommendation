import 'package:flutter/material.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';

// class Loading extends StatelessWidget {
//   final List<String> selectedTags;
//
//   const Loading({Key? key, required this.selectedTags}) : super(key: key);
//
//   @override
//   Widget build(BuildContext context) {
//     Future.delayed(const Duration(seconds: 3), () {
//       Navigator.pushReplacement(
//         context,
//         MaterialPageRoute(
//           builder: (context) => RecommendationPage(selectedTags: selectedTags),
//         ),
//       );
//     });
//
//     return Scaffold(
//       backgroundColor: const Color(0xffF49B33),
//       body: const Center(
//         child: SpinKitPumpingHeart(
//           color: Colors.white,
//           size: 80.0,
//         ),
//       ),
//     );
//   }
// }
