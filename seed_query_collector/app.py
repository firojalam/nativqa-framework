from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sentences.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Define countries, locations, languages, and topics
# countries = ['Country1', 'Country2', 'Country3']
# locations = {
#     'Country1': ['Location1', 'Location2'],
#     'Country2': ['Location3', 'Location4'],
#     'Country3': ['Location5', 'Location6']
# }
# languages = ['Language1', 'Language2', 'Language3']
topics = ['Animals', 'Business', 'Cloths', 'Education', 'Events', 'Food&Drinks', 'General', 'Geography',
          'Immigration Related', 'Language', 'Literature', 'Names', 'Plants', 'Religion', 'Sports&Games',
          'Tradition', 'Travel', 'Weather', 'Others']

# Database model for User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    sentences = db.relationship('Sentence', backref='user', lazy=True)

# Database model for Sentence
class Sentence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    language = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    sentence_text = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Create the database tables before the first request
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        country = request.form.get('country')
        location = request.form.get('location')
        language = request.form.get('language')
        topic = request.form.get('topic')
        #sentence = request.form.get('sentence')

        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(username=username, email=email)
            db.session.add(user)
            db.session.commit()

        if topic == "Others":
            topic = request.form.get('add_topic')
        num_sent = int(request.form.get('num_sent'))

        for i in range(1, num_sent+1):
            sentence = request.form.get(f'sentence_{i}')
            if sentence:
                session["user_id"] = user.id

                # data = {'country': country, 'location': location, 'lang': language, 'topic':topic, 'sent': sentence}
                new_sentence = Sentence(country=country, location=location, language=language, topic=topic, sentence_text=sentence, user_id=user.id)
                # print(data)
                db.session.add(new_sentence)
                db.session.commit()

        return redirect(url_for('index'))

    sentences = Sentence.query.all()
    return render_template('index.html', topics=topics, sentences=sentences)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_sentence(id):
    sentence = Sentence.query.get_or_404(id)

    if request.method == 'POST':
        edited_sentence_text = request.form.get('edited_sentence')
        if edited_sentence_text:
            sentence.sentence_text = edited_sentence_text
            db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit.html', sentence=sentence)

@app.route('/view', methods=['GET'])
def view_sentence():
    id = None
    if 'user_id' in session:
        id = session['user_id']
    sentences = None
    if id:
        sentences = Sentence.query.filter_by(user_id=id).all()
        # sentences = result.all()
    return render_template('view.html', sentences=sentences)

@app.route('/contributors', methods=['GET'])
def contributor():
    users = User.query.all()
    return render_template('contributors.html', users=users)


if __name__ == '__main__':
    app.run(debug=True)
