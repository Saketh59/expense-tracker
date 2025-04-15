from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import os
import json
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import csv
import io
# Optionally you'd use a library for OCR functionality
# import pytesseract
# from PIL import Image

app = Flask(__name__,static_folder='static', template_folder='templates')
app.secret_key = 'your_secret_key_here'  # Change this in production

# Database setup
def get_db_connection():
    conn = sqlite3.connect('finance_tracker.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        subcategory TEXT,
        note TEXT,
        amount REAL NOT NULL,
        mode TEXT DEFAULT 'manual',
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html')

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    
    # Validate data
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    username = data.get('username')
    email = data.get('email')
    password = generate_password_hash(data.get('password'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                      (username, email, password))
        conn.commit()
        return jsonify({'message': 'Signup successful!'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username or email already exists'}), 400
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    user = cursor.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({'message': 'Login successful!'}), 200
    
    return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/user_info')
def user_info():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    return jsonify({'username': session.get('username')})

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    category = request.form.get('category')
    subcategory = request.form.get('subcategory', '')
    note = request.form.get('note', '')
    amount = request.form.get('amount')
    
    if not category or not amount:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        amount = float(amount)
    except ValueError:
        return jsonify({'error': 'Amount must be a number'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO transactions (user_id, category, subcategory, note, amount)
    VALUES (?, ?, ?, ?, ?)
    ''', (session['user_id'], category, subcategory, note, amount))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Transaction added successfully'})

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be a CSV'}), 400
    
    try:
        # Read CSV file
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        count = 0
        for row in csv_reader:
            # Adjust these field names to match your CSV structure
            category = row.get('category', 'Uncategorized')
            subcategory = row.get('subcategory', '')
            note = row.get('note', '')
            amount = float(row.get('amount', 0))
            
            cursor.execute('''
            INSERT INTO transactions (user_id, category, subcategory, note, amount, mode)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (session['user_id'], category, subcategory, note, amount, 'csv'))
            
            count += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': f'Successfully imported {count} transactions'})
    
    except Exception as e:
        return jsonify({'error': f'Error processing CSV: {str(e)}'}), 400

@app.route('/upload_receipt', methods=['POST'])
def upload_receipt():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # In a real application, you would:
    # 1. Save the file temporarily
    # 2. Process it with OCR
    # 3. Extract transaction data
    # 4. Save to database
    
    # This is just a placeholder - in a real app you'd use OCR
    # Example with pytesseract (commented out):
    # image = Image.open(file.stream)
    # text = pytesseract.image_to_string(image)
    # Process the text to extract transaction data
    
    # For now, we'll just add a placeholder transaction
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO transactions (user_id, category, amount, mode)
    VALUES (?, ?, ?, ?)
    ''', (session['user_id'], 'Receipt Upload', 0.00, 'receipt'))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Receipt uploaded. Implement OCR to extract data.'})

@app.route('/get_transactions')
def get_transactions():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    transactions = cursor.execute('''
    SELECT * FROM transactions 
    WHERE user_id = ? 
    ORDER BY date DESC
    ''', (session['user_id'],)).fetchall()
    
    # Convert to list of dicts
    transaction_list = []
    for txn in transactions:
        transaction_list.append({
            'id': txn['id'],
            'category': txn['category'],
            'subcategory': txn['subcategory'],
            'note': txn['note'],
            'amount': txn['amount'],
            'mode': txn['mode'],
            'date': txn['date']
        })
    
    # Simple budget advice (in a real app, this would be more sophisticated)
    total_spent = sum(txn['amount'] for txn in transaction_list)
    budget_advice = "No transactions yet" if not transaction_list else f"Total spent: ${total_spent:.2f}"
    
    conn.close()
    
    return jsonify({
        'transactions': transaction_list,
        'budget_advice': budget_advice
    })

@app.route('/get_budget_advice')
def get_budget_advice():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    transactions = cursor.execute('''
    SELECT category, SUM(amount) as total
    FROM transactions 
    WHERE user_id = ?
    GROUP BY category
    ORDER BY total DESC
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    
    if not transactions:
        return jsonify({'advice': 'No transaction data available for budget analysis.'})
    
    # Generate simple advice based on spending patterns
    # In a real app, this would be more sophisticated
    highest_category = transactions[0]['category']
    highest_amount = transactions[0]['total']
    
    advice = f"Your highest spending category is '{highest_category}' at ${highest_amount:.2f}."
    
    if len(transactions) > 1:
        advice += f" Consider reducing spending in this category."
    
    return jsonify({'advice': advice})



if __name__ == '__main__':
    app.run(debug=True)