class Book {
  final String isbn;
  final String title;
  final String? author;
  final String? publisher;
  final String? category;
  final String? imageUrl;
  final String? description;
  final String? keySentences;

  Book({
    required this.isbn,
    required this.title,
    this.author,
    this.publisher,
    this.category,
    this.imageUrl,
    this.description,
    this.keySentences,
  });

  // JSON 데이터를 Dart 객체로 변환
  factory Book.fromJson(Map<String, dynamic> json) {
    return Book(
      isbn: json['isbn'],
      title: json['title'],
      author: json['author'],
      publisher: json['publisher'],
      category: json['category'],
      imageUrl: json['image_url'],
      description: json['description'],
      keySentences: json['key_sentences'],
    );
  }
}