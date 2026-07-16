from models import User

def test_user_password_hash():
    user = User(username="bob")
    user.set_password("password123")

    assert user.password_hash != "password123"
    assert user.check_password("password123")
    assert not user.check_password("a-nice-password")

