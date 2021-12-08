import random
from pathlib import Path
from flask import Flask, abort, jsonify, request
from flask_sqlalchemy import SQLAlchemy

BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'test.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
KEYS = ("id", "author", "text")

# quotes = [
#    {
#        "id": 1,
#        "author": "Rick Cook",
#        "text": "Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает."
#    },
#    {
#        "id": 2,
#        "author": "Waldi Ravens",
#        "text": "Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках."
#    },
#    {
#        "id": 3,
#        "author": "Mosher’s Law of Software Engineering",
#        "text": "Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили."
#    },
#    {
#        "id": 4,
#        "author": "Yoggi Berra",
#        "text": "В теории, теория и практика неразделимы. На практике это не так."
#    },
#
# ]

# quotes = execute_read_query(connection, "SELECT * FROM quotes")

db = SQLAlchemy(app)

class QuoteModel(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   author = db.Column(db.String(32), unique=False)
   text = db.Column(db.String(255), unique=False)

   def __init__(self, author, text):
       self.author = author
       self.text = text

   def __repr__(self):
       return f"a:{self.author}, q:{self.text[:15]}"

   def to_dict(self):
       return {
           "id": self.id,
           "author": self.author,
           "text": self.text,
       }

@app.route('/quotes/<int:id>')
def show_quote(id):
    quote = QuoteModel.query.get(id)
    if quote is None:
        abort(404, f"quote with id={id} not found")
    return jsonify(quote.to_dict())


@app.route("/quotes/")
@app.route("/quotes")
def show_all_quotes():
    quotes = QuoteModel.query.all()
    if quotes is None:
        abort(404, f"There is no any quote")
    return jsonify([quote.to_dict() for quote in quotes])


@app.route("/quotes/<int:id>", methods=['DELETE'])
def delete(id):
    quote = QuoteModel.query.get(id)
    if quote is None:
        abort(404, "Quote not found")
    db.session.delete(quote)
    db.session.commit()
    return jsonify(quote.to_dict())

@app.route("/quotes/<int:id>", methods=['PUT'])
def edit_quote(id):
   new_data = request.json
   # for quote in quotes:
   #     if quote["id"] == id:
   #         if new_data.get("author"):
   #             quote["author"] = new_data["author"]
   #         if new_data.get("text"):
   #             quote["text"] = new_data["text"]
   #         return jsonify(quote), 200
   quote = QuoteModel.query.get(id)
   if quote is None:
       abort(404, f"quote with id={id} not found")
   quote.author = new_data["author"] if "author" in new_data.keys() else quote.author
   quote.text = new_data["text"] if "text" in new_data.keys() else qoute.text
   db.session.commit()
   return jsonify(quote.to_dict())



@app.route("/quotes", methods=['POST'])
def create_quote():
    new_quote = request.json
    try:
        q1 = QuoteModel(new_quote["author"], new_quote["text"])
    except KeyError:
        abort(400, "There must be author and text for quote")
    db.session.add(q1)
    db.session.commit()
    return jsonify(q1.to_dict()), 201



@app.route("/quotes/random")
def show_random_quote():
    quote = random.choice(quotes)
    return jsonify(quote)




if __name__ == "__main__":
   app.run(debug=True)
