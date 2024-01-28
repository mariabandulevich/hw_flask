from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class User(db.Model):  # создание базы данных
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.Text)
    age = db.Column(db.Integer)
    gender = db.Column(db.Text)


class Questions(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)


class Answers(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    q1 = db.Column(db.Integer)
    q2 = db.Column(db.String)
    q3 = db.Column(db.String)
    q4 = db.Column(db.String)
    q5 = db.Column(db.Text)


@app.route('/')  # отображение главной страницы
def index():
    return render_template('index.html')


@app.route('/form')  # перенаправление на страницу с опросом
def form():
    return redirect(url_for('question_page'))


@app.route('/questions')  # получение вопросов из базы данных и отображение на странице с опросом
def question_page():
    questions = Questions.query.all()
    return render_template(
        'questions.html',
        questions=questions
    )


@app.route('/process', methods=['POST'])  # получение и обработка данных после заполнения теста
def answer_process():
    if not request.form:  # если форма не отправлена, то пользователь перенаправляется на страницу с опросом
        return redirect(url_for('question_page'))
    city = request.form.get('city')  # извлечение данных из формы
    age = request.form.get('age')
    gender = request.form.get('gender')
    user = User(
        city=city,
        age=age,
        gender=gender,
    )
    db.session.add(user)
    db.session.commit()  # сохранение изменений в базе данных
    db.session.refresh(user)  # обновление объекта user
    q1 = request.form.get('q1')  # извлечение данных из опроса
    q2 = request.form.get('q2')
    q3 = request.form.get('q3')
    q4 = request.form.get('q4')
    q5 = request.form.get('q5')
    answer = Answers(id=user.id, q1=q1, q2=q2, q3=q3, q4=q4, q5=q5)
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('stats'))  # после прохождения теста пользователя перенаправляют на страницу со статистикой


@app.route('/stats')  # отображение статистики по вопросам
def stats():
    all_info = {}  # словарь для отображения статистики на отдельной странице
    age_stats = db.session.query(
        func.avg(User.age),  # нахождение  среднего возраста
        func.min(User.age),  # нахождение  минимального возраста
        func.max(User.age)   # нахождение  максимального возраста
    ).one()
    all_info['age_mean'] = age_stats[0]  # добавление данных о возрасте в словарь
    all_info['age_min'] = age_stats[1]
    all_info['age_max'] = age_stats[2]
    all_info['total_count'] = User.query.count()  # вычисление общего количества пользователей
    # вычисление среднего значения ответа на первый вопрос
    all_info['q1_mean'] = db.session.query(func.avg(Answers.q1)).one()[0]
    # вычисление количества правильных ответов на 5-ый вопрос
    all_info['q5_correct'] = Answers.query.filter_by(q5='смелый').count()
    return render_template('stats.html', all_info=all_info)  # передача данных из словаря на страницу со статистикой


if __name__ == '__main__':
    app.run(debug=True)
