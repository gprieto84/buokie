from appdir.forms import RegisterForm, LoginForm, SearchForm, ReviewForm
from flask import render_template, redirect, url_for, flash, session, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from appdir import app, db
from datetime import datetime
import requests


@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/register", methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db.execute("INSERT INTO users (username, password_hash, email, first_name, last_name) values (:username, :password_hash, :email, :first_name, :last_name)"
            ,{"username":form.username.data, "password_hash":generate_password_hash(form.password.data)
            ,"email":form.email.data,"first_name":form.first_name.data,"last_name":form.last_name.data})
        db.commit()
        flash("User created")
        return redirect(url_for("login"))
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET','POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.execute("SELECT * FROM users WHERE username=:username",{"username":form.username.data}).fetchone()
        if user is None or not check_password_hash(user.password_hash, form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        session['user_id'] = user.id
        session['user_name'] = user.first_name
        return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_name',None)
    session.pop('user_id',None)
    return redirect(url_for('index'))

@app.route("/search", methods=['GET','POST'])
def search():
    if 'user_id' in session:
        form = SearchForm()
        if form.validate_on_submit():
            books = db.execute("SELECT * FROM books WHERE isbn LIKE ('%' || :isbn || '%') OR title LIKE ('%' || :title || '%') OR author LIKE ('%' || :author || '%')",
                {"isbn": form.search.data,"title": form.search.data,"author": form.search.data}).fetchall()
            return render_template('search.html',  form=form, books=books)
        return render_template('search.html', form= form)

@app.route("/book/<book_id>", methods=['GET','POST'])
def book(book_id):
    if 'user_id' in session:
        book = db.execute("SELECT * FROM books WHERE id=:id",{"id":book_id}).fetchone()
        try:
            res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "P3rKT05i2aMQ36S6NTNlZg", "isbns": book.isbn})
            work_ratings_count = res.json()['books'][0]['work_ratings_count']
            avg_rating = res.json()['books'][0]['average_rating']
        except requests.exceptions.Timeout as e:
            avg_rating = 'Time out from Goodreads'
            work_ratings_count = 'Time out from Goodreads'
        except requests.exceptions.TooManyRedirects as e:
            avg_rating = 'Too many redirects from GoodReads'
            work_ratings_count = 'Time out from Goodreads'
        except requests.exceptions.RequestException as e:
            avg_rating = 'General Exception from GoodReads'
            work_ratings_count = 'Time out from Goodreads'

        form = ReviewForm()
        if form.validate_on_submit():
            review = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id",{"user_id":session['user_id'],"book_id":book_id}).fetchone()
            if review is None:
                db.execute("INSERT INTO reviews (star, review, book_id, user_id) VALUES (:star, :review, :book_id,:user_id)",
                    {"star":form.star.data,"review":form.review.data,"book_id":book_id,"user_id":session['user_id']})
                db.commit()
                flash("Review submitted")
            else:
                flash("You have already submitted a review for this book.")

        reviews = db.execute("SELECT review, star, title, author, username, to_char(timestamp, 'HH24:MI:SS') AS created_on  "+
                            "FROM reviews INNER JOIN books ON (reviews.book_id = books.id) " + 
                            "INNER JOIN users ON (reviews.user_id = users.id) "+
                            "WHERE book_id = :book_id",{"book_id":book_id}).fetchall()
        return render_template('book.html', book=book, avg_rating=avg_rating, work_ratings_count=work_ratings_count, reviews=reviews, form = form)

@app.route("/api/<isbn>")
def book_api(isbn):
    """Return details about a single book."""

    # Make sure book exists.
    
    book = db.execute("SELECT * FROM books where isbn=:isbn",{"isbn":isbn}).fetchone()

    if book is None:
        return jsonify({"error": "Invalid book_id"}), 422

    book_api = db.execute("SELECT title, author, year, isbn, COALESCE(a.review_count,0) as review_count, round(COALESCE(a.average_score,0),2) as average_score " +
        " FROM books LEFT OUTER JOIN  (SELECT book_id, COUNT(1) AS review_count, AVG(star) AS average_score FROM reviews GROUP BY book_id) a ON (books.id = a.book_id) " +
        " WHERE isbn = :isbn",{"isbn":isbn}).fetchone()
    print(book_api)
    return jsonify({
            "title": book_api.title,
            "author": book_api.author,
            "year": book_api.year,
            "review_count": book_api.review_count,
            "average_score": str(book_api.average_score)
          })
