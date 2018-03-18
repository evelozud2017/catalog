from flask import Flask, render_template, request, redirect
from flask import url_for, jsonify, flash
from flask import session as login_session
from flask import make_response
from sqlalchemy import create_engine, desc, asc
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from itemcatalog_dbsetup import Base, User, Category, Item
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response
import random
import string
import httplib2
import json
import requests


app = Flask(__name__)


CLIENT_ID = json.loads(
    open(
        'client_secrets.json', 'r'
    ).read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


#  Item Catalog App routes

#  Main page
@app.route('/')
@app.route('/catalog')
@app.route('/catalog/')
def showCategories():
    #  shows all categories and latest added items
    categories = session.query(Category).all()
    items = session.query(Item).order_by(desc(Item.create_date))
    if 'username' not in login_session:
        return render_template(
            'publiccatalog.html',
            categories=categories,
            items=items)
    else:
        return render_template(
            'catalog.html',
            categories=categories,
            items=items,
            user_id=login_session['user_id'])


@app.route('/catalog/<int:category_id>')
def showItemsByCategory(category_id):
    #  show the items in the category selected
    category = session.query(Category).filter_by(id=category_id).one()
    categories = session.query(Category).all()
    items = session.query(Item).filter_by(
        cat_id=category_id).order_by(asc(Item.title)).all()
    if 'username' not in login_session:
        return render_template(
            'publiccatalog.html',
            categories=categories,
            items=items)
    else:
        return render_template(
            'catalogitems.html', category=category, categories=categories,
            items=items, user_id=login_session['user_id'])


@app.route('/catalog/<int:category_id>/<int:item_id>/')
def showItemDetail(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')

    item = session.query(Item).filter_by(id=item_id).one()
    return render_template(
        'itemdetail.html', item=item, user_id=login_session['user_id'])


@app.route('/catalog/add', methods=['GET', 'POST'])
def addItem():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newItem = Item(
                        title=request.form['title'],
                        description=request.form['description'],
                        cat_id=request.form['category_id'],
                        user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash("%s added." % newItem.title)
        return redirect(url_for('showCategories'))
    else:
        categories = session.query(Category).all()
        return render_template('additem.html', categories=categories)


@app.route(
    '/catalog/<int:category_id>/<int:item_id>/edit',
    methods=['GET', 'POST'])
def editItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')

    editedItem = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['title']:
            editedItem.title = request.form['title']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category_id']:
            editedItem.cat_id = request.form['category_id']
        session.add(editedItem)
        session.commit()
        flash("%s updated." % editedItem.title)
        return redirect(url_for('showCategories'))
    else:
        categories = session.query(Category).all()
        return render_template(
            'edititem.html', categories=categories, item=editedItem)


@app.route(
    '/catalog/<int:category_id>/<int:item_id>/delete',
    methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')

    itemToDelete = session.query(Item).filter(
        Item.id == item_id).filter(Item.cat_id == category_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("%s deleted." % itemToDelete.title)
        return redirect(url_for(
            'showItemsByCategory', category_id=category_id))
    else:
        return render_template('deleteitem.html', item=itemToDelete)


#  Credentials routes

#  Show login
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/logout')
def logout():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']

        flash("You have Successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in to begin with.")
        return redirect(url_for('showCategories'))


#  Login via Google login
@app.route('/gconnect', methods=['POST'])
def gconnect():
    #  Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    #  Obtain authorization code, now compatible with Python3
    code = request.get_data()

    try:
        #  Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    #  Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    #  Submit request, parse response - Python3 compatible
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    #  If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    #  Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    #  Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    #  Store the access token in the session for later use.
    login_session['provider'] = 'google'
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    #  Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['email']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    #  see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: '
    output += '150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    flash("you are now logged in as %s" % login_session['username'])
    return output


@app.route('/gdisconnect')
def gdisconnect():
    #  Only disconnect a connected user.
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
        #  For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


#  User Helper Functions

def createUser(login_session):
    newUser = User(
        username=login_session['username'],
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


#  JSON routes

#  Display all Categories
@app.route('/catalog/JSON')
def showCategoriesJSON():
    categories = session.query(Category).all()
    return jsonify(category=[i.serialize for i in categories])


#  Display all Items
@app.route('/catalogitems/JSON')
def showCategoryItemsJSON():
    items = session.query(Item).order_by(Item.cat_id)
    return jsonify(items=[i.serialize for i in items])


#  Display Items in a category
@app.route('/catalog/<int:category_id>/items/JSON')
def showItemsInCategoryJSON(category_id):
    items = session.query(Item).filter_by(cat_id=category_id).all()
    return jsonify(items=[i.serialize for i in items])


#  Main method
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
