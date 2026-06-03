from flask import Blueprint, render_template, redirect, url_for, request, session, render_template_string

auth = Blueprint("auth", __name__)

from Versions.NEW.db import get_db

db,cur=get_db()

# -------- HELPER --------
def login_required():
    return 'uid' in session


# -------- AUTH --------
@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/authenticate', methods=['POST'])
def authenticate():
    db,cur=get_db()
    try:
        email = request.form['email']
        password = request.form['password']

        cur.execute("SELECT uid, pass FROM users WHERE email = %s;", (email,))
        user = cur.fetchone()

        if not user or user[1] != password:
            return render_template_string("<script>alert('Invalid credentials');history.back()</script>")

        session['uid'] = user[0]
        return render_template_string("<script>history.go(-2)</script>")

    except Exception as e:
        db.rollback()
        return render_template(
        "404.html",
        code=400,
        title="An Error Occurred",
        message=str(e),
        steps=[
            "Check the URL for any typing errors",
            "Refresh the page or try again after a moment",
            "Navigate back to our homepage to continue browsing",
            "Clear your browser cache if the issue persists"
        ],
        e=e
    )


@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('products.home'))


# -------- REGISTER --------
@auth.route('/register')
def register():
    return render_template('register.html')


@auth.route('/add-user', methods=['POST'])
def add_user():
    cur = db.cursor()  # request-scoped cursor

    try:
        name = request.form['name']
        email = request.form['email']
        password = request.form['pass']
        cpassword = request.form['cpass']

        if password != cpassword:
            return render_template_string(
                "<script>alert('Passwords do not match');history.back()</script>"
            )

        cur.execute("SELECT uid FROM users WHERE email = %s;", (email,))
        if cur.fetchone():
            return render_template_string(
                "<script>alert('Email already exists');history.back()</script>"
            )

        cur.execute(
            "INSERT INTO users (username, email, pass, desig) VALUES (%s, %s, %s, %s) RETURNING uid;",
            (name, email, password,"u")
        )

        uid = cur.fetchone()
        if uid is None:
            raise Exception("UID not returned after insert")

        session['uid'] = uid[0]

        db.commit()
        return redirect(url_for('auth.profile'))

    finally:
        cur.close()



# -------- PROFILE --------
@auth.route('/profile')
def profile():
    if not login_required():
        return redirect(url_for('auth.login'))
    db,cur=get_db()
    try:
        cur.execute("SELECT * FROM users WHERE uid=%s", (session['uid'],))
        user = cur.fetchone()

        cur.execute("SELECT * FROM orders WHERE uid = %s ORDER BY oid DESC;", (session['uid'],))
        orders = cur.fetchall()

        cur.execute("""SELECT products.pid, products.prodname, products.price, products.offer FROM wish JOIN products ON products.pid = wish.pid WHERE wish.uid = %s;""", (session['uid'],))
        wishlist = cur.fetchall()

        cur.execute("""SELECT products.pid, products.prodname, products.price, products.offer FROM cart JOIN products ON products.pid = cart.pid WHERE cart.uid = %s;""", (session['uid'],))
        cart = cur.fetchall()
        t=[]
        for i in cart:
            t.append(i[0])
        return render_template("profile.html",
                               user=user,
                               orders=orders,
                               wishlist=wishlist,
                               cart=cart,t=t)

    except Exception as e:
        db.rollback()
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
    )


# -------- UPDATE PROFILE --------
@auth.route('/update-profile', methods=['POST'])
def update_profile():
    if not login_required():
        return redirect(url_for('auth.login'))
    try:
        cur.execute("UPDATE users SET username = %s, phone = %s, address = %s WHERE uid = %s;",(request.form['name'],request.form['phone'],request.form['address'],session['uid']))
        db.commit()
        return redirect(url_for('auth.profile'))

    except Exception as e:
        db.rollback()
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
    )


# -------- CHANGE PASSWORD --------
@auth.route('/change-password', methods=['POST'])
def change_password():
    if not login_required():
        return redirect(url_for('auth.login'))

    try:
        old = request.form['old']
        new = request.form['new']
        confirm = request.form['confirm']

        if new != confirm:
            return render_template_string("<script>alert('Passwords do not match');history.back()</script>")

        cur.execute("SELECT pass FROM users WHERE uid=%s;", (session['uid'],))
        if cur.fetchone()[0] != old:
            return render_template_string("<script>alert('Wrong password');history.back()</script>")

        cur.execute("UPDATE users SET pass=%s WHERE uid=%s;", (new, session['uid']))
        db.commit()

        return redirect(url_for('auth.profile'))

    except Exception as e:
        db.rollback()
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
    )

@auth.route("/password")
def forgot_password():
    return render_template('pswd.html')


@auth.route("/email-request", methods=['POST'])
def email_request():

    email = request.form['email']

    db, cur = get_db()

    try:
        cur.execute(
            "SELECT pass FROM users WHERE email=%s",
            (email,)
        )

        data = cur.fetchone()

        if data is None:
            return render_template_string(
                "<script>alert('Email not registered!');history.back()</script>"
            )

        pswd = data[0]

        cur.execute(
            "INSERT INTO password VALUES (%s,%s)",
            (email, pswd)
        )

        db.commit()

        return render_template_string(
            "<script>alert('You will get your password in your email soon!');history.back()</script>"
        )

    except Exception as e:
        return str(e)

    finally:
        db.close()