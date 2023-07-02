import unittest
from app import app, db
from app.models import User, Url

class TestRoutes(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_dashboard(self):
        user = User(username='testuser', password_hash='password')
        db.session.add(user)
        db.session.commit()
        with self.app.session_transaction() as session:
            session['user_id'] = user.id
        response = self.app.get('/dashboard')
        self.assertEqual(response.status_code, 200)

    def test_about(self):
        response = self.app.get('/about')
        self.assertEqual(response.status_code, 200)

    def test_history(self):
        user = User(username='testuser', password_hash='password')
        db.session.add(user)
        db.session.commit()
        with self.app.session_transaction() as session:
            session['user_id'] = user.id
        response = self.app.get('/history')
        self.assertEqual(response.status_code, 200)

    def test_redirect_link(self):
        url = Url(long_url='http://www.google.com', short_url='abc123', user_id=1)
        db.session.add(url)
        db.session.commit()
        response = self.app.get('/abc123')
        self.assertEqual(response.status_code, 302)

    def test_generate_qr_code_link(self):
        user = User(username='testuser', password_hash='password')
        db.session.add(user)
        db.session.commit()
        url = Url(long_url='http://www.google.com', short_url='abc123', user_id=user.id)
        db.session.add(url)
        db.session.commit()
        with self.app.session_transaction() as session:
            session['user_id'] = user.id
        response = self.app.get('/abc123/qr_code')
        self.assertEqual(response.status_code, 200)

    def test_delete(self):
        user = User(username='testuser', password_hash='password')
        db.session.add(user)
        db.session.commit()
        url = Url(long_url='http://www.google.com', short_url='abc123', user_id=user.id)
        db.session.add(url)
        db.session.commit()
        with self.app.session_transaction() as session:
            session['user_id'] = user.id
        response = self.app.get('/abc123/delete')
        self.assertEqual(response.status_code, 302)

    def test_update(self):
        user = User(username='testuser', password_hash='password')
        db.session.add(user)
        db.session.commit()
        url = Url(long_url='http://www.google.com', short_url='abc123', user_id=user.id)
        db.session.add(url)
        db.session.commit()
        with self.app.session_transaction() as session:
            session['user_id'] = user.id
        response = self.app.get('/abc123/edit')
        self.assertEqual(response.status_code, 200)

    def test_analytics(self):
        user = User(username='testuser', password_hash='password')
        db.session.add(user)
        db.session.commit()
        url = Url(long_url='http://www.google.com', short_url='abc123', user_id=user.id)
        db.session.add(url)
        db.session.commit()
        with self.app.session_transaction() as session:
            session['user_id'] = user.id
        response = self.app.get('/abc123/analytics')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()