import random
from pathlib import Path
from flask import Flask, abort, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'test.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class AuthorModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    quotes = db.relationship('QuoteModel', backref='author', lazy='select')

    def __init__(self, name):
        if name is not None:
            self.name = name

    def to_dict(self):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = str(getattr(self, column.name))
        return d

class QuoteModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(AuthorModel.id))
    text = db.Column(db.String(255), unique=False)

    def __init__(self, author, text):
        self.author_id = author.id
        self.text = text

    def to_dict(self):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = str(getattr(self, column.name))
        del d["author_id"]
        d["author"] = self.author.to_dict()
        return d

# AUTHORS API
@app.route('/authors')
def get_authors():
    authors = AuthorModel.query.all()
    if authors is None:
        abort(404, f"There is no any quote")
    return jsonify([author.to_dict() for author in authors])


@app.route('/authors/<int:author_id>')
def get_author_by_id(author_id):
    author = AuthorModel.query.get(author_id)
    if author is None:
        abort(404, f"Author with id={author_id} not found")
    return jsonify(author.to_dict())


@app.route('/authors/<int:author_id>', methods=['DELETE'])
def delete_author_by_id(author_id):
    author = AuthorModel.query.get(author_id)
    if author is None:
        abort(404, "Author not found")
    quotes = QuoteModel.query.filter(QuoteModel.author.has(name=author.name)).all()
    for quote in quotes:
        db.session.delete(quote)
    db.session.delete(author)
    db.session.commit()
    return jsonify(author.to_dict()), 200


@app.route('/authors', methods=['POST'])
def add_new_author():
    new_author = request.json
    author = AuthorModel(**new_author)
    db.session.add(author)
    db.session.commit()
    return jsonify(author.to_dict()), 201

@app.route('/authors/<int:id>', methods=['PUT'])
def change_author(id):
    return {}


# QUOTES API
@app.route('/author/<int:author_id>/quotes/<int:quote_id>')
def show_quote(author_id, quote_id):
    quote = QuoteModel.query.get(quote_id)
    if quote is None:
        abort(404, f"quote with id={qoute_id} not found")
    if quote.author_id != author_id:
        abort(404, f"Цитата с id={quote_id} принадлежит не автору с id={author_id}")
    return jsonify(quote.to_dict())


@app.route("/author/<int:author_id>/quotes")
def get_all_quotes_of_author(author_id):
    author = AuthorModel.query.get(author_id)
    if author is None:
        abort(404, "Author not found")
    quotes = QuoteModel.query.filter(QuoteModel.author.has(name=author.name)).all()
    return jsonify([quote.to_dict() for quote in quotes])

@app.route("/quotes/")
@app.route("/quotes")
def show_all_quotes():
    quotes = QuoteModel.query.all()
    if quotes is None:
        abort(404, f"There is no any quote")
    return jsonify([quote.to_dict() for quote in quotes])


@app.route("/author/<int:author_id>/quotes/<int:quote_id>", methods=['DELETE'])
def delete(author_id, quote_id):
    quote = QuoteModel.query.get(quote_id)
    if quote is None:
        abort(404, "Quote not found")
    if quote.author_id != author_id:
        abort(404, f"Цитата с id={quote_id} принадлежит не автору с id={author_id}")
    db.session.delete(quote)
    db.session.commit()
    # FIXME: Цитату находит и удаляет, но крашится при возврате цитаты из-за DetachedInstanceError:
    #  Parent instance <QuoteModel at 0x7f24b4336d90> is not bound to a Session; lazy load operation
    #  of attribute 'author' cannot proceed
    return jsonify(quote.to_dict()), 200


@app.route("/author/<int:author_id>/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(author_id, quote_id):
    new_data = request.json
    quote = QuoteModel.query.get(quote_id)
    author = AuthorModel.query.get(author_id)
    new_author = None
    if new_data.get("author"):
        new_author = AuthorModel(**new_data.get("author"))
    author = new_author or author
    if new_data.get("text"):
        new_text = new_data.get("text")
    if quote is None or author is None:
        abort(404, "No such author or quote")
    quote.author = author
    quote.text = new_text or quote.text
    db.session.commit()
    return jsonify(quote.to_dict()), 200


@app.route("/author/<int:author_id>/quotes", methods=['POST'])
def create_quote(author_id):
    new_quote = request.json
    author = AuthorModel.query.get(author_id)
    if author is None:
        abort(404, 'There is no such author')
    try:
        q = QuoteModel(author, new_quote["text"])
    except KeyError:
        abort(400, "There must be author and text for quote")
    db.session.add(q)
    db.session.commit()
    return jsonify(q.to_dict()), 201


@app.route("/quotes/random")
def show_random_quote():
    # TODO: Перейти на ORM
    quote = random.choice(quotes)
    return jsonify(quote)


if __name__ == "__main__":
    app.run(debug=True)
