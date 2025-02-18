import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../main.dart';

class CreatorScreen extends StatelessWidget {
  const CreatorScreen({Key? key}) : super(key: key);

  // 커피 후원 페이지로 링크 열기
  _launchURL() async {
    const url = 'https://buymeacoffee.com/fromsentence';  // 커피 후원 링크
    if (await canLaunch(url)) {
      await launch(url);  // 링크 열기
    } else {
      throw 'Could not launch $url';
    }
  }

  @override
  Widget build(BuildContext context) {
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
              style: TextStyle(
                fontFamily: 'AbhayaLibre',
                fontSize: 36,
                color: Color(0xFFF8F8F8),
                height: 0.6, // 줄 간격을 기본값보다 더 줄이기
              ),
            ),
          ),
        ),
      ),
      body: SingleChildScrollView(  // 스크롤 가능
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(height: 40),
            Align(
              alignment: Alignment.topCenter,
              child: Text(
                '책을 고르는 순간이 설렘으로 가득 차길 바랍니다.\n\n\n\n'
                    '서점에서 어떤 책을 읽어야 할지 망설여질 때,\n\n'
                    '혹은 새로운 취향의 책을 발견하고 싶을 때,\n\n'
                    'fromSentence가 당신만을 위한 특별한 한 권을 찾아드릴게요.\n\n'
                    '감성과 효율을 동시에 담아, 더 깊이 있는 독서 경험을 선물하는 것.\n\n'
                    '그것이 fromSentence를 만든 toReader 팀의 바람입니다.\n\n'
                    '책을 통해 더 넓은 세상을 만나는 여정,\n\n'
                    '이제 fromSentence와 함께하세요.\n\n',
                style: TextStyle(
                  fontFamily: 'Spectral-Regular',
                  fontSize: 13,
                  color: Colors.black,
                ),
              ),
            ),
            SizedBox(height: 30),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                _buildEmployeeCard('assets/images/seohyeon.jpg', 'Seohyeon'),
                SizedBox(width: 50),
                _buildEmployeeCard('assets/images/hc.png', 'HC'),
                SizedBox(width: 50),
                _buildEmployeeCard('assets/images/yeeun.jpg', 'Yeeun'),
              ],
            ),
            SizedBox(height: 30),
            Align(
              alignment: Alignment.center,
              child: _buildEmployeeCard('assets/images/JY_image.jpg', 'mentor.JY'),
            ),
            SizedBox(height: 30),
            // 후원 버튼 추가
            Center(
              child: ElevatedButton(
                onPressed: _launchURL,
                style: ElevatedButton.styleFrom(
                  foregroundColor: Colors.white, backgroundColor: primarySwatch,  // 글자 색상 설정
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(20)
                  )
                ),
                child: Text(
                  '☕ Support our journey!',
                  style: TextStyle(
                    fontFamily: 'AbhayaLibre',
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmployeeCard(String imagePath, String name) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        CircleAvatar(
          radius: 40,
          backgroundImage: AssetImage(imagePath),
          backgroundColor: imagePath.isEmpty ? Colors.grey : null,  // 이미지가 없을 경우 회색 원으로 표시
        ),
        SizedBox(height: 8),
        Text(
          name,
          style: TextStyle(
            fontFamily: 'Spectral-Regular',
            fontSize: 8,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }
}