"""
BIGBREW Management System
Responsive mobile-friendly web application using Python + Flask + MySQL.

Run on PC:
    python -m pip install -r requirements.txt
    python main.py

Open on the same PC:
    http://127.0.0.1:5000

Open on a phone connected to the SAME Wi-Fi:
    http://YOUR-COMPUTER-LAN-IP:5000

Set your MySQL password in DB_CONFIG before running.
"""
from flask import Flask, request, redirect, url_for, session, flash, render_template_string
from functools import wraps
from decimal import Decimal, InvalidOperation
from datetime import datetime
import hashlib
import socket
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_KEY"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "bigbrew"
}

def pw_hash(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

class DB:
    def __init__(self):
        cfg = dict(DB_CONFIG)
        dbname = cfg.pop("database")
        server = mysql.connector.connect(**cfg)
        cur = server.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{dbname}`")
        cur.close()
        server.close()
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.setup()

    def cursor(self, dictionary=True):
        if not self.conn.is_connected():
            self.conn.reconnect(attempts=3, delay=1)
        return self.conn.cursor(dictionary=dictionary)

    def setup(self):
        cur = self.cursor(False)
        ddl = [
            """CREATE TABLE IF NOT EXISTS users(
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(64) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'cashier',
                is_active BOOLEAN NOT NULL DEFAULT TRUE)""",
            """CREATE TABLE IF NOT EXISTS categories(
                category_id INT AUTO_INCREMENT PRIMARY KEY,
                category_name VARCHAR(80) UNIQUE NOT NULL)""",
            """CREATE TABLE IF NOT EXISTS products(
                product_id INT AUTO_INCREMENT PRIMARY KEY,
                product_code VARCHAR(40) UNIQUE NOT NULL,
                product_name VARCHAR(120) NOT NULL,
                category_id INT,
                price DECIMAL(10,2) NOT NULL,
                is_available BOOLEAN NOT NULL DEFAULT TRUE,
                FOREIGN KEY(category_id) REFERENCES categories(category_id))""",
            """CREATE TABLE IF NOT EXISTS ingredients(
                ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
                ingredient_name VARCHAR(100) UNIQUE NOT NULL,
                unit VARCHAR(20) NOT NULL,
                quantity DECIMAL(10,2) NOT NULL DEFAULT 0,
                reorder_level DECIMAL(10,2) NOT NULL DEFAULT 0)""",
            """CREATE TABLE IF NOT EXISTS product_recipes(
                recipe_id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT NOT NULL,
                ingredient_id INT NOT NULL,
                quantity_used DECIMAL(10,2) NOT NULL,
                UNIQUE KEY uq_recipe(product_id,ingredient_id),
                FOREIGN KEY(product_id) REFERENCES products(product_id),
                FOREIGN KEY(ingredient_id) REFERENCES ingredients(ingredient_id))""",
            """CREATE TABLE IF NOT EXISTS orders(
                order_id INT AUTO_INCREMENT PRIMARY KEY,
                order_datetime DATETIME NOT NULL,
                cashier_id INT,
                total_amount DECIMAL(10,2) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'COMPLETED',
                FOREIGN KEY(cashier_id) REFERENCES users(user_id))""",
            """CREATE TABLE IF NOT EXISTS order_items(
                order_item_id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT NOT NULL,
                product_id INT NOT NULL,
                product_name_at_sale VARCHAR(120) NOT NULL,
                quantity INT NOT NULL,
                unit_price_at_sale DECIMAL(10,2) NOT NULL,
                line_subtotal DECIMAL(10,2) NOT NULL,
                FOREIGN KEY(order_id) REFERENCES orders(order_id),
                FOREIGN KEY(product_id) REFERENCES products(product_id))""",
            """CREATE TABLE IF NOT EXISTS payments(
                payment_id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT UNIQUE NOT NULL,
                payment_method VARCHAR(20) NOT NULL DEFAULT 'CASH',
                amount_received DECIMAL(10,2) NOT NULL,
                change_amount DECIMAL(10,2) NOT NULL,
                FOREIGN KEY(order_id) REFERENCES orders(order_id))""",
            """CREATE TABLE IF NOT EXISTS stock_movements(
                movement_id INT AUTO_INCREMENT PRIMARY KEY,
                ingredient_id INT NOT NULL,
                movement_type VARCHAR(20) NOT NULL,
                quantity DECIMAL(10,2) NOT NULL,
                movement_datetime DATETIME NOT NULL,
                notes VARCHAR(255),
                FOREIGN KEY(ingredient_id) REFERENCES ingredients(ingredient_id))"""
        ]
        for sql in ddl:
            cur.execute(sql)
        self.conn.commit()
        cur.close()
        self.seed_menu()

    def seed_menu(self):
        cur = self.cursor(False)
        cur.execute(
            "INSERT IGNORE INTO users(username,password_hash,role) VALUES(%s,%s,'admin')",
            ("admin", pw_hash("admin123"))
        )
        cats = ["Milk Tea", "Coffee", "Fruit Tea", "BROSTY", "Praf", "Add-ons"]
        for category in cats:
            cur.execute("INSERT IGNORE INTO categories(category_name) VALUES(%s)", (category,))
        cur.execute("SELECT category_id,category_name FROM categories")
        ids = {name: cid for cid, name in cur.fetchall()}

        milk = ["Dark Choco","Cookies & Cream","Okinawa","Wintermelon","Cheesecake","Matcha",
                "Chocolate","Red Velvet","Salted Caramel","Choco Kisses","Taro","Strawberry"]
        coffee = ["Brusko","Mocha","Macchiato","Vanilla","Caramel","Matcha","Fudge","Spanish Latte"]
        fruit = ["Lychee","Green Apple","Blueberry","Lemon","Strawberry","Kiwi","Mango","Honey Peach"]
        praf = ["Coffee Jelly","Caramel Macch","Mocha","Vanilla Coffee","Java Chip","Cheesecake",
                "Cookies & Cream","Creamy Avocado","Chocolate","Matcha","Strawberry","Taro"]
        brosty = fruit[:]
        products = []
        def add(cat, code, name, price):
            products.append((code, name, ids[cat], price))
        for i, name in enumerate(milk, 1):
            add("Milk Tea", f"MT{i:03}R", f"{name} (Regular)", 29)
            add("Milk Tea", f"MT{i:03}L", f"{name} (Large)", 39)
        for i, name in enumerate(coffee, 1):
            add("Coffee", f"CF{i:03}IR", f"{name} Iced (Regular)", 29)
            add("Coffee", f"CF{i:03}IL", f"{name} Iced (Large)", 39)
            add("Coffee", f"CF{i:03}H", f"{name} Hot", 39)
        for i, name in enumerate(fruit, 1):
            add("Fruit Tea", f"FT{i:03}R", f"{name} (Regular)", 29)
            add("Fruit Tea", f"FT{i:03}L", f"{name} (Large)", 39)
        for i, name in enumerate(brosty, 1):
            add("BROSTY", f"BR{i:03}R", f"{name} (Regular)", 49)
            add("BROSTY", f"BR{i:03}L", f"{name} (Large)", 59)
        for i, name in enumerate(praf, 1):
            add("Praf", f"PR{i:03}R", f"{name} (Regular)", 49)
            add("Praf", f"PR{i:03}L", f"{name} (Large)", 59)
        addons = ["Pearl","Crystal","Cream Cheese","Cream Puff","Cheesecake",
                  "Crushed Oreo","Coffee Jelly","Whipped Cream"]
        for i, name in enumerate(addons, 1):
            add("Add-ons", f"AD{i:03}", f"Add-on: {name}", 9)
        add("Add-ons", "AD009", "Extra Shot", 5)

        # Upsert menu rows; preserve old products and completed sales history.
        cur.executemany(
            """INSERT INTO products(product_code,product_name,category_id,price,is_available)
               VALUES(%s,%s,%s,%s,TRUE)
               ON DUPLICATE KEY UPDATE product_name=VALUES(product_name),
               category_id=VALUES(category_id),price=VALUES(price),is_available=TRUE""",
            products
        )
        # Deactivate only previous sample items, not this poster's menu.
        new_codes = [x[0] for x in products]
        placeholders = ",".join(["%s"] * len(new_codes))
        cur.execute(f"UPDATE products SET is_available=FALSE WHERE product_code NOT IN ({placeholders})", new_codes)
        ingredients = [
            ("Coffee Beans","g",5000,500),("Fresh Milk","ml",10000,1000),
            ("Caramel Syrup","ml",2000,200),("Tea Powder","g",2000,200),
            ("Fruit Syrup","ml",3000,300),("Pearls","g",2000,200)
        ]
        for item in ingredients:
            cur.execute(
                """INSERT IGNORE INTO ingredients(ingredient_name,unit,quantity,reorder_level)
                   VALUES(%s,%s,%s,%s)""", item
            )
        self.conn.commit()
        cur.close()

    def login(self, username, password):
        cur = self.cursor()
        cur.execute(
            "SELECT user_id,username,role FROM users WHERE username=%s AND password_hash=%s AND is_active=1",
            (username, pw_hash(password))
        )
        row = cur.fetchone()
        cur.close()
        return row

    def register(self, username, password):
        if len(username) < 3:
            raise ValueError("Username must contain at least 3 characters.")
        if len(password) < 6:
            raise ValueError("Password must contain at least 6 characters.")
        cur = self.cursor(False)
        try:
            cur.execute(
                "INSERT INTO users(username,password_hash,role) VALUES(%s,%s,'cashier')",
                (username, pw_hash(password))
            )
            self.conn.commit()
        finally:
            cur.close()

    def summary(self):
        cur = self.cursor()
        cur.execute("""SELECT COALESCE(SUM(total_amount),0) total,COUNT(*) transactions
                       FROM orders WHERE DATE(order_datetime)=CURDATE()""")
        summary = cur.fetchone()
        cur.execute("""SELECT ingredient_name,quantity,unit,reorder_level
                       FROM ingredients WHERE quantity<=reorder_level ORDER BY ingredient_name""")
        low = cur.fetchall()
        cur.close()
        return summary, low

    def products(self, category="", search=""):
        cur = self.cursor()
        sql = """SELECT p.product_id,p.product_code,p.product_name,p.price,c.category_name
                 FROM products p JOIN categories c USING(category_id)
                 WHERE p.is_available=1"""
        args = []
        if category:
            sql += " AND c.category_name=%s"
            args.append(category)
        if search:
            sql += " AND p.product_name LIKE %s"
            args.append(f"%{search}%")
        sql += " ORDER BY c.category_name,p.product_name"
        cur.execute(sql, args)
        rows = cur.fetchall()
        cur.close()
        return rows

    def categories(self):
        cur = self.cursor()
        cur.execute("SELECT category_name FROM categories ORDER BY category_id")
        rows = [x["category_name"] for x in cur.fetchall()]
        cur.close()
        return rows

    def inventory(self):
        cur = self.cursor()
        cur.execute("SELECT * FROM ingredients ORDER BY ingredient_name")
        rows = cur.fetchall()
        cur.close()
        return rows

    def restock(self, ingredient_id, amount):
        cur = self.cursor(False)
        try:
            self.conn.start_transaction()
            cur.execute("UPDATE ingredients SET quantity=quantity+%s WHERE ingredient_id=%s",
                        (amount, ingredient_id))
            cur.execute("""INSERT INTO stock_movements
                (ingredient_id,movement_type,quantity,movement_datetime,notes)
                VALUES(%s,'RESTOCK',%s,%s,'Manual restock')""",
                (ingredient_id, amount, datetime.now()))
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def checkout(self, cart, cash, cashier_id):
        total = sum((Decimal(str(x["price"])) * x["qty"] for x in cart), Decimal("0.00"))
        cash = Decimal(str(cash))
        if cash < total:
            raise ValueError("Insufficient cash payment.")
        cur = self.cursor()
        try:
            self.conn.start_transaction()
            for item in cart:
                cur.execute("""SELECT pr.ingredient_id,pr.quantity_used,i.ingredient_name,i.quantity
                    FROM product_recipes pr JOIN ingredients i USING(ingredient_id)
                    WHERE pr.product_id=%s FOR UPDATE""", (item["id"],))
                for recipe in cur.fetchall():
                    needed = Decimal(str(recipe["quantity_used"])) * item["qty"]
                    if Decimal(str(recipe["quantity"])) < needed:
                        raise ValueError(f"Not enough {recipe['ingredient_name']} in stock.")
                    cur.execute("UPDATE ingredients SET quantity=quantity-%s WHERE ingredient_id=%s",
                                (needed, recipe["ingredient_id"]))
                    cur.execute("""INSERT INTO stock_movements
                        (ingredient_id,movement_type,quantity,movement_datetime,notes)
                        VALUES(%s,'SALE',%s,%s,%s)""",
                        (recipe["ingredient_id"], needed, datetime.now(), f"Sale: {item['name']}"))
            cur.execute("INSERT INTO orders(order_datetime,cashier_id,total_amount) VALUES(%s,%s,%s)",
                        (datetime.now(), cashier_id, total))
            order_id = cur.lastrowid
            for item in cart:
                subtotal = Decimal(str(item["price"])) * item["qty"]
                cur.execute("""INSERT INTO order_items
                    (order_id,product_id,product_name_at_sale,quantity,unit_price_at_sale,line_subtotal)
                    VALUES(%s,%s,%s,%s,%s,%s)""",
                    (order_id,item["id"],item["name"],item["qty"],item["price"],subtotal))
            change = cash - total
            cur.execute("""INSERT INTO payments(order_id,payment_method,amount_received,change_amount)
                           VALUES(%s,'CASH',%s,%s)""", (order_id,cash,change))
            self.conn.commit()
            return order_id,total,change
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def sales(self):
        cur = self.cursor()
        cur.execute("""SELECT o.order_id,o.order_datetime,u.username,o.total_amount,
                       p.amount_received,p.change_amount FROM orders o
                       LEFT JOIN users u ON o.cashier_id=u.user_id
                       LEFT JOIN payments p USING(order_id)
                       ORDER BY o.order_id DESC LIMIT 200""")
        rows = cur.fetchall()
        cur.close()
        return rows

    def report(self):
        cur = self.cursor()
        cur.execute("""SELECT DATE(order_datetime) sales_date,COUNT(*) transactions,
                       SUM(total_amount) total FROM orders GROUP BY DATE(order_datetime)
                       ORDER BY sales_date DESC LIMIT 30""")
        rows = cur.fetchall()
        cur.close()
        return rows

try:
    db = DB()
    DB_ERROR = None
except Exception as exc:
    db = None
    DB_ERROR = str(exc)

BASE = r"""
<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }} | BIGBREW</title>
<style>
:root{--brown:#573522;--orange:#c56b18;--cream:#f7f0e7;--paper:#fffdf9;--ink:#30251e}
*{box-sizing:border-box}body{margin:0;background:var(--cream);color:var(--ink);font-family:Arial,sans-serif}
header{background:var(--brown);color:white;padding:15px 22px;display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}
.brand{font-size:26px;font-weight:900;letter-spacing:1px}.sub{font-size:12px;color:#f4d9bd}
nav{display:flex;gap:8px;flex-wrap:wrap;padding:12px 18px;background:#eadbca}
nav a,.btn{background:var(--brown);color:white;text-decoration:none;padding:10px 14px;border:0;border-radius:8px;font-weight:bold;display:inline-block;cursor:pointer}
nav a:hover,.btn:hover{background:var(--orange)}
main{max-width:1200px;margin:20px auto;padding:0 16px}
h1{color:var(--brown);margin:8px 0 4px}.muted{color:#82644d}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}
.card{background:var(--paper);padding:18px;border-radius:14px;box-shadow:0 2px 9px #5b392615;margin:10px 0}
.metric{font-size:27px;font-weight:800;color:var(--brown);margin-top:8px}
input,select{padding:11px;border:1px solid #c9b8a6;border-radius:7px;width:100%;font-size:15px;background:white}
label{font-weight:bold;font-size:13px;display:block;margin:9px 0 5px}
table{width:100%;border-collapse:collapse;background:white;border-radius:10px;overflow:hidden}
th,td{text-align:left;padding:11px;border-bottom:1px solid #eee;font-size:14px}th{background:#eadbca;color:var(--brown)}
.tablewrap{overflow-x:auto}.product{display:flex;justify-content:space-between;gap:10px;align-items:center}
.price{font-weight:bold;color:var(--orange);white-space:nowrap}
.flash{padding:12px;border-radius:8px;background:#fff1d9;margin:10px 0}
.auth{max-width:420px;margin:45px auto;padding:28px}
.auth h1{text-align:center;font-size:34px}.auth .btn{width:100%;margin-top:16px}
.row{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.actions{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
small{color:#82644d}
@media(max-width:650px){header{padding:13px}.brand{font-size:22px}nav{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;padding:8px}nav a{text-align:center;padding:10px 4px;font-size:12px}main{padding:0 10px;margin:12px auto}.card{padding:14px}th,td{padding:8px;font-size:12px}.row{grid-template-columns:1fr}.auth{margin:20px 10px;padding:20px}}
</style></head><body>
<header><div><div class="brand">☕ BIGBREW</div><div class="sub">Coffee • Milk Tea • Fruit Tea • More</div></div>
{% if user %}<div>Hi, {{ user.username }} · {{ user.role }}</div>{% endif %}</header>
{% if user %}<nav>
<a href="{{ url_for('dashboard') }}">Dashboard</a><a href="{{ url_for('pos') }}">POS</a>
<a href="{{ url_for('menu') }}">Menu</a><a href="{{ url_for('inventory_page') }}">Inventory</a>
<a href="{{ url_for('sales_page') }}">Sales</a><a href="{{ url_for('reports_page') }}">Reports</a>
<a href="{{ url_for('logout') }}">Log out</a></nav>{% endif %}
<main>
{% with messages=get_flashed_messages() %}{% for message in messages %}<div class="flash">{{ message }}</div>{% endfor %}{% endwith %}
{{ body|safe }}
</main></body></html>
"""

def page(title, body, **context):
    return render_template_string(BASE, title=title, body=render_template_string(body, **context),
                                  user=session.get("user"))

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    return redirect(url_for("dashboard") if session.get("user") else url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    if DB_ERROR:
        return page("Database setup", f"<div class='card'><h2>MySQL connection failed</h2><p>{DB_ERROR}</p><p>Check DB_CONFIG and make sure MySQL Server is running.</p></div>")
    if request.method == "POST":
        user = db.login(request.form.get("username","").strip(), request.form.get("password",""))
        if user:
            session["user"] = user
            return redirect(url_for("dashboard"))
        flash("Incorrect username or password.")
    body = """
    <div class="card auth"><h1>☕ BIGBREW</h1><p class="muted" style="text-align:center">Coffee Shop Management System</p>
    <form method="post"><label>Username</label><input name="username" required autocomplete="username">
    <label>Password</label><input name="password" type="password" required autocomplete="current-password">
    <button class="btn" type="submit">SIGN IN</button></form>
    <p style="text-align:center">No account yet? <a href="{{ url_for('signup') }}">Create an account</a></p>
    <small>Demo admin: admin / admin123</small></div>"""
    return page("Sign in", body)

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        try:
            db.register(request.form.get("username","").strip(), request.form.get("password",""))
            flash("Account created! You can now sign in.")
            return redirect(url_for("login"))
        except Error:
            flash("That username may already exist. Please choose another.")
        except ValueError as exc:
            flash(str(exc))
    body = """
    <div class="card auth"><h1>Join BIGBREW</h1><p class="muted">Create your staff account</p>
    <form method="post"><label>Username</label><input name="username" required minlength="3">
    <label>Password</label><input name="password" type="password" required minlength="6">
    <button class="btn" type="submit">SIGN UP</button></form>
    <p style="text-align:center"><a href="{{ url_for('login') }}">Back to sign in</a></p></div>"""
    return page("Sign up", body)

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    summary, low = db.summary()
    body = """
    <h1>Dashboard</h1><p class="muted">Welcome to BIGBREW Management System.</p>
    <div class="grid"><div class="card">Today's Sales<div class="metric">₱{{ '%.2f'|format(summary.total) }}</div></div>
    <div class="card">Transactions Today<div class="metric">{{ summary.transactions }}</div></div>
    <div class="card">Menu Items<div class="metric">{{ product_count }}</div></div></div>
    <div class="card"><h3>Low-stock ingredients</h3>{% if low %}<div class="tablewrap"><table><tr><th>Ingredient</th><th>Stock</th><th>Unit</th><th>Reorder at</th></tr>
    {% for x in low %}<tr><td>{{ x.ingredient_name }}</td><td>{{ x.quantity }}</td><td>{{ x.unit }}</td><td>{{ x.reorder_level }}</td></tr>{% endfor %}</table></div>{% else %}<p>All ingredients are above reorder level.</p>{% endif %}</div>"""
    return page("Dashboard", body, summary=summary, low=low, product_count=len(db.products()))

@app.route("/menu")
@login_required
def menu():
    category = request.args.get("category","")
    search = request.args.get("q","")
    products = db.products(category, search)
    categories = db.categories()
    body = """
    <h1>BIGBREW Menu</h1><p class="muted">Menu and prices based on your supplied poster.</p>
    <form class="card" method="get"><div class="row"><div><label>Category</label><select name="category"><option value="">All categories</option>
    {% for c in categories %}<option {% if c==selected %}selected{% endif %}>{{ c }}</option>{% endfor %}</select></div>
    <div><label>Search flavor</label><input name="q" value="{{ search }}" placeholder="Search product"></div></div><button class="btn" style="margin-top:12px">Filter</button></form>
    <div class="grid">{% for p in products %}<div class="card product"><div><b>{{ p.product_name }}</b><br><small>{{ p.category_name }}</small></div><span class="price">₱{{ '%.2f'|format(p.price) }}</span></div>{% endfor %}</div>"""
    return page("Menu", body, products=products, categories=categories, selected=category, search=search)

@app.route("/pos", methods=["GET","POST"])
@login_required
def pos():
    products = db.products(request.args.get("category",""), request.args.get("q",""))
    if request.method == "POST":
        try:
            ids = request.form.getlist("product_id")
            quantities = request.form.getlist("quantity")
            cart = []
            product_map = {str(p["product_id"]):p for p in db.products()}
            for pid, qty_text in zip(ids, quantities):
                qty = int(qty_text)
                if qty > 0 and pid in product_map:
                    p = product_map[pid]
                    cart.append({"id":p["product_id"],"name":p["product_name"],
                                 "price":Decimal(str(p["price"])),"qty":qty})
            if not cart:
                raise ValueError("Please select at least one item and enter a valid quantity.")
            cash = Decimal(request.form.get("cash","0"))
            oid,total,change = db.checkout(cart,cash,session["user"]["user_id"])
            flash(f"Sale completed! Order #{oid} · Total ₱{total:.2f} · Change ₱{change:.2f}")
            return redirect(url_for("pos"))
        except (ValueError, InvalidOperation) as exc:
            flash(str(exc))
        except Error as exc:
            flash(f"Database error: {exc}")
    categories = db.categories()
    body = """
    <h1>Point of Sale</h1><p class="muted">Select menu items, quantity, and cash received.</p>
    <form method="get" class="card"><label>Search menu</label><input name="q" placeholder="Type a flavor" value="{{ search }}">
    <label>Category</label><select name="category"><option value="">All categories</option>{% for c in categories %}<option>{{ c }}</option>{% endfor %}</select>
    <button class="btn" style="margin-top:10px">Search</button></form>
    <form method="post"><div class="grid">{% for p in products %}<div class="card">
    <b>{{ p.product_name }}</b><div class="price">₱{{ '%.2f'|format(p.price) }}</div>
    <input type="hidden" name="product_id" value="{{ p.product_id }}"><label>Quantity</label><input type="number" name="quantity" value="0" min="0" inputmode="numeric"></div>{% endfor %}</div>
    <div class="card"><label>Cash received (₱)</label><input name="cash" type="number" min="0" step="0.01" required inputmode="decimal">
    <button class="btn" style="width:100%;margin-top:12px">COMPLETE CASH SALE</button></div></form>"""
    return page("POS", body, products=products, categories=categories, search=request.args.get("q",""))

@app.route("/inventory", methods=["GET","POST"])
@login_required
def inventory_page():
    if request.method == "POST":
        try:
            amount = Decimal(request.form.get("amount","0"))
            iid = int(request.form.get("ingredient_id","0"))
            if amount <= 0: raise ValueError("Restock amount must be greater than zero.")
            db.restock(iid, amount)
            flash("Inventory restocked successfully.")
            return redirect(url_for("inventory_page"))
        except (ValueError, InvalidOperation, Error) as exc:
            flash(str(exc))
    ingredients = db.inventory()
    body = """
    <h1>Inventory</h1><div class="card"><h3>Record restock</h3><form method="post">
    <label>Ingredient</label><select name="ingredient_id">{% for x in ingredients %}<option value="{{ x.ingredient_id }}">{{ x.ingredient_name }}</option>{% endfor %}</select>
    <label>Quantity to add</label><input type="number" step="0.01" min="0.01" name="amount" required>
    <button class="btn" style="margin-top:12px">Save restock</button></form></div>
    <div class="card tablewrap"><table><tr><th>Ingredient</th><th>Stock</th><th>Unit</th><th>Reorder level</th></tr>
    {% for x in ingredients %}<tr><td>{{ x.ingredient_name }}</td><td>{{ x.quantity }}</td><td>{{ x.unit }}</td><td>{{ x.reorder_level }}</td></tr>{% endfor %}</table></div>"""
    return page("Inventory", body, ingredients=ingredients)

@app.route("/sales")
@login_required
def sales_page():
    sales = db.sales()
    body = """
    <h1>Sales History</h1><div class="card tablewrap"><table><tr><th>Order</th><th>Date</th><th>Cashier</th><th>Total</th><th>Cash</th><th>Change</th></tr>
    {% for x in sales %}<tr><td>#{{ x.order_id }}</td><td>{{ x.order_datetime }}</td><td>{{ x.username or '-' }}</td><td>₱{{ x.total_amount }}</td><td>₱{{ x.amount_received }}</td><td>₱{{ x.change_amount }}</td></tr>{% endfor %}</table></div>"""
    return page("Sales", body, sales=sales)

@app.route("/reports")
@login_required
def reports_page():
    rows = db.report()
    body = """
    <h1>Sales Reports</h1><div class="card tablewrap"><table><tr><th>Date</th><th>Transactions</th><th>Total Sales</th></tr>
    {% for x in rows %}<tr><td>{{ x.sales_date }}</td><td>{{ x.transactions }}</td><td>₱{{ x.total }}</td></tr>{% endfor %}</table></div>"""
    return page("Reports", body, rows=rows)

def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8",80))
        return s.getsockname()[0]
    except OSError:
        return "YOUR-PC-IP"
    finally:
        s.close()

if __name__ == "__main__":
    print("\\nBIGBREW is starting...")
    print("Computer: http://127.0.0.1:5000")
    print(f"Phone on same Wi-Fi: http://{local_ip()}:5000")
    print("Press CTRL+C to stop the server.\\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
