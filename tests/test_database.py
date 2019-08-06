from flaskr.database import db_session, init_db
from flaskr.models import User


def test_add():
    init_db()
    u = User('admin', 'admin@localhost')
    db_session.add(u)
    db_session.commit()


def test_query():
    init_db()
    print(User.query.all())
    print(User.query.filter(User.name == 'admin').first())
