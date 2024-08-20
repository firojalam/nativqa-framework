from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sentences.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define countries, locations, languages, and topics
countries = ['Country1', 'Country2', 'Country3']
locations = {
    'Country1': ['Location1', 'Location2'],
    'Country2': ['Location3', 'Location4'],
    'Country3': ['Location5', 'Location6']
}
languages = ['Language1', 'Language2', 'Language3']
topics = ['Topic1', 'Topic2', 'Topic3']

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
        sentence = request.form.get('sentence')

        if sentence:
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(username=username, email=email)
                db.session.add(user)
                db.session.commit()

            new_sentence = Sentence(country=country, location=location, language=language, topic=topic, sentence_text=sentence, user_id=user.id)
            db.session.add(new_sentence)
            db.session.commit()

        return redirect(url_for('index'))

    sentences = Sentence.query.all()
    return render_template('index.html', countries=countries, locations=locations, languages=languages, topics=topics, sentences=sentences)

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

if __name__ == '__main__':
    app.run(debug=True)
