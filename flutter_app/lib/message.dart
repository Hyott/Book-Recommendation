class Message {
  final String isbn;
  final String sentence;
  // final List<String> hashtags;

  Message({
    required this.isbn,
    required this.sentence,
    // required this.hashtags,
  });

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      isbn: json['isbn'],
      sentence: json['sentence'],
      // hashtags: List<String>.from(json['hashtags']),
    );
  }
}