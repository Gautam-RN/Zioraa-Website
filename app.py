from flask import Flask, render_template
from dotenv import load_dotenv
import os

from Versions.NEW.auth import auth
from Versions.NEW.dash import dash
from Versions.NEW.products import products
from Versions.NEW.payment import payment  

load_dotenv()

from Versions.NEW.db import get_db

db,cur=get_db()

app = Flask(__name__)
scrt_app = os.getenv("FLASK_SECRET_KEY")
app.secret_key = scrt_app

# ---------- REGISTER BLUEPRINTS ----------
app.register_blueprint(auth)
app.register_blueprint(products)
app.register_blueprint(payment)  
app.register_blueprint(dash)  
#"""
@app.errorhandler(404)
def page_not_found(e):
    db.rollback()
    return render_template(
        "404.html",
        code=404,
        title="Page Not Found",
        message="The page you’re looking for may have been moved, renamed, or is temporarily unavailable.",
        steps=[
            "Check the URL for any typing errors",
            "Refresh the page or try again after a moment",
            "Navigate back to our homepage to continue browsing",
            "Clear your browser cache if the issue persists"
        ],
        e=e
    ), 404

@app.errorhandler(500)
def internal_error(e):
    db.rollback()
    return render_template(
        "404.html",
        code=500,
        title="Internal Server Error",
        message="Oops! Something went wrong on our end. Please try again later.",
        steps=[
            "Refresh the page or try again after a moment",
            "If you are using VPN, please try switching it"
            "Clear your browser cache if the issue persists"
        ],
        e=e
    ), 500

@app.errorhandler(Exception)
def handle_exception(e):
    db.rollback()
    # Generic handler for other errors
    return render_template(
        "404.html",
        code=getattr(e, 'code', 400),
        title="An Error Occurred",
        message=str(e),
        steps=[
            "Check the URL for any typing errors",
            "Refresh the page or try again after a moment",
            "Navigate back to our homepage to continue browsing",
            "Clear your browser cache if the issue persists"
        ],
        e=e
    ), getattr(e, 'code', 400)
#"""
# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
