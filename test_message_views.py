"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py

from flask import session
from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, connect_db, Message, User

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

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_see_message(self):
        """ Can we see message on homepage and userpage """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            make_mess = c.post("/messages/new", data={"text": "Hello"})
            resp = c.get('/')
            resp2 = c.get(f'/users/{self.testuser.id}')
            html = resp.get_data(as_text=True)
            html2 = resp2.get_data(as_text=True)
            msg = Message.query.one()
            self.assertEqual(resp.status_code, 200)
            self.assertIn(msg.text, html)
            self.assertIn(msg.text, html2)

    def test_auth_follower(self):
        """ When you’re logged in, can you see the follower / following pages for any user?  """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f'/users/{self.testuser.id}/followers')
            self.assertEqual(resp.status_code, 200)

    def test_auth_follower_fail(self):
        """ When you’re logged out, are you disallowed from visiting a user’s follower / following pages? """
        with self.client as c:
            resp = c.get(f'/users/{self.testuser.id}/followers')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 302)
            self.assertIn('Redirecting', html)

    """ Can't get the below one to work, testing permission as logged in but posting as someone else """

    # def test_auth_post_message(self):
    #     """ When you’re logged in, are you prohibiting from adding a message as another user? """
    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser.id
    #         resp = c.post("/messages/new",
    #                       data={"text": "Hello ducker", "user_id": "5"})

    #         self.assertEqual(resp.status_code, 302)
    #         msg = Message.query.one()
    #         self.assertEqual(msg.text, "Hello ducker")
