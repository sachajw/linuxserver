# CRUD Operations
from database_setup import Base, User, Book
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   flash,
                   jsonify)
from flask_wtf import FlaskForm
from wtforms import (StringField,
                     SubmitField,
                     PasswordField,
                     BooleanField,
                     IntegerField,
                     FloatField)
from wtforms.validators import (DataRequired,
                                Length,
                                Email,
                                EqualTo,
                                ValidationError)
from flask_bootstrap import Bootstrap
from flask import session as login_session
from sqlalchemy import Column, ForeignKey, Integer, String
from flask_sqlalchemy import SQLAlchemy
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
app = Flask(__name__)


# Create session and connect to DB
engine = create_engine('postgresql+psycopg2://catalog:catalog@localhost/bookcatalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Book Catalogue"

# CSRF Config
app.config.update(
    SECRET_KEY='a random string',
    SQLALCHEMY_DATABASE_URI=('postgresql+psycopg2://catalog:catalog@localhost/bookcatalog'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

# App configuration
db = SQLAlchemy()
bootstrap = Bootstrap(app)
db.init_app(app)


# Forms are defined here
class EditBookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    genre = StringField('Genre', validators=[DataRequired()])
    format = StringField('Format', validators=[DataRequired()])
    image = StringField('Image')
    num_pages = StringField('Pages', validators=[DataRequired()])
    pub_date = StringField('Publication Date', validators=[DataRequired()])
    pub_name = StringField('Publisher Name', validators=[DataRequired()])
    submit = SubmitField('Update')


class CreateBookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    genre = StringField('Genre', validators=[DataRequired()])
    format = StringField('Format', validators=[DataRequired()])
    image = StringField('Image')
    num_pages = IntegerField('Pages', validators=[DataRequired()])
    pub_date = IntegerField('Publication Year', validators=[DataRequired()])
    pub_name = StringField('Publisher Name', validators=[DataRequired()])
    submit = SubmitField('Create')


class DeleteBookForm(FlaskForm):
    delete = SubmitField('Delete')


# Routes begin
# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        'print' "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # Add provider to login session
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px;' \
              'height: 300px;' \
              'border-radius: 150px;' \
              '-webkit-border-radius: 150px;' \
              '-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    'print' "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current users token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON API to view book Information
@app.route('/JSON')
def display_booksJSON():
    books = session.query(Book).all()
    return jsonify(book=[b.serialize for b in books])
# JSON APIs end


# Show all books
@app.route('/')
def display_books():
    books = session.query(Book).all()
    return render_template('home.html', books=books)


@app.route('/create', methods=['GET', 'POST'])
def add_new_book():
    if 'username' not in login_session:
        return redirect('/login')
    form = CreateBookForm()
    if form.validate_on_submit():
        book = Book(title=form.title.data,
                    author=form.author.data,
                    genre=form.genre.data,
                    format=form.format.data,
                    image=form.image.data,
                    num_pages=form.num_pages.data,
                    pub_date=form.pub_date.data,
                    pub_name=form.pub_name.data)
        book.user_id = login_session["user_id"]
        session.add(book)
        session.commit()
        flash('book added successfully')
        return redirect(url_for('display_books'))
    return render_template('create_book.html', form=form)


@app.route('/book/delete/<book_id>', methods=['GET', 'POST'])
def delete_book(book_id):
    book = session.query(Book).filter_by(id=book_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if book.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this book. Please create your own book if you want to delete.');}</script><body onload='myFunction()'>"
    form = DeleteBookForm()
    if form.validate_on_submit():
        session.delete(book)
        session.commit()
        flash('book deleted successfully')
        return redirect(url_for('display_books'))
    return render_template('delete_book.html', form=form)


@app.route('/book/edit/<book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    editedbook = session.query(Book).filter_by(id=book_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedbook.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this book. Please create your own book.');}</script><body onload='myFunction()'>"
    form = EditBookForm(obj=editedbook)
    if form.validate_on_submit():
        editedbook.title = form.title.data
        editedbook.author = form.author.data
        editedbook.genre = form.genre.data
        editedbook.format = form.format.data
        editedbook.image = form.image.data
        editedbook.num_pages = form.num_pages.data
        editedbook.pub_date = form.pub_date.data
        editedbook.pub_name = form.pub_name.data
        session.add(editedbook)
        session.commit()
        flash('book edited successfully')
        return redirect(url_for('display_books'))
    return render_template('edit_book.html', form=form)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully logged out.")
        return redirect(url_for('display_books'))
    else:
        flash("You were not logged in")
        return redirect(url_for('display_books'))

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
