import os
from flask import Flask
from flask_login import LoginManager

from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy and LoginManager without an app
db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your secret key'
    app.config['DEBUG'] = True

    # Configure the SQLite database URI
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
        os.path.join(basedir, 'database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the SQLAlchemy and LoginManager with the app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    with app.app_context():
        from models.user_model import User
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints or import routes here
    from . import routes
    app.register_blueprint(routes.bp)

    return app


# ----------------------------- END LOGIN -------------------------------------------------
app = create_app()
if __name__ == '__main__':
    app.run(debug=True)
