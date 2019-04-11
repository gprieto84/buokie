# Project 1

Web Programming with Python and JavaScript


Getting Started
+ The project consists of book review page called "BUOKIE"
+ Explanation can be found on: https://you

Functionality:
+ Login a user
+ Register a user: Includes email format validation, password min 8 characters restriction.
+ Search books
+ Obtain average rating and number of rating from Goodreads, for each book
+ Visualize buokie reviews
+ Create buokie reviews

Additional Libraries used:
+ Flask Session: In order to manage database sessions
+ Flask-WTF: Used for forms and validators
+ Flask-Bootstrap: Used for styling

Structure:
+ appdir/
    + templates/
        + base.html : page layout base (All pages extends from this one)
        + book.html : page to visualize books and give reviews
        + index.html : Welcome page
        + login.html : Login page
        + register.html : Register page
        + search.html: Search functionality page
    + __init__.py : It creates the Flask app, and loads configuration and database
    + forms.py : Forms definition and validations
    + routes.py : The routes and logic for all the pages
    + import.py : Program that takes the books.csv document and load it into the database

Database tables
+ books
+ users 
+ reviews

Aknowledgement:
+ http://getbootstrap samples
+ https://blog.miguelgrinberg.com/
