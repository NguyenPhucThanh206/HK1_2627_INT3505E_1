from flask import Flask
from model import db, Book, Category, Author
from route import books_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(books_bp)

with app.app_context():
    db.create_all()

    # Dữ liệu mẫu
    c1 = Category(name="Văn học", slug="van-hoc")
    c2 = Category(name="Khoa học", slug="khoa-hoc")
    a1 = Author(name="Nam Cao")
    db.session.add_all([c1, c2, a1])
    db.session.commit()

    books = [
        Book(
            title=f"Book {i}",
            isbn=f"ISBN-97800000{i:02d}",
            price_vnd=10000 + i * 2000,
            stock=i * 2,
            category_id=c1.id if i % 2 == 0 else c2.id,
            author_id=a1.id
        )
        for i in range(1, 15)
    ]
    db.session.add_all(books)
    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, port=5000)