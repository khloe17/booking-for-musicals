from flask import Flask, render_template, session, url_for, g, request, redirect
from database import get_db, close_db
from forms import RegistrationForm, LoginForm, ChoiceForm, SearchForm, FilterForm, ReviewForm, PayForm, ContactForm, CustomerForm
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_session import Session
from functools import wraps
from random import randint

'''
My system has two kinds of user: regular ones, and administrators.
Choose Register on the main page in order to register as a regular user.
But to login as an administrator, the user name is admin and the password is adminjrw

add or delete function(include add/delete one item or all items, write/delete reviews, add/delete musicals'
stock) and when user purchase items, the stock number will decrease accordingly

search items by full show name or show date in index.html

only user login in as admin (user: admin password: adminjrw) can see the stock function and customer details function

order function on tickets page and filter function on customer details page(only admin can see the information)

'''

app = Flask(__name__)
app.teardown_appcontext(close_db)
app.config["SECRET_KEY"] = "this-is-my-secret-key"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.before_request
def logged_in_user():
    db = get_db()
    g.user = session.get("user", None)
    entry = db.execute("""SELECT * FROM users
                                   WHERE user = ?;""", (g.user,)).fetchone()
    if entry is not None:
        g.email = entry[2]


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login", next=request.url))
        return view(*args, **kwargs)
    return wrapped_view


@app.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()

    musicals = None
    if form.validate_on_submit():
        name = form.name.data
        date = form.date.data
        db = get_db()

        if name != "" and date == "":
            name_capital = name.capitalize()

            musicals = db.execute("""SELECT * FROM musicals
                            WHERE name = ?;""", (name_capital,)).fetchall()
            return render_template("search_result.html", name=name, form=form, musicals=musicals)

        if name == "" and date != "":
            musicals = db.execute("""SELECT * FROM musicals
                            WHERE date >= ?;""", (date,)).fetchall()
            return render_template("search_result.html", date=date, form=form, musicals=musicals)

        elif name != "" and date != "":
            name_capital = name.capitalize()
            musicals = db.execute("""SELECT * FROM musicals
                            WHERE name = ? and date >= ?;""", (name_capital, date)).fetchall()
            return render_template("search_result.html", name=name, date=date, form=form, musicals=musicals)

        else:
            return render_template("index.html", form=form, musicals=musicals)

    return render_template("index.html", form=form, musicals=musicals)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = form.user.data
        password = form.password.data
        password2 = form.password2.data
        email = form.email.data

        db = get_db()
        clashing_user = db.execute("""SELECT * FROM users
                                   WHERE user = ?;""", (user,)).fetchone()
        if clashing_user is not None:
            form.user.errors.append("This user id is clashed with another")
        else:
            db.execute("""INSERT INTO users (user, password, email)
                            VALUES (?, ?, ?);""",
                       (user, generate_password_hash(password), email))
            # session["email"] = email
            # email = request.form.get('email')
            db.commit()
            return redirect(url_for("login"))

        if form.errors != {}:
            for err_msg in form.errors.values():
                print(
                    f'There was an error with creating a user: {err_msg}')
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = form.user.data
        password = form.password.data
        db = get_db()
        if user == "" and password == "":
            form.user.errors.append("Enter the user id")
            form.password.errors.append("Enter the password")
        elif user == "":
            form.user.errors.append("Enter the user id")
        elif password == "":
            form.password.errors.append("Enter the password")
        else:
            check_for_user = db.execute("""SELECT * FROM users
                                WHERE user = ?;""", (user,)).fetchone()
            if check_for_user is None:
                form.user.errors.append(
                    "This user is not in the database")
            elif not check_password_hash(check_for_user["password"], password):

                form.password.errors.append(
                    "Incorrect password")
            else:
                session.clear()
                session["user"] = user
                next_page = request.args.get("next")
                if not next_page:
                    next_page = url_for("index")
                return redirect(next_page)
    return render_template("login.html", form=form)


# @app.route("/change_password", methods=["GET", "POST"])
# def change_password():


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/musicals", methods=["GET", "POST"])
def musicals():
    form = FilterForm()

    db = get_db()
    musicals = db.execute(
        """SELECT * FROM musicals;""").fetchall()
    if form.validate_on_submit():
        filter = form.filter.data
        if filter == "Price(low to high)":
            musicals = db.execute(
                """SELECT * FROM musicals ORDER BY price ASC;""").fetchall()
        elif filter == "Price(high to low)":
            musicals = db.execute(
                """SELECT * FROM musicals ORDER BY price DESC;""").fetchall()
        else:
            musicals = db.execute(
                """SELECT * FROM musicals ORDER BY date;""").fetchall()

    # sorted_musicals = sorted(musicals, key=lambda musical: musical['price'])
    # sorted_musicals2 = sorted(
    #     musicals, key=lambda musical: musical['price'], reverse=True)
    # sorted_musicals3 = sorted(musicals, key=lambda musical: musical['date'])

    return render_template("musicals.html", form=form, musicals=musicals)


@app.route("/musical/<int:musical_id>")
def musical(musical_id):
    form = ChoiceForm()
    db = get_db()
    musical = db.execute("""SELECT * FROM musicals
                         WHERE musical_id = ?;""", (musical_id,)).fetchone()
    price = db.execute("""SELECT price FROM musicals
                         WHERE musical_id = ?;""", (musical_id,)).fetchone()
    date = db.execute("""SELECT date FROM musicals
                         WHERE musical_id = ?;""", (musical_id,)).fetchone()

    return render_template("musical.html", form=form, musical=musical, price=price, date=date)


@app.route("/review", methods=["GET", "POST"])
@login_required
def review():
    form = ReviewForm()
    db = get_db()
    if form.validate_on_submit():
        user = session.get("user", None)
        title = form.title.data
        content = form.content.data
        db.execute("""INSERT INTO reviews (r_user, title, content, date_reviewed)
                            VALUES (?, ?, ?, ?);""",
                   (user, title, content, datetime.utcnow()))
        db.commit()
        return redirect(url_for("index"))
    g.reviews = db.execute("""SELECT * FROM reviews;""").fetchall()
    return render_template("review.html", form=form)


@app.route("/cart")
@login_required
def cart():
    if "cart" not in session:
        session["cart"] = {}
    names = {}
    prices = {}
    dates = {}
    db = get_db()
    # when cart has no tickets
    if not session["cart"]:
        return render_template("cart.html", cart=session["cart"], names=names, prices=prices, dates=dates)
    else:
        for musical_id in session["cart"]:
            musical = db.execute("""SELECT * FROM musicals
                                WHERE musical_id= ?;""", (musical_id,)).fetchone()
            name = musical["name"]
            names[musical_id] = name
            price = musical["price"]
            prices[musical_id] = price
            date = musical["date"]
            dates[musical_id] = date

        return render_template("cart.html", cart=session["cart"], names=names, prices=prices, dates=dates, musical_id=musical_id)


@app.route("/add_to_cart/<int:musical_id>")
@login_required
def add_to_cart(musical_id):
    if "cart" not in session:
        session["cart"] = {}
    if musical_id not in session["cart"]:
        session["cart"][musical_id] = 1
    else:
        session["cart"][musical_id] = session["cart"][musical_id] + 1
    return redirect(url_for("cart"))


@app.route("/delete_from_cart/<int:musical_id>")
@login_required
def delete_from_cart(musical_id):
    if "cart" not in session:
        session["cart"] = {}
    elif session["cart"][musical_id] > 1:
        session["cart"][musical_id] = session["cart"][musical_id] - 1
    else:
        session["cart"].pop(musical_id)
    return redirect(url_for("cart"))


@app.route("/remove_from_cart/<int:musical_id>")
@login_required
def remove_from_cart(musical_id):
    if "cart" not in session:
        session["cart"] = {}
    else:
        session["cart"].pop(musical_id)
        # delete the item from the cart.
    return redirect(url_for("cart"))


@app.route("/clear_cart")
@login_required
def clear_cart():
    if "cart" not in session:
        session["cart"] = {}
    else:
        session["cart"].clear()
        # delete the item from the cart.
    return redirect(url_for("cart"))


# passing title from the html(web page)
@app.route("/delete_review/<title>")
@login_required
def delete_review(title):  # receiving the title in python side
    db = get_db()

    review = db.execute("""DELETE FROM reviews
                    WHERE title= ?;""", (title,))
    # using title as primary key to delete the row from the db
    db.commit()

    return redirect(url_for("review"))


@app.route("/stock")
@login_required
def stock():
    db = get_db()
    stock_list = db.execute(
        """SELECT musical_id, name, number FROM musicals""")
    return render_template("stock.html", stock_list=stock_list)


@app.route("/add_to_stock/<int:musical_id>")
@login_required
def add_to_stock(musical_id):
    # increment the value in the stock
    db = get_db()
    db.execute(
        """UPDATE musicals SET number = number + 1 WHERE musical_id = ?""", (musical_id,))
    db.commit()

    return redirect(url_for("stock"))


@app.route("/delete_from_stock/<int:musical_id>")
@login_required
def delete_from_stock(musical_id):
    # decrement from the stock
    db = get_db()
    db.execute(
        """UPDATE musicals SET number = number - 1 WHERE musical_id = ?""", (musical_id,))
    db.commit()
    return redirect(url_for("stock"))


@app.route("/buy_tickets")
@login_required
def buy_tickets():
    # reduce the stock
    db = get_db()
    # print(session["cart"])

    # print(session["cart"].keys(), session["cart"].values())
    musical_ids = list(session["cart"].keys())
    quantities = list(session["cart"].values())
    for id in musical_ids:
        db.execute(
            f"""UPDATE musicals SET number = number - {quantities[musical_ids.index(id)]} WHERE musical_id = ?""",
            (id,))

    # order history

    names = {}
    prices = {}
    quantities = {}

    for musical_id in session["cart"]:
        quantity = session["cart"][musical_id]
        quantities[musical_id] = quantity
        musical = db.execute("""SELECT * FROM musicals
                            WHERE musical_id= ?;""", (musical_id,)).fetchone()
        print(musical)
        print(musical['name'])

        name = musical["name"]
        names[musical_id] = name
        price = musical["price"]
        prices[musical_id] = price
        user = session["user"]
        db.execute("""INSERT INTO orders (o_name, o_price, o_quantity, o_owner)
                        VALUES (?, ?, ?, ?);""",
                   (name, price, quantity, user))
        print(name)
        print(price)

    db.commit()
    session["cart"].clear()
    # send it to the account page
    return redirect(url_for("account"))


# display the order history in account page

@app.route("/account", methods=["GET", "POST"])
def account():
    form = PayForm()
    db = get_db()

    order_list = db.execute(
        """SELECT o_name, o_price, o_quantity FROM orders WHERE o_owner = ?""", (session["user"],))

    return render_template("account.html", form=form, order_list=order_list)


# contact us
@app.route("/contact_us", methods=["GET", "POST"])
@login_required
def contact_us():
    form = ContactForm()
    if form.validate_on_submit():
        user = form.user.data
        email = form.email.data
        topic = form.topic.data
        message = form.message.data
        db = get_db()
        db.execute("""INSERT INTO contacts(c_user, c_email, c_topic, c_message)
                VALUES(?, ?, ?, ?); """,
                   (user, email, topic, message))
        db.commit()
        #return redirect(url_for("contact.html"))
        return render_template("contact.html", form=form, message="Thank you!")
    return render_template("contact.html", form=form)
    # return render_template("contact.html", form=form)
    # the question is want to disappear after submitting


# admin see the information about contact us and filter information by topic

@app.route("/customer_details", methods=["GET", "POST"])
def customer_details():
    form = CustomerForm()
    db = get_db()
    contact_list = db.execute("""SELECT c_user, c_email, c_topic, c_message FROM contacts""").fetchall()
    if form.validate_on_submit():
        filter_customer = form.filter_customer.data
        if filter_customer == "I have a question about the show":
            contacts = db.execute(
                """SELECT * FROM contacts WHERE c_topic = ?;""", (filter_customer,)).fetchall()
            return render_template("customer_details.html", contact_list=contacts, form=form, filter_customer=filter_customer)
        elif filter_customer == "I have a question about tickets":
            contacts = db.execute(
                """SELECT * FROM contacts WHERE c_topic = ?;""", (filter_customer,)).fetchall()
            return render_template("customer_details.html", contact_list=contacts, form=form, filter_customer=filter_customer)
        elif filter_customer == "I have a question about my order":
            contacts = db.execute(
                """SELECT * FROM contacts WHERE c_topic = ?;""", (filter_customer,)).fetchall()
            return render_template("customer_details.html", contact_list=contacts, form=form, filter_customer=filter_customer)
        else:
            contacts = db.execute(
                """SELECT * FROM contacts WHERE c_topic = ?;""", (filter_customer,)).fetchall()
            return render_template("customer_details.html", contact_list=contacts, form=form, filter_customer=filter_customer)


    return render_template("customer_details.html", contact_list=contact_list, form=form)





    # delete order history

    # @app.route("/delete_order_history/<title>")
    # @login_required
    # def delete_review(title):  # receiving the title in python side
    #     db = get_db()

    #     review = db.execute("""DELETE FROM reviews
    #                     WHERE title= ?;""", (title,))
    #     # using title as primary key to delete the row from the db
    #     db.commit()

    #     return redirect(url_for("review"))
