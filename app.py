from flask import Flask, abort, jsonify
import random


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

quotes = [
   {
       "id": 1,
       "author": "Rick Cook",
       "text": "Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает."
   },
   {
       "id": 2,
       "author": "Waldi Ravens",
       "text": "Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках."
   },
   {
       "id": 3,
       "author": "Mosher’s Law of Software Engineering",
       "text": "Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили."
   },
   {
       "id": 4,
       "author": "Yoggi Berra",
       "text": "В теории, теория и практика неразделимы. На практике это не так."
   },

]


@app.route("/")
def hello_world():
   return "Hello, World!"

about_me = {
   "name": "Евгений",
   "surname": "Юрченко",
   "email": "eyurchenko@specialist.ru"
}

@app.route('/quotes/<int:quote_id>')
def show_quote(quote_id):
    for quote in quotes:
        if quote["id"] == quote_id:
            return jsonify(quote)
    abort(404)

@app.route("/quotes/")
@app.route("/quotes")
def show_all_quotes():
    return jsonify(quotes)

@app.route("/quotes/count")
def show_num_of_qoutes():
    return {"number": len(quotes)}

@app.route("/quotes/random")
def show_random_quote():
    quote = random.choice(quotes)
    return jsonify(quote)

@app.route("/about")
def about():
   return about_me


if __name__ == "__main__":
   app.run(debug=True)
