from flask import Blueprint, render_template, redirect, url_for, request, session, render_template_string
import datetime
dash = Blueprint("dash", __name__)

from db import get_db 

# -------- HELPER --------
def login_required():
    return 'uid' in session

@dash.route("/dash")
def dashbd():
    if not login_required():
        return redirect(url_for('auth.login'))
    return render_template("dash.html")
