"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app
import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Follows

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


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr(self):
        """Does repr return what you want"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()
        reppr = f"<User #{u.id}: {u.username}, {u.email}>"
        # User repr should be as above
        self.assertEqual(
            reppr, str(u))

    def test_is_following(self):
        """ Does is_following successfully detect when user1 is following user2? """
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test2.com",
            username="test2user",
            password="HASHED_PASSWORD"
        )

        db.session.add_all([u, u2])
        db.session.commit()

        follow = Follows(
            user_following_id=u.id,
            user_being_followed_id=u2.id
        )

        db.session.add(follow)
        db.session.commit()

        self.assertTrue(u.is_following(u2))

    def test_is_not_following(self):
        """ Does is_following successfully detect when user1 is NOT following user2? """
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test2.com",
            username="test2user",
            password="HASHED_PASSWORD"
        )

        db.session.add_all([u, u2])
        db.session.commit()

        self.assertFalse(u.is_following(u2))

    def test_is_followed_by(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?  """
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test2.com",
            username="test2user",
            password="HASHED_PASSWORD"
        )

        db.session.add_all([u, u2])
        db.session.commit()

        follow = Follows(
            user_following_id=u.id,
            user_being_followed_id=u2.id
        )

        db.session.add(follow)
        db.session.commit()

        self.assertTrue(u2.is_followed_by(u))

    def test_is_not_followed_by(self):
        """ Does is_followed_by successfully detect when user1 is not followed by user2? """
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test2.com",
            username="test2user",
            password="HASHED_PASSWORD"
        )

        db.session.add_all([u, u2])
        db.session.commit()

        self.assertFalse(u2.is_followed_by(u))

    def test_user_create(self):
        """ Does User.create successfully create a new user given valid credentials? """
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()

        self.assertTrue(u.id)

    "cant get this one to work. I get the failure in command line but not sure how to code it here"

    # def test_user_create_fail(self):
    #     """ Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?  """
    #     try:
    #         u = User.signup(
    #             email="test@test.com",
    #             username="testuser",
    #             password="HASHED_PASSWORD",
    #             image_url=User.image_url.default.arg,
    #         )
    #         u2 = User.signup(
    #             email="test2@test2.com",
    #             username="test2user",
    #             password="HASHED_PASSWORD",
    #             image_url=User.image_url.default.arg,

    #         )

    #         u3 = User.signup(
    #             email="test@test.com",
    #             username="testuser",
    #             password="HASHED_PASSWORD",
    #             image_url=User.image_url.default.arg,
    #         )

    #         db.session.commit()

    #     except IntegrityError:
    #         self.assertFalse(u3.id)

    def test_user_authenticate_true(self):
        """ Does User.authenticate successfully return a user when given a valid username and password? """
        password_test = "HASHED_PASSWORD"
        user = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url=User.image_url.default.arg,
        )
        db.session.commit()
        usertest = User.authenticate(user.username,
                                     password_test)
        self.assertTrue(usertest)

    def test_username_false(self):
        """ Does User.authenticate fail to return a user when the username is invalid? """
        password_test = "HASHED_PASSWORD"
        user = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url=User.image_url.default.arg,
        )
        db.session.commit()
        usertest = User.authenticate('testfaker',
                                     password_test)
        self.assertFalse(usertest)

    def test_pw_invaled(self):
        """ Does User.authenticate fail to return a user when the password is invalid? """
        password_test = "WRONG_PASSWORD"
        user = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url=User.image_url.default.arg,
        )
        db.session.commit()
        usertest = User.authenticate(user.username,
                                     password_test)
        self.assertFalse(usertest)
