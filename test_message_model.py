"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app
import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserMessageTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        self.user_id = u.id
        self.u = u

        self.client = app.test_client()

    def test_test(self):
        self.assertTrue(self.user_id)

    def test_message_text(self):
        """ Test message model text """
        mess = Message(
            text='test1 test2',
            user_id=self.user_id
        )
        db.session.add(mess)
        db.session.commit()

        self.assertEqual(mess.text, 'test1 test2')
        self.assertEqual(mess.user_id, self.user_id)

    def test_multiple_message_assignment(self):
        """ Test multiple message assigned to one user """
        mess = Message(
            text='test1 test2',
            user_id=self.user_id
        )

        mess2 = Message(
            text='test3 test4',
            user_id=self.user_id
        )

        db.session.add_all([mess, mess2])
        db.session.commit()

        self.assertEqual(len(self.u.messages), 2)

    def test_liked_message(self):
        """ test like message model """
        mess = Message(
            text='test1 test2',
            user_id=self.user_id
        )
        u2 = User(
            email="test2@test2.com",
            username="test2user",
            password="HASHED_PASSWORD"
        )
        db.session.add_all([mess, u2])
        db.session.commit()

        like = Likes(
            user_id=u2.id,
            message_id=mess.id
        )

        db.session.add(like)
        db.session.commit()

        self.assertTrue(like.id)
        """ Making sure like shows up within user like """
        self.assertIn(str(mess.id), str(u2.likes))
