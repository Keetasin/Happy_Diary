from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

# Initialize SQLAlchemy database instance
db = SQLAlchemy()

# Define the name of the database file
DB_NAME = "database.db"

# Function to create the Flask application
def create_app():
    # Create Flask application instance
    app = Flask(__name__)
    
    # Configure Flask app settings
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    
    # Initialize SQLAlchemy with the Flask app
    db.init_app(app)

    # Import blueprints for different parts of the application
    from .views import views
    from .auth import auth

    # Register blueprints with the app and specify URL prefixes
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Import User model from models module
    from .models import User 

    # Create the database if it does not exist
    create_database(app)

    # Initialize Flask-Login for user authentication
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # Set the login view
    login_manager.init_app(app)

    # Function to load a user by ID for Flask-Login
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

# Function to create the database
def create_database(app):
    if not path.exists('website/' + DB_NAME):
        # Create all tables in the database if it does not exist
        with app.app_context():
            db.create_all()
        print('Created Database!')  # Print confirmation message
