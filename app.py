from flask import Flask, render_template, request, session, redirect, url_for, g, make_response
from forms import RegistrationForm, LoginForm, RequestForm, ReviewForm, RemoveForm, OrderForm, NameForm, PassForm
from forms import DeleteForm, EditForm, AddForm, EditFForm, UpdateForm, UpdateRForm, UserForm, ProceedForm
from database import close_db, get_db
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta, time
from random import randint

"""
My system has two kinds of user: regular ones, and administrators.
Choose Register on the main page in order to register as a regular user.
But to login as an administrator, the user name is admin and the password is admin

@app.route('/_sort') any of the sorts.
@app.route('/xret_menu')
@app.route('/settings_user')
"""

app = Flask(__name__)
app.config["SECRET_KEY"] = "this-is-my-secret-key"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.teardown_appcontext
def close_db_at_end_of_requests(e=None):
    close_db(e)

@app.before_request
def load_logged_in_user():
    g.user = session.get("user_id", None)
    g.name = session.get('name', None)

def login_required(view):
    @wraps(view)                       
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url)) 
        return view(**kwargs)
    return wrapped_view

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        password2 = form.password2.data
        fname = form.fname.data
        lname = form.lname.data
        name = fname + " " + lname
        db = get_db()
        if  db.execute("""SELECT * FROM users    
                            WHERE user_id = ?""", (user_id,)).fetchone() is not None:
                form.user_id.errors.append("User id used already")
        else:
            db.execute("""INSERT INTO users
                        VALUES (?, ?, ?);""", (user_id, generate_password_hash(password), name))
            db.commit()
            return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        db = get_db()
        user = db.execute('''SELECT * FROM users
                   WHERE user_id = ?; ''', (user_id,)).fetchone()
        if user is None:
            form.user_id.errors.append("Unknown user id.")
        elif not check_password_hash(user['password'], password):   
            form.password.errors.append("Incorrect password!")
        else:
            #session.clear()
            session["user_id"] = user_id
            session['name'] = user['name']
            session['info'] = 0
            order = db.execute('''SELECT COUNT(*) as count FROM order_info WHERE user_id = ? ''', (user_id,)).fetchall()
            order = [orders['count'] for orders in order]
            session['order'] = order[0]
            next_page = request.args.get("next")
            if not next_page:
                next_page = url_for("index")
            return redirect(next_page)
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/menu", methods=['GET', 'POST'])
def menu():
    db = get_db() 
    menu = db.execute('''SELECT * FROM menu WHERE description != '' ;''').fetchall()

    return render_template('menu.html', menu=menu)

@app.route("/amenu", methods=['GET', 'POST'])
@login_required
def amenu():
    db = get_db()
    if g.user == 'rb' or g.user == 'admin' : 
        menu = db.execute('''SELECT * FROM menu;''').fetchall()
    return render_template('amenu.html', menu=menu)

@app.route("/sort/<sort>")
def sort(sort):
    db = get_db()
    if sort == 'alphabetical':
        if session['info'] == 0:
            menu = db.execute('''SELECT * FROM menu WHERE description != '' ORDER BY name ;''').fetchall()
        else: 
            menu = db.execute('''SELECT * FROM menu WHERE description != '' ORDER BY name DESC;''').fetchall()
    elif sort == 'low':
        menu = db.execute('''SELECT * FROM menu WHERE description != '' ORDER BY price ;''').fetchall()
    else:
        menu = db.execute('''SELECT * FROM menu WHERE description != '' ORDER BY price DESC;''').fetchall()
    return render_template('menu.html', menu=menu)

@app.route("/xsort/<sort>")
def xsort(sort):
    db = get_db()
    if sort == 'alphabetical':
            menu = db.execute('''SELECT * FROM menu WHERE description = '' ORDER BY name ;''').fetchall()
    elif sort == 'low':
        menu = db.execute('''SELECT * FROM menu WHERE description = '' ORDER BY price ;''').fetchall()
    else:
        menu = db.execute('''SELECT * FROM menu WHERE description = '' ORDER BY price DESC;''').fetchall()
    return render_template('xmenu.html', menu=menu)   

@app.route("/asort/<sort>")
def asort(sort):
    db = get_db()
    if sort == 'alphabetical':
            menu = db.execute('''SELECT * FROM menu ORDER BY name;''').fetchall()
    elif sort == 'low':
        menu = db.execute('''SELECT * FROM menu ORDER BY price;''').fetchall()
    elif sort == 'desc':
        menu = db.execute('''SELECT * FROM menu ORDER BY description;''').fetchall()
    else:
        menu = db.execute('''SELECT * FROM menu ORDER BY price DESC;''').fetchall()
    return render_template('amenu.html', menu=menu) 

@app.route('/add_menu', methods=['GET','POST'])
@login_required
def add_menu():
    if g.user == 'rb' or g.user == 'admin':
        db = get_db()
        form = AddForm()
        message = ''
        menu = db.execute('''SELECT * FROM menu;''').fetchall()
        names = [food['name'] for food in menu]
        if form.validate_on_submit():
            name = form.name.data
            name = name[0].upper() + name[1:]
            if name in names:
                form.name.errors.append("Food already in database.")
            else:
                price = form.price.data
                description = form.description.data
                allergens = form.allergens.data
                var = form.var.data
                db.execute('''INSERT INTO menu (name, price, description, allergens)
                                VALUES(?, ?, ?, ?);''', (name, price, description, allergens))
                db.commit()
                if var != "" or var != " ":
                    db.execute('''INSERT INTO varieties(name, var)
                                VALUES (?, ?);''', (name, var))
                    db.commit()
                message = 'Food added in the menu!' 
                return render_template('message.html', message=message, link='amenu', link_name='menu')  
    else:
        return render_template('message.html', message='Access Denied')
    return render_template('add.html', form=form)

@app.route('/edit_menu', methods=['GET','POST'])
def edit_menu():
    db = get_db()
    menu = db.execute('''SELECT * FROM menu;''').fetchall()
    forms = EditFForm()
    forms.name.choices = [food['name'] for food in menu]
    forms.name.choices.insert(0, "")
    delete = DeleteForm()
    if forms.validate_on_submit():
        name = forms.name.data
        price = forms.price.data
        description = forms.description.data
        if price != '' and description != '':
            db.execute('''UPDATE menu  SET price = ? AND description = ?
                        WHERE name = ? ''', (price, description, name))
            db.commit()
            message = 'Menu Updated!'
        elif price != '' and description == '':
            db.execute('''UPDATE menu  SET price = ? WHERE name = ? ''', (price, name))
            db.commit()
            message = 'Menu Updated.'
        elif price == '' and description != '':
            db.execute('''UPDATE menu  SET description = ? WHERE name = ? ''', (description, name))
            db.commit()
            message = 'Menu Updated.!'
        return render_template('message.html', message=message, link='amenu', link_name='menu')
    elif delete.validate_on_submit():
        name = forms.name.data
        db.execute('''DELETE FROM menu WHERE name = ?''', (name,))
        db.commit()
        db.execute('''DELETE FROM type WHERE name = ?''', (name,))
        db.commit()
        db.execute('''DELETE FROM varieties WHERE name = ?''', (name,))
        db.commit()
        message = "Food item deleted"
        return render_template('message.html', message=message, link='amenu', link_name='menu')
    return render_template('edit_menu.html', forms=forms, delete=delete) 
  
@app.route("/rsort/<sort>")
def rsort(sort):
    db = get_db()
    form = UpdateRForm()
    requests = db.execute('''SELECT * FROM requests ORDER BY status DESC;''').fetchall()
    form.Id.choices = [request['id'] for request in requests]
    if sort == 'id':
        if session['info'] == 0:
            requests = db.execute('''SELECT * FROM requests ORDER BY id;''').fetchall()
            session['info'] += 1
        else:
            requests = db.execute('''SELECT * FROM requests ORDER BY id DESC;''').fetchall()
            session['info'] = 0
    elif sort == 'user':
        if session['info'] == 0:
            requests = db.execute('''SELECT * FROM requests ORDER BY user_id;''').fetchall()
            session['info'] += 1
        else:
            requests = db.execute('''SELECT * FROM requests ORDER BY user_id DESC;''').fetchall()
            session['info'] = 0
    elif sort == 'food':
        if session['info'] == 0:
            requests = db.execute('''SELECT * FROM requests ORDER BY food;''').fetchall()
            session['info'] += 1
        else:
            requests = db.execute('''SELECT * FROM requests ORDER BY food DESC;''').fetchall()
            session['info'] = 0
    else:
        if session['info'] == 0:
            requests = db.execute('''SELECT * FROM requests ORDER BY date;''').fetchall()
            session['info'] += 1
        else:
            requests = db.execute('''SELECT * FROM requests ORDER BY date DESC;''').fetchall()
            session['info'] = 0
    return render_template('arequest.html', requests=requests, form=form) 

@app.route("/osort/<sort>")
def osort(sort):
    db = get_db()
    form = UpdateForm()
    forms = RemoveForm()
    user = session['user_id']
    if sort == 'astatus':
        if session['info'] == 0:
            orders = db.execute('''SELECT *  FROM order_info as oi JOIN users as u
                            ON oi.user_id = u.user_id ORDER BY status DESC;''').fetchall()
            session['info'] += 1
        else:
            orders = db.execute('''SELECT *  FROM order_info as oi JOIN users as u
                            ON oi.user_id = u.user_id ORDER BY status;''').fetchall()
            session['info'] = 0
    elif sort == 'adate_order':
        if session['info'] == 0:
            orders = db.execute('''SELECT *  FROM order_info as oi JOIN users as u
                            ON oi.user_id = u.user_id ORDER BY date_of_order ;''').fetchall()
            session['info'] += 1
        else:
            orders = db.execute('''SELECT *  FROM order_info as oi JOIN users as u
                            ON oi.user_id = u.user_id ORDER BY date_of_order DESC;''').fetchall()
            session['info'] = 0
    elif sort == 'adate_del':
        if session['info'] == 0:
            orders = db.execute('''SELECT *  FROM order_info as oi JOIN users as u
                            ON oi.user_id = u.user_id ORDER BY date_del;''').fetchall()
            session['info'] += 1
        else:
            orders = db.execute('''SELECT *  FROM order_info as oi JOIN users as u
                            ON oi.user_id = u.user_id ORDER BY date_del DESC;''').fetchall()
            session['info'] = 0
    elif sort == 'atotal':
        if session['info'] == 0:
            orders = db.execute('''SELECT *  FROM order_info as oi JOIN users as u
                            ON oi.user_id = u.user_id ORDER BY total;''').fetchall()
            session['info'] += 1
        else:
            orders = db.execute('''SELECT *  FROM order_info as oi JOIN users as u
                            ON oi.user_id = u.user_id ORDER BY total DESC;''').fetchall()
            session['info'] = 0
    elif sort == 'ctotal':
        if session['info'] == 0:
            orders = db.execute('''SELECT *  FROM order_info as oi JOIN users as u
                            ON oi.user_id = u.user_id WHERE user_id = ? 
                            ORDER BY total;''', (user,)).fetchall()
            session['info'] += 1
        else:
            orders = db.execute('''SELECT *  FROM order_info as oi JOIN users as u
                            ON oi.user_id = u.user_id WHERE user_id = ?
                            ORDER BY total DESC;''', (user,)).fetchall()
            session['info'] = 0
    elif sort == 'cdate_order':
        if session['info'] == 0:
            orders = db.execute('''SELECT *  FROM order_info as oi JOIN users as u
                            ON oi.user_id = u.user_id WHERE user_id = ? 
                            ORDER BY date_of_order;''', (user,)).fetchall()
            session['info'] += 1
        else:
            orders = db.execute('''SELECT *  FROM order_info as oi JOIN users as u
                            ON oi.user_id = u.user_id WHERE user_id = ?
                            ORDER BY date_of_order DESC;''', (user,)).fetchall()
            session['info'] = 0
    elif sort == 'cdate_del':
        if session['info'] == 0:
            orders = db.execute('''SELECT *  FROM order_info as oi JOIN users as u
                            ON oi.user_id = u.user_id WHERE user_id = ? 
                            ORDER BY date_del;''', (user,)).fetchall()
            session['info'] += 1
        else:
            orders = db.execute('''SELECT *  FROM order_info as oi JOIN users as u
                            ON oi.user_id = u.user_id WHERE user_id = ?
                            ORDER BY date_del DESC;''', (user,)).fetchall()
            session['info'] = 0
    elif sort == 'cstatus':
        if session['info'] == 0:
            orders = db.execute('''SELECT *  FROM order_info as oi JOIN users as u
                            ON oi.user_id = u.user_id WHERE oi.user_id = ? 
                            ORDER BY status;''', (user,)).fetchall()
            session['info'] += 1
        else:
            orders = db.execute('''SELECT *  FROM order_info as oi JOIN users as u
                            ON oi.user_id = u.user_id WHERE user_id = ?
                            ORDER BY status DESC;''', (user,)).fetchall()
            session['info'] = 0
    order = db.execute('''SELECT * FROM orders as o JOIN menu as m
                        ON o.food_id = m.food_id; ''').fetchall()
    lis = []
    for ordr in orders:
        li = {'user_id': ordr['user_id'], 'name' :ordr['name'], 'date_of_order':ordr['date_of_order'], 
            'date_del': ordr['date_del'], 'time_del': ordr['time_del'], 
                'address': ordr['address'], 'info': ordr['info'],
                'status': ordr['status'], 'total': ordr['total']}
        orer = []
        for ordd in order:
            if ordr['id'] == ordd['oi_id']:
                orer.append(f"{ordd['name']}: {ordd['qty']}")
        li['order'] = orer
        lis.append(li)
    return render_template('orders.html', lis=lis, form=form, forms=forms) 

@app.route("/food/<int:food_id>")
def food(food_id):
    db = get_db()
    food = db.execute('''SELECT * FROM menu
                    WHERE food_id = ?;''', (food_id,)).fetchone()
    vari = db.execute('''SELECT menu.name, var FROM menu JOIN varieties 
                        ON menu.name = varieties.name
                        WHERE food_id = ? ''',(food_id,)).fetchall()
    return render_template('food.html', food=food, vari=vari)

@app.route("/request_food", methods=['GET', 'POST'])
@login_required
def request_food():
    db = get_db()
    user_id = session['user_id']
    if user_id == 'admin' or user_id == 'rb':
        form = UpdateRForm()
        requests = db.execute('''SELECT * FROM requests ORDER BY status DESC;''').fetchall()
        form.Id.choices = [request['id'] for request in requests]
        if form.validate_on_submit():
            Id = form.Id.data
            stat = db.execute('''SELECT * FROM requests WHERE id = ?;''', (Id,)).fetchone()
            if stat['status'] == 'UNREAD':
                status = 'READ'
                db.execute('''UPDATE requests SET status = ? WHERE id = ?''',(status, Id))
                db.commit()
                message = 'Food request updated!'
            else:
                status = 'UNREAD'
                db.execute('''UPDATE requests SET status = ? WHERE id = ?''',(status, Id))
                db.commit()
                message = 'Food request updated!'
            return render_template('message.html', message=message, link='requests', link_name='food requests')
        return render_template('arequest.html', requests=requests, form=form)
    else:
        req = db.execute('''SELECT * FROM requests WHERE user_id = ?;''', (user_id,)).fetchall()
        form = RequestForm()
        if form.validate_on_submit():
            food = form.food.data
            status = 'UNREAD'
            date = datetime.now().date()
            if db.execute('''SELECT * FROM menu WHERE name = ? and description != '' ''', (food,)).fetchone() is not None:
                form.food.errors.append("Food already in the menu!")
            else:
                db = get_db()
                db.execute('''INSERT INTO requests(user_id, food, status, date)
                        VALUES (?, ?, ?, ?);''', (user_id, food, status, date))
                db.commit()
                return render_template('message.html', message="Request submitted!", link='requests', link_name='request')
    return render_template('request.html', form=form, req=req)

@app.route('/remove_request/<int:Id>')
def remove_request(Id):
    db = get_db()
    db.execute('''DELETE FROM reviews WHERE id = ?;''', (Id,))
    db.commit()
    return render_template('message.html', message="Request Removed!", link='requests', link_name='request')

@app.route("/leave_review", methods=['GET', 'POST'])
@login_required
def leave_review():
    form = ReviewForm()
    message = ""
    db = get_db()
    food = form.food.data
    review = form.review.data
    user_id = session["user_id"]
    foods = db.execute('''SELECT * FROM menu;''').fetchall()
    form.food.choices = [ item['name'] for item in foods]
    form.food.choices.insert(0, " ")
    if form.validate_on_submit():
        db.execute(''' INSERT INTO reviews (user_id, n_food, review) 
                    VALUES (?,?,?);''', (user_id, food, review))
        db.commit()
        message = 'Review Submitted!'
        return render_template('message.html', message=message, link='review', link_name='review')
    return render_template('leave_reviews.html', form=form)

@app.route("/review", methods=['GET', 'POST'])
def review():
    db = get_db()
    reviews = db.execute('''SELECT * FROM reviews as r JOIN users as u
                            ON r.user_id = u.user_id;''').fetchall()   
    message = ""
    rev=""
    order = ''
    if g.user != None: 
        user_id = session['user_id']
        rev = db.execute('''SELECT * FROM reviews WHERE user_id = ?;''', (user_id,)).fetchall()
        order = db.execute('SELECT * FROM order_info WHERE user_id = ?;', (user_id,)).fetchall()
    if reviews == []:
        message = "No reviews submitted!"
    return render_template('reviews.html', reviews=reviews, message=message, rev=rev, order=order)

@app.route("/edit_review", methods=['GET', 'POST'])
@login_required
def edit_review():
    db = get_db()
    form = EditForm()
    user_id = session['user_id']
    reviews = db.execute('SELECT * FROM reviews WHERE user_id=?;', (user_id,)).fetchall()
    form.Id.choices = [review['id'] for review in reviews]
    if form.validate_on_submit():
        Id = form.Id.data
        review = form.review.data
        db.execute('''UPDATE reviews SET review = ? WHERE id = ? ''', (review, Id))
        db.commit()
        message = "Review edited!"
        return render_template('message.html', message=message, link='review', link_name='reviews')
    return render_template('edit_review.html', reviews=reviews, form=form)

@app.route('/message/<message>')
def message(message):
    return render_template('message.html', message=message)

@app.route('/remove_review/<int:Id>')
def remove_review(Id):
    db = get_db()
    db.execute('''DELETE FROM reviews WHERE id = ? ;''', (Id,))
    db.commit()
    return render_template('message.html', message="Review Removed!", link='review', link_name='review')

@app.route('/orders', methods=["GET", "POST"])
@login_required
def orders():
    db = get_db()
    message = ''
    if g.user == 'admin' or g.user == 'rb' :
        form = UpdateForm()
        forms = RemoveForm()
        orders = db.execute('''SELECT *  FROM order_info as oi JOIN users as u
                            ON oi.user_id = u.user_id;''').fetchall()
        order = db.execute('''SELECT * FROM orders as o JOIN menu as m
                            ON o.food_id = m.food_id; ''').fetchall()
        lis = []
        form.Id.choices = [ o['id'] for o in orders]
        form.Id.choices.insert(0, '')
        forms.Id.choices = [ o['id'] for o in orders]
        forms.Id.choices.insert(0, '')
        for ordr in orders:
            li = {'id': ordr['id'],'user_id': ordr['user_id'], 'name' :ordr['name'], 'date_of_order':ordr['date_of_order'], 
                'date_del': ordr['date_del'], 'time_del': ordr['time_del'], 
                    'address': ordr['address'], 'info': ordr['info'],
                    'status': ordr['status'], 'total': ordr['total']}
            orer = []
            for ordd in order:
                if ordr['id'] == ordd['oi_id']:
                    orer.append(f"{ordd['name']}: {ordd['qty']}")
            li['order'] = orer
            lis.append(li)
        if form.validate_on_submit():
            Id = form.Id.data
            status = form.status.data
            db.execute('''UPDATE order_info SET status = ? WHERE id = ? ''', (status, Id))
            db.commit()
            message='Order Updated!'
            return render_template('message.html', message=message, link='orders', link_name='orders')
        elif forms.validate_on_submit():
            Id = forms.Id.data
            db.execute('''DELETE FROM order_info WHERE id = ?''', (Id,))
            db.commit()
            db.execute('''DELETE FROM orders WHERE oi_id =? ''', (Id,))
            db.commit()
            message='Order Deleted!'
            return render_template('message.html', message=message, link='orders', link_name='orders')
    return render_template('orders.html', orders=orders, lis=lis, form=form, forms=forms)

@app.route('/cart', methods=['GET', 'POST'])
def cart(): 
    db = get_db()
    if "cart" not in session:
        session["cart"] = {}
    names = {}
    prices = {}
    food_id = []
    for food_id in session["cart"]:
        name = db.execute('''SELECT * FROM menu
                            WHERE food_id = ?; ''',(food_id,)).fetchone()["name"]
        names[food_id] = name
        price = db.execute('''SELECT * FROM menu
                            WHERE food_id = ?; ''',(food_id,)).fetchone()["price"]
        prices[food_id] = session["cart"][food_id] * price
    total = sum(prices.values())
    return render_template("cart.html", cart=session['cart'], names=names, prices=prices, total=total)

@app.route('/add_to_cart/<int:food_id>')
#@login_required
def add_to_cart(food_id):
    if "cart" not in session:
        session["cart"] = {}
    if food_id not in session["cart"]:
        session["cart"][food_id] = 0
    session["cart"][food_id] += 1
    return redirect( url_for('cart') )

@app.route('/remove_to_cart/<int:food_id>')
#@login_required
def remove_to_cart(food_id):
    if session['cart'][food_id] == 1:
        del session['cart'][food_id]
    else:
        session["cart"][food_id] -= 1
    return redirect( url_for('cart') )


@app.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    db = get_db()
    names = {}
    prices = {}
    food_id = [] 
    message = ''   
    for food_id in session["cart"]:
        name = db.execute('''SELECT * FROM menu
                            WHERE food_id = ?; ''',(food_id,)).fetchone()["name"]
        names[food_id] = name
        price = db.execute('''SELECT * FROM menu
                            WHERE food_id = ?; ''',(food_id,)).fetchone()["price"]
        prices[food_id] = session["cart"][food_id] * price
    total = float(sum(prices.values()))
    time_open = time(8,0, 0)
    time_close = time(21,0, 0)
    form = OrderForm()
    valid_date = datetime.now() + timedelta(days=7)
    if bool(session['cart']) == False:
        return render_template('message.html', message='Uh-oh. Cart is empty!', link='menu', link_name='menu')
    else:
        if form.validate_on_submit():
            user_id = session['user_id']
            date_del = form.date.data
            date_of_order = datetime.now().strftime('%Y-%m-%d %H:%M')
            info = form.info.data
            time_del = form.time.data
            status = 'PENDING'
            address = form.first_line.data + "," + form.sec_line.data + "," + form.town.data + "," + form.county.data + "," + form.eircode.data
            if date_del< valid_date.date():
                form.date.errors.append('Date of order must be in a week time.')
            if time_del > time_close or time_del < time_open:
                form.time.errors.append('Time of order must be from 8:00-21:00.')
            else:
                time_del = str(form.time.data)
                date_del = str(form.date.data)
                db.execute('''INSERT INTO order_info(user_id, date_of_order, date_del, time_del, info, total, address, status)
                            VALUES (?,?,?,?,?,?,?,?);''', (user_id, date_of_order, date_del, time_del, info, total, address, status))
                db.commit()
                Id = db.execute('''SELECT * FROM order_info WHERE user_id = ? AND date_of_order = ? ;''', (user_id, date_of_order)).fetchone()['Id']
                for food_id in session['cart']:
                    db.execute('''INSERT INTO orders
                                    VALUES (?,?,?);''',(Id, food_id, session['cart'][food_id]))
                    db.commit()
                order = db.execute('''SELECT COUNT(*) as count FROM order_info WHERE user_id = ? ''', (user_id,)).fetchall()
                order = [orders['count'] for orders in order]
                session['order'] = order[0]
                session['cart'].clear()
                if order[0] == 3:
                    message = "Order completed! Congratulations! You have unlocked the secret menu!"
                else:
                    message = 'Order completed!'
                return render_template('message.html', message=message, link_name="order", link='ordered')
    return render_template("order.html", cart=session['cart'], message=message, form=form, names=names, prices=prices, total=total)

@app.route('/confirm', methods=['GET', 'POST'])
@login_required
def confirm():
    form = ProceedForm()
    if form.validate_on_submit():
        answer = form.yesno.data
        if answer == True:
            return redirect(url_for('order'))
        else:
            session['cart'].clear()
            db = get_db()
            food = db.execute("SELECT * FROM menu WHERE description != '';").fetchall()
            name = [names['name'] for names in food]
            message = ['Why not?!', 'Order something good!', f'You should definitely try {name[randint(0, len(name)-1)]}!', f'You should definitely try {name[randint(0, len(name)-1)]}!']
            return render_template('message.html', message=message[randint(0, len(message)-1)], link_name="menu", link='menu')
    return render_template('confirm.html', form=form)

@app.route("/ordered", methods=["GET", "POST"])
@login_required
def ordered():
    db = get_db()
    user_id = session['user_id']
    orders = db.execute('''SELECT *  FROM order_info
                        WHERE user_id = ? ORDER BY date_of_order DESC;''', (user_id,)).fetchall()
    order = db.execute('''SELECT * FROM orders as o JOIN menu as m
                        ON o.food_id = m.food_id; ''').fetchall()
    lis = []
    for ordr in orders:
        li = {'id':ordr['id'], 'date_of_order':ordr['date_of_order'][:10], 
            'date_del': ordr['date_del'], 'time_del': ordr['time_del'], 
                'address': ordr['address'], 'info': ordr['info'],
                'status': ordr['status'], 'total': ordr['total']}
        orer = []
        for ordd in order:
            if ordr['id'] == ordd['oi_id']:
                orer.append(f"{ordd['name']}: {ordd['qty']}")
        li['order'] = orer
        lis.append(li)
    return render_template('ordered.html', lis=lis)

@app.route("/xret_menu", methods=["GET", "POST"])
def xret_menu():
    db = get_db()
    menu = db.execute('''SELECT * FROM menu WHERE description = '';''').fetchall()
    return render_template('xmenu.html', menu=menu)

@app.route("/account_settings", methods=['GET', 'POST'])
@login_required
def account_settings():
    db = get_db()
    user_id = session['user_id']
    person = db.execute('''SELECT * FROM users WHERE user_id = ?''', (user_id,)).fetchone()
    return render_template('account_settings.html', person=person)

@app.route("/settings_user", methods=['GET', 'POST'])
def settings_user():
    db = get_db()
    form_user = UserForm()
    user_id = session['user_id']
    person = db.execute('''SELECT * FROM users WHERE user_id = ?''', (user_id,)).fetchone()
    if form_user.validate_on_submit():
        user = form_user.user_id.data
        password = form_user.password.data
        if not check_password_hash(person['password'], password):   
            form_user.password.errors.append("Incorrect password!")
        else: 
            if db.execute(''' SELECT * FROM users WHERE user_id = ?;''',(user,)).fetchone() is not None:
                form_user.user_id.errors.append('User id taken.')
            else:
                db.execute('''UPDATE users SET user_id = ? WHERE user_id = ?;''',(user, user_id))
                db.commit()
                db.execute('''UPDATE reviews SET user_id = ? WHERE user_id = ?;''',(user, user_id))
                db.commit()
                db.execute('''UPDATE requests SET user_id = ? WHERE user_id = ?;''',(user, user_id))
                db.commit()
                db.execute('''UPDATE order_info SET user_id = ? WHERE user_id = ?;''',(user, user_id))
                db.commit()
                message = 'Account Info Updated! User id has been changed.'
                session['user_id'] = user
                return render_template('message.html', message=message, link='account', link_name='account info')
    return render_template('setting_user.html', form_user=form_user, person=person) 

@app.route("/settings_pass", methods=['GET', 'POST'])
def settings_pass():
    db = get_db()
    form_pass = PassForm()
    user_id = session['user_id']
    person = db.execute('''SELECT * FROM users WHERE user_id = ?''', (user_id,)).fetchone()
    if form_pass.validate_on_submit():
        old_password = form_pass.old_password.data
        password = form_pass.npassword.data
        password2 = form_pass.password2.data
        if not check_password_hash(person['password'], old_password):   
            form_pass.old_password.errors.append("Incorrect password!")
        else:
            db.execute('''UPDATE users SET password = ? WHERE user_id = ?;''',(generate_password_hash(password), user_id))
            db.commit()
            message = 'Account Info Updated! Password has been changed.'
            return render_template('message.html', message=message, link='account', link_name='account info')
    return render_template('setting_password.html', form_pass=form_pass, person=person) 


@app.route("/settings_name", methods=['GET', 'POST'])
def settings_name():
    db = get_db()
    form = NameForm()
    user_id = session['user_id']
    person = db.execute('''SELECT * FROM users WHERE user_id = ?''', (user_id,)).fetchone()
    if form.validate_on_submit():
        name = form.fname.data + " " + form.lname.data
        password = form.password.data
        if not check_password_hash(person['password'], password):   
            form.password.errors.append("Incorrect password!")
        else:
            db.execute('''UPDATE users SET name = ? WHERE user_id = ?;''', (name, user_id))
            db.commit()
            message = 'Account Info Updated! Name has been changed.'
            session['name'] = name
            return render_template('message.html', message=message, link='account', link_name='account info')
    return render_template('setting_name.html', form=form, person=person) 


