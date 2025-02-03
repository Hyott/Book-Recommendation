class Message {
  final String isbn;
  final String message;
  final List<String> hashtags;

  Message({
    required this.isbn,
    required this.message,
    required this.hashtags,
  });

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      isbn: json['isbn'],
      message: json['message'],
      hashtags: List<String>.from(json['hashtags']),
    );
  }
}