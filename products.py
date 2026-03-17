from flask import Blueprint, render_template, render_template_string, redirect, url_for, session, abort, request
from db import get_db

products = Blueprint("products", __name__)

# ---------- HELPERS ----------
def login_required():
    return 'uid' in session

def alert(msg):
    return render_template_string(
        f"<script>alert('{msg}');history.back()</script>"
    )


def get_prod():
    db, cur = get_db()
    if not cur:
        return []

    try:
        cur.execute("SELECT pid,prodname,description,stock,price,offer,sold,supplier,catgy,collection FROM products ORDER BY sold")
        rows = cur.fetchall()
        if not rows:
            return []

        heading = (
            "pid","prodname","decrp","stock",
            "price","offer","sold","supplier",
            "ctgy","collection"
        )

        prods = []

        for row in rows:
            prod = dict(zip(heading, row))
            prod["prodname"] = prod["prodname"].title()

            cur.execute("SELECT link FROM images WHERE pid=%s", (prod["pid"],))
            imgs = cur.fetchall() or [("black.png",)]

            prod["images"] = [f"images/{i[0]}" for i in imgs]

            cur.execute(
                "SELECT SUM(star), COUNT(*) FROM review WHERE pid=%s",
                (prod["pid"],)
            )
            s, n = cur.fetchone()
            prod["rating"] = round(s / n) if s and n else 0

            prods.append(prod)

        return prods

    except Exception as e:
        db.rollback()
        print("get_prod error:", e)
        return []

    finally:
        db.close()



# ---------- HOME ----------
@products.route('/')
def home():
    data=get_prod()
    if data:
        return render_template("home.html",products=data[:3])
    else:
        return render_template("home.html")
    
# ---------- STORE ----------
@products.route('/store')
def store():
    db, cur = get_db()
    if not cur:
        db.rollback()
        return render_template("404.html"), 500

    try:
        cur.execute("SELECT Distinct catgy FROM products WHERE stock > 0")
        data = cur.fetchall()
        return render_template("store.html", products=get_prod(),ctgy=data)

    finally:
        db.close()

# ---------- PRODUCT DETAIL ----------
@products.route('/product/<int:pid>')
def product_detail(pid):
    db, cur = get_db()
    if not cur:
        db.rollback()
        return render_template("404.html"), 500
    try:
        cur.execute("SELECT pid,prodname,description,stock,price,offer,sold,supplier,catgy,collection FROM products WHERE pid=%s", (pid,))
        heading = (
        "pid","prodname","decrp","stock",
        "price","offer","sold","supplier",
        "ctgy","collection"
        )
        data = cur.fetchone()
        if not data:
            abort(404)
        prod = dict(zip(heading, data))
        prod['offer']=float(prod['price'])-(float(prod['price'])*float(prod['offer'])/100)
        prod["prodname"] = prod["prodname"].title()

        cur.execute("SELECT link FROM images WHERE pid=%s", (prod["pid"],))
        imgs = cur.fetchall() or (("black.png",))
        prod["images"] = ["images/" + i[0] for i in imgs]

        cur.execute("Select sum(star),count(*) from review where pid=%s", (prod["pid"],))
        prod['rating']=0
        s,n=cur.fetchone()
        if s is not None or n!=0:
            prod['rating']=round(s/n)

        cur.execute('Select "user",comment,star from review where pid=%s',(prod["pid"],))
        data=cur.fetchall()
        heading=("user","comment","star")
        l=[]
        for i in data:
            l.append(dict(zip(heading,i)))
        prod['reviews']=l

        return render_template("product.html", product=prod)

    finally:
        db.close()

# ---------- ADD TO WISHLIST ----------
@products.route('/add-wish/<int:pid>')
def add_wish(pid):
    if not login_required():
        return redirect(url_for('auth.login'))

    db, cur = get_db()
    if not cur:
        db.rollback()
        return render_template("404.html"), 500

    try:
        cur.execute("SELECT wid FROM wish WHERE uid=%s AND pid=%s", (session['uid'], pid))
        if cur.fetchone():
            return alert("Already in your wishlist")

        cur.execute("INSERT INTO wish (uid, pid) VALUES (%s, %s)", (session['uid'], pid))
        db.commit()
        return alert("Added to wishlist!")
    finally:
        db.close()

# ---------- ADD TO CART ----------
@products.route('/add-cart/<int:pid>')
def add_cart(pid):
    if not login_required():
        return redirect(url_for('auth.login'))

    db, cur = get_db()
    if not cur:
        db.rollback()
        return render_template("404.html"), 500

    try:
        cur.execute("SELECT cid FROM cart WHERE uid=%s AND pid=%s", (session['uid'], pid))
        if cur.fetchone():
            return alert("Already in your cart")

        cur.execute("INSERT INTO cart (uid, pid) VALUES (%s, %s)", (session['uid'], pid))
        db.commit()
        return alert("Added to cart!")
    finally:

        db.close()

#-------------review-------------
@products.route("/add_review/<int:pid>", methods=["POST"])
def add_review(pid):
    if not login_required():
        return redirect(url_for('auth.login'))
    conn,cur = get_db()
    
    star = request.form.get("star")
    comment = request.form.get("comment")

    cur.execute("Select username from users where uid=%s",(session['uid'],))
    username = cur.fetchone()[0]
    cur.execute(
        'INSERT INTO review (pid, star, comment, "user") VALUES (%s, %s, %s, %s)',
        (pid, star, comment, username)
    )

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("products.product_detail", pid=pid))

#----------contact--------
@products.route("/contact")
def contact():
    return render_template("contact.html")

#-----------cutomize-----------
@products.route("/custom")
def custom():
    return render_template("custom.html")

#--------------cart-------
@products.route("/cart")
def cart():
    if not login_required():
        return redirect(url_for('auth.login'))
    db,cur = get_db()
    cur.execute("Select pid from cart where uid=%s",(session['uid'],))
    data=cur.fetchall()
    l=[]
    m=[]
    t=of=0
    for i in data:
        cur.execute("Select * from products where pid=%s",(i[0],))
        data=cur.fetchone()
        data=list(data)
        of+=(data[4]*data[5]/100)
        m.append(data[0])
        cur.execute("Select link from images where pid=%s",(data[0],))
        img=cur.fetchone()
        if img:
            data.append("images/"+str(img[0]))
        else:
            data.append("images/black.png")
        l.append(data)
        t+=data[4]
    db.close()
    st=t-of
    return render_template("cart.html",cart=l,total=t,i=m,offer=of,sub=st)

@products.route("/delcart/<int:pid>")
def delcart(pid):
    db,cur=get_db()
    cur.execute("Delete from cart where pid=%s",(pid,))
    db.commit()
    db.close()
    return redirect((url_for("products.cart")))