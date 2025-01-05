from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'python_flask_crud'

mysql = MySQL(app)
@app.route("/")
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def authenticate_user():
    email = request.form['email']
    password = request.form['password']

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, email, role, password FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    
    if user and user[3] == password:
        session['user_id'] = user[0]
        session['user_email'] = user[1]
        session['user_role'] = user[2]
        flash("Login successful!", "success")
        return redirect(url_for('home'))
    else:
        flash("Invalid email or password!", "danger")
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route("/home")
def home():
    if 'user_id' not in session:
        flash("Please log in to access the home page.", "warning")
        return redirect(url_for('login'))
    return render_template('index.html', user_email=session.get('user_email'))

@app.route('/management', methods=["GET", "POST"])
def management():
    if 'user_id' not in session:
        flash("Please log in to access the management page.", "warning")
        return redirect(url_for('login'))

    user_role = session.get('user_role')
    cursor = mysql.connection.cursor()

    if request.method == "POST" and user_role == "regular":
        name = request.form['name']
        description = request.form['description']
        price = int(request.form['price'])
        stock = int(request.form['stock'])
        category = request.form['category']
        status = request.form['status']

        try:
            cursor.execute("INSERT INTO products (name, description, price, stock, category, status) VALUES (%s, %s, %s, %s, %s, %s)",
                           (name, description, price, stock, category, status))
            mysql.connection.commit()
            flash("Product added successfully!", "success")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Failed to add product: {e}", "danger")
        return redirect(url_for('management'))

    if request.method == "POST" and user_role == "admin":
        fullname = request.form['fullname']
        email = request.form['email']
        address = request.form['address']
        phone = request.form['phone']
        account_status = request.form['account_status']

        try:
            cursor.execute("INSERT INTO customers (fullname, email, address, phone_number, account_status, registration_date) VALUES (%s, %s, %s, %s, %s, %s)",
                           (fullname, email, address, phone, account_status, datetime.now()))
            mysql.connection.commit()
            flash("Customer added successfully!", "success")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Failed to add customer: {e}", "danger")
        return redirect(url_for('management'))

    if user_role == "admin":
        cursor.execute("SELECT customer_id, fullname, email, address, phone_number, account_status, registration_date FROM customers")
        customers = cursor.fetchall()

        customer_list = [
            {
                "customer_id": c[0],
                "fullname": c[1],
                "email": c[2],
                "address": c[3],
                "phone_number": c[4],
                "account_status": c[5],
                "registration_date": c[6],
            }
            for c in customers
        ]
        return render_template('management_admin.html', customers=customer_list)

    elif user_role == "regular":
        cursor.execute("SELECT product_id, name, description, price, stock, category, status FROM products")
        products = cursor.fetchall()

        product_list = [
            {
                "product_id": p[0],
                "name": p[1],
                "description": p[2],
                "price": p[3],
                "stock": p[4],
                "category": p[5],
                "status": p[6],
            }
            for p in products
        ]
        return render_template('management_regular.html', products=product_list)

    flash("Unauthorized access! Please contact support.", "danger")
    return redirect(url_for('home'))

@app.route("/about")
def about():
    if 'user_id' not in session:
        flash("Please log in to access the about page.", "warning")
        return redirect(url_for('login'))
    return render_template('about.html', user_email=session.get('user_email'))



@app.route('/update_product', methods=['POST'])
def update_product():
    product_id = request.form['product_id']
    name = request.form['name']
    description = request.form['description']
    price = request.form['price']
    stock = request.form['stock']
    category = request.form['category']
    status = request.form['status']

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""
            UPDATE products 
            SET name=%s, description=%s, price=%s, stock=%s, category=%s, status=%s 
            WHERE product_id=%s
        """, (name, description, price, stock, category, status, product_id))
        mysql.connection.commit()
        flash("Product updated successfully!", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Error updating product: {e}", "danger")
    return redirect(url_for('management'))

@app.route('/update_customer', methods=['POST'])
def update_customer():
    customer_id = request.form['customer_id']
    fullname = request.form['fullname']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    account_status = request.form['account_status']
    registration_date = request.form['registration_date']  # Capture registration date

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""
            UPDATE customers 
            SET fullname=%s, email=%s, phone_number=%s, address=%s, account_status=%s, registration_date=%s
            WHERE customer_id=%s
        """, (fullname, email, phone, address, account_status, registration_date, customer_id))
        mysql.connection.commit()
        flash("Customer updated successfully!", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Error updating customer: {e}", "danger")
    finally:
        cursor.close()
    return redirect(url_for('management'))


@app.route('/delete_product', methods=['POST'])
def delete_product():
    product_id = request.form['product_id']

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("DELETE FROM products WHERE product_id=%s", (product_id,))
        mysql.connection.commit()
        flash("Product deleted successfully!", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Error deleting product: {e}", "danger")
    return redirect(url_for('management'))

@app.route('/delete_customer', methods=['POST'])
def delete_customer():
    customer_id = request.form['customer_id']

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("DELETE FROM customers WHERE customer_id=%s", (customer_id,))
        mysql.connection.commit()
        flash("Customer deleted successfully!", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Error deleting customer: {e}", "danger")
    return redirect(url_for('management'))

@app.route("/test")
def test_db():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT 1")
        return "Database connection successful!"
    except Exception as e:
        return f"Database connection failed: {e}"

if __name__ == '__main__':
    app.run(debug=True)
