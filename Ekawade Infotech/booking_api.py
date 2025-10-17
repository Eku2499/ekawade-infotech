try:
    import openpyxl
except Exception:
    openpyxl = None
from flask import Flask, request, jsonify, session, redirect, url_for, render_template_string
from flask_cors import CORS
import os
import sqlite3
import math
from typing import List, Tuple
from flask import send_from_directory

app = Flask(__name__)
# Allow cross-origin requests from the frontend
CORS(app)

# Paths
ROOT = os.path.dirname(__file__)
EXCEL_FILE = os.path.join(ROOT, 'booking.xlsx')
DB_FILE = os.environ.get('BOOKING_DB', os.path.join(ROOT, 'bookings.db'))

CREATE_TABLE_SQL = '''
CREATE TABLE IF NOT EXISTS bookings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  appointment_date TEXT NOT NULL,
  phone TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
'''


def get_db_connection():
    db_path = os.environ.get('BOOKING_DB', os.path.join(ROOT, 'bookings.db'))
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


# --- Simple session-based admin auth configuration ---
# In production set SECRET_KEY, ADMIN_USER and ADMIN_PASS via environment variables
app.secret_key = os.environ.get('SECRET_KEY', 'change-me-in-production')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'password')
# Enable admin auth only when ADMIN_AUTH=1 is set. Default off for developer convenience/tests.
ADMIN_AUTH_ENABLED = os.environ.get('ADMIN_AUTH', '0') == '1'

def login_required_api(f):
    """Decorator for JSON/API endpoints. Returns 401 JSON if not authenticated."""
    from functools import wraps
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not ADMIN_AUTH_ENABLED:
            return f(*args, **kwargs)
        if not session.get('admin_authenticated'):
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return wrapped

def login_required_html(f):
    """Decorator for pages - redirects to login if not authenticated."""
    from functools import wraps
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not ADMIN_AUTH_ENABLED:
            return f(*args, **kwargs)
        if not session.get('admin_authenticated'):
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return wrapped


LOGIN_HTML = '''
<!doctype html>
<html>
<head><meta charset="utf-8"><title>Admin Login</title></head>
<body style="font-family:Arial,Helvetica,sans-serif;max-width:420px;margin:3rem auto;">
  <h2>Admin Login</h2>
  {% if error %}<div style="color:red">{{ error }}</div>{% endif %}
  <form method="post">
    <input name="username" placeholder="Username" style="width:100%;padding:8px;margin:6px 0" required>
    <input name="password" type="password" placeholder="Password" style="width:100%;padding:8px;margin:6px 0" required>
    <input type="hidden" name="next" value="{{ next }}">
    <button type="submit" style="padding:8px 12px;background:#0055aa;color:white;border:none;border-radius:4px">Login</button>
  </form>
  <p style="margin-top:1rem;font-size:0.9rem;color:#666">Set ADMIN_USER and ADMIN_PASS environment variables in production.</p>
</body>
</html>
'''


@app.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next') or url_for('admin_page')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['admin_authenticated'] = True
            return redirect(request.form.get('next') or url_for('admin_page'))
        else:
            return render_template_string(LOGIN_HTML, error='Invalid credentials', next=next_url)
    return render_template_string(LOGIN_HTML, error=None, next=next_url)


@app.route('/logout')
def logout():
    session.pop('admin_authenticated', None)
    return redirect(url_for('login'))



def init_db(migrate_from_excel: bool = True) -> Tuple[bool, str]:
    """Create DB and optionally migrate data from booking.xlsx if present.

    Returns (success, message).
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.executescript(CREATE_TABLE_SQL)
        conn.commit()

        if migrate_from_excel and os.path.exists(EXCEL_FILE):
            try:
                wb = openpyxl.load_workbook(EXCEL_FILE)
                ws = wb.active
                rows = list(ws.iter_rows(min_row=2, values_only=True))
                if rows:
                    cur.executemany(
                        'INSERT INTO bookings (name, email, appointment_date, phone) VALUES (?, ?, ?, ?)',
                        [(r[0], r[1], r[2], r[3]) for r in rows]
                    )
                    conn.commit()
            except Exception as e:
                # Migration shouldn't stop DB creation; log and continue
                app.logger.exception('Excel migration failed: %s', e)

        conn.close()
        return True, 'DB initialized'
    except Exception as e:
        app.logger.exception('Failed to initialize DB')
        return False, str(e)


@app.route('/book', methods=['POST'])
def book():
    try:
        data = request.get_json()
        if not data:
            app.logger.warning('No JSON body in request')
            return jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400

        name = data.get('name')
        email = data.get('email')
        date = data.get('date')
        phone = data.get('phone')

        # Basic validation
        if not name or not email or not date or not phone:
            return jsonify({'status': 'error', 'message': 'Missing one or more required fields'}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO bookings (name, email, appointment_date, phone) VALUES (?, ?, ?, ?)',
            (name, email, date, phone)
        )
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        app.logger.exception('Failed to save booking')
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/bookings', methods=['GET'])
@login_required_api
def get_bookings():
    try:
        # pagination and search
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        search = (request.args.get('search') or '').strip()

        conn = get_db_connection()
        cur = conn.cursor()

        base_query = 'FROM bookings'
        params: List = []
        if search:
            base_query += ' WHERE name LIKE ? OR email LIKE ? OR appointment_date LIKE ? OR phone LIKE ?'
            like = f'%{search}%'
            params.extend([like, like, like, like])

        # total count
        count_sql = 'SELECT COUNT(*) ' + base_query
        cur.execute(count_sql, params)
        total = cur.fetchone()[0]

        # fetch page
        offset = (max(page, 1) - 1) * per_page
        select_sql = 'SELECT id, name, email, appointment_date as date, phone, created_at ' + base_query + ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        rows = cur.execute(select_sql, params + [per_page, offset]).fetchall()
        conn.close()

        bookings = [dict(r) for r in rows]
        total_pages = math.ceil(total / per_page) if per_page else 1

        return jsonify({
            'bookings': bookings,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages
        })
    except Exception as e:
        app.logger.exception('Failed to fetch bookings')
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/bookings/<int:booking_id>', methods=['DELETE'])
@login_required_api
def delete_booking(booking_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM bookings WHERE id = ?', (booking_id,))
        conn.commit()
        deleted = cur.rowcount
        conn.close()
        if deleted:
            return jsonify({'status': 'success', 'deleted': booking_id})
        else:
            return jsonify({'status': 'error', 'message': 'Booking not found'}), 404
    except Exception as e:
        app.logger.exception('Failed to delete booking')
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/export', methods=['GET'])
@login_required_api
def export_csv():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, name, email, appointment_date, phone, created_at FROM bookings ORDER BY created_at DESC')
        rows = cur.fetchall()
        conn.close()

        # build CSV
        import io, csv
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['id', 'name', 'email', 'appointment_date', 'phone', 'created_at'])
        for r in rows:
            writer.writerow([r['id'], r['name'], r['email'], r['appointment_date'], r['phone'], r['created_at']])

        csv_data = output.getvalue()
        return app.response_class(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment;filename=bookings.csv'}
        )
    except Exception as e:
        app.logger.exception('Failed to export CSV')
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Serve admin page and images so the UI can be opened via Flask
@app.route('/admin')
@login_required_html
def admin_page():
    return send_from_directory(ROOT, 'admin.html')


@app.route('/images/<path:filename>')
def images_static(filename):
    return send_from_directory(os.path.join(ROOT, 'images'), filename)


if __name__ == '__main__':
    ok, msg = init_db(migrate_from_excel=True)
    if not ok:
        app.logger.error('Database init failed: %s', msg)
    app.run(debug=True)

