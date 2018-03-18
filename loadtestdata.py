import contextlib

from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy.orm import sessionmaker
from itemcatalog_dbsetup import Base, User, Category, Item
import json
from pprint import pprint

engine = create_engine('sqlite:///itemcatalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


#  Delete records from tables
session.query(Item).delete()
session.commit()

session.query(Category).delete()
session.commit()

session.query(User).delete()
session.commit()


#  Populate test data into tables

#  Create a default user
test_user = User(
    username="mimoy",
    email="mimoy@test.com",
    picture='https://test.com/pic.png')
session.add(test_user)
session.commit()

test_user_id = session.query(User.id).limit(1)


#  Insert Music Genre into Category and Artists into Item table from json file
with open('testdata.json') as data_file:
    data = json.load(data_file)
    for category in data['categories']:
        category_name = category['name']
        test_category = Category(name=category_name, user_id=test_user_id)
        session.add(test_category)
        session.commit()

        test_category_id = session.query(Category.id).filter_by(
            name=category_name).limit(1)
        if 'items' in category:
            for item in category['items']:
                item_title = item['title']
                item_description = item['description']
                test_item = Item(
                    title=item_title,
                    description=item_description,
                    cat_id=test_category_id,
                    user_id=test_user_id)
                session.add(test_item)
                session.commit()


#  Print results
categories = session.query(Category).all()
for category in categories:
    print "id: %d" % category.id
    print "Category: " + category.name
    print "created_date: %s" % category.create_date
    print "update_date: %s" % category.update_date
    print "user_id: %s" % category.user_id


items = session.query(Item).all()
for catItem in items:
    print "Item id: %s" % catItem.id
    print "title: " + catItem.title
    print "description: " + catItem.description
    print "cat_id: %s" % catItem.cat_id
    print "user_id: %s" % catItem.user_id
