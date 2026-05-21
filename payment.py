from flask import Blueprint, request, render_template, session
from db import get_db
from dotenv import load_dotenv

import os
import time

load_dotenv()

payment = Blueprint("payment", __name__)

# ---------------- CASHFREE ----------------

from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.models.customer_details import CustomerDetails

Cashfree.XClientId = os.getenv("CASHFREE_APP_ID")
Cashfree.XClientSecret = os.getenv("CASHFREE_SECRET_KEY")

# Sandbox
Cashfree.XEnvironment = Cashfree.XSandbox

# Production
# Cashfree.XEnvironment = Cashfree.XProduction

x_api_version = "2023-08-01"


# ---------------- CHECKOUT DATA ----------------

def get_checkout_data(cur, uid, pids):

    products = []

    for pid in pids:

        cur.execute(
            "SELECT prodname, price, offer FROM products WHERE pid=%s",
            (int(pid),)
        )

        row = cur.fetchone()

        if not row:
            continue

        name, price, offer = row

        final_price = float(price) - (
            float(offer) * float(price) / 100
        )

        products.append({
            "pid": pid,
            "name": name,
            "price": final_price
        })

    cur.execute(
        "SELECT username, email, phone, address FROM users WHERE uid=%s",
        (uid,)
    )

    user = cur.fetchone()

    if not user:
        return None

    username, mail, phone, address = user

    total = sum(p["price"] for p in products)

    return {
        "username": username,
        "mail": mail,
        "phone": phone,
        "address": address,
        "products": products,
        "total": total
    }


# ---------------- CREATE CASHFREE ORDER ----------------

def create_cashfree_order(amount, uid, phone):

    try:

        order_id = f"ORDER_{uid}_{int(time.time())}"

        customer_phone = str(phone).strip()

        if len(customer_phone) < 10:
            customer_phone = "9999999999"

        customer_details = CustomerDetails(
            customer_id=f"CUS_{uid}",
            customer_phone=customer_phone
        )

        create_order_request = CreateOrderRequest(
            order_amount=float(amount),
            order_currency="INR",
            order_id=order_id,
            customer_details=customer_details
        )

        # WORKING VERSION
        response = Cashfree().PGCreateOrder(
            x_api_version,
            create_order_request,
            None,
            None
        )

        return {
            "success": True,
            "data": response.data.to_dict()
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }
# ---------------- INSERT CUSTOM ORDER ----------------

def insert_custom_order(db, cur, data, pids):

    try:

        description = ",".join([str(pid) for pid in pids])

        temp = "amount collect:" + str(data["total"])

        cur.execute("""
            INSERT INTO custom
            (date, template, description, status, mail, phone, name)

            VALUES
            (CURRENT_DATE, %s, %s, %s, %s, %s, %s)
        """, (
            temp,
            description,
            "paid",
            data["mail"],
            data["phone"],
            data["username"]
        ))

        db.commit()

        return True

    except Exception as e:

        db.rollback()

        print("CUSTOM INSERT ERROR:", e)

        return False


# ---------------- INSERT ORDERS ----------------

def insert_orders(db, cur, uid, products):

    try:

        for product in products:

            cur.execute("""
                INSERT INTO orders
                (uid, pid, price, status, date)

                VALUES
                (%s, %s, %s, %s, CURRENT_DATE)
            """, (
                uid,
                product["pid"],
                product["price"],
                "paid"
            ))

        db.commit()

        return True

    except Exception as e:

        db.rollback()

        print("ORDER INSERT ERROR:", e)

        return False


# ---------------- INSERT TRANSACTION ----------------

def insert_transaction(db, cur, amount, uid):

    try:

        title = f"Order Payment By User {uid}"

        cur.execute("""
            INSERT INTO transactions
            (date, title, debit, credit)

            VALUES
            (CURRENT_DATE, %s, %s, %s)
        """, (
            title,
            0,
            float(amount)
        ))

        db.commit()

        return True

    except Exception as e:

        db.rollback()

        print("TRANSACTION INSERT ERROR:", e)

        return False


# ---------------- CHECKOUT PAGE ----------------

@payment.route("/checkout/")
def checkout():

    db, cur = get_db()

    pids = request.args.getlist("pid")

    if not pids:

        pid = request.args.get("pid")

        if pid:
            pids = [pid]

    try:

        data = get_checkout_data(
            cur,
            session['uid'],
            pids
        )

        if not data:

            return render_template(
                "404.html",
                code=404,
                title="Checkout Error",
                message="Checkout data not found",
                steps=[
                    "Please try again later"
                ],
                e="Checkout data not found"
            )

        # CREATE CASHFREE ORDER
        payment_data = create_cashfree_order(
            data["total"],
            session['uid'],
            data["phone"]
        )

        if not payment_data["success"]:

            return render_template(
                "404.html",
                code=400,
                title="Payment Error",
                message=payment_data["message"],
                steps=[
                    "Please try again later"
                ],
                e=payment_data["message"]
            )

        return render_template(
            "checkout.html",
            data=data,
            total=data["total"],
            payment_session_id=payment_data["data"]["payment_session_id"],
            order_id=payment_data["data"]["order_id"]
        )

    except Exception as e:

        db.rollback()

        print(e)

        return render_template(
            "404.html",
            code=400,
            title="An Error Occurred",
            message=str(e),
            steps=[
                "Refresh the page and try again"
            ],
            e=e
        )

    finally:

        db.close()


# ---------------- PAYMENT SUCCESS ----------------

@payment.route("/orderplace")
def order():

    db, cur = get_db()

    pids = request.args.getlist("pid")

    try:

        data = get_checkout_data(
            cur,
            session['uid'],
            pids
        )

        if not data:

            return render_template(
                "404.html",
                code=400,
                title="Checkout Error",
                message="Checkout data not found",
                steps=[
                    "Please try again later"
                ],
                e="Checkout data not found"
            )

        # INSERT CUSTOM
        custom_success = insert_custom_order(
            db,
            cur,
            data,
            pids
        )

        if not custom_success:

            return render_template(
                "404.html",
                code=400,
                title="Database Error",
                message="Unable to save custom order",
                steps=[
                    "Please try again later"
                ],
                e="Custom order insert failed"
            )

        # INSERT ORDERS
        order_success = insert_orders(
            db,
            cur,
            session['uid'],
            data["products"]
        )

        if not order_success:

            return render_template(
                "404.html",
                code=400,
                title="Order Error",
                message="Unable to save order",
                steps=[
                    "Please try again later"
                ],
                e="Order insert failed"
            )

        # INSERT TRANSACTION
        transaction_success = insert_transaction(
            db,
            cur,
            data["total"],
            session['uid']
        )

        if not transaction_success:

            return render_template(
                "404.html",
                code=400,
                title="Transaction Error",
                message="Unable to save transaction",
                steps=[
                    "Please try again later"
                ],
                e="Transaction insert failed"
            )

        # SUCCESS PAGE
        return render_template(
            "order_success.html"
        )

    except Exception as e:

        db.rollback()

        print(e)

        return render_template(
            "404.html",
            code=400,
            title="An Error Occurred",
            message=str(e),
            steps=[
                "Refresh the page and try again",
                "Check your payment status"
            ],
            e=e
        )

    finally:

        db.close()

