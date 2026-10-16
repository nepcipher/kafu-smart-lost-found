
from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3
from pathlib import Path

app = Flask(__name__)
DATABASE = Path(__file__).with_name("lost_found.db")


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_type TEXT NOT NULL
                    CHECK(report_type IN ('lost', 'found')),
                item_name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT NOT NULL,
                report_date TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta name="google-site-verification" content="bkCUQSTiB8DatPcPl5lhA9-ty8GQPpWxI06iM1ns5hk" />
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#102b50">
<link rel="manifest" href="/static/manifest.json">
<link rel="icon" type="image/png" sizes="192x192" href="/static/icons/icon-192.png">
<title>KAFU Smart Lost & Found</title>
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f2f5fa;
    color: #18253a;
}
header {
    background: #102b50;
    color: white;
    padding: 22px 7%;
}
header a { color: white; text-decoration: none; }
header h1 { margin: 0 0 8px; }
nav { margin-top: 16px; display: flex; gap: 18px; flex-wrap: wrap; }
nav a { color: #dceaff; text-decoration: none; }
.hero {
    background: linear-gradient(120deg, #102b50, #1769aa);
    color: white;
    padding: 45px 7%;
}
.hero h2 { font-size: clamp(28px, 5vw, 42px); margin-top: 0; }
.hero p { line-height: 1.7; max-width: 650px; }
main { max-width: 1050px; width: 90%; margin: 30px auto; }
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
}
.card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 4px 16px #18253a0c;
    margin-bottom: 20px;
}
.card p { line-height: 1.6; color: #58667a; }
.btn {
    display: inline-block;
    background: #1769aa;
    color: white;
    padding: 12px 16px;
    border: 0;
    border-radius: 7px;
    text-decoration: none;
    cursor: pointer;
    font-size: 15px;
}
.btn:hover { background: #0f4e80; }
.secondary { background: #e5effb; color: #164a7b; }
label { display: block; margin: 16px 0 7px; font-weight: bold; }
input, select, textarea {
    display: block;
    width: 100%;
    padding: 12px;
    border: 1px solid #ccd5e1;
    border-radius: 7px;
    font: inherit;
    background: white;
}
textarea { min-height: 100px; resize: vertical; }
.notice {
    background: #e5f7ec;
    color: #17623b;
    padding: 14px;
    border-radius: 8px;
    margin-bottom: 20px;
}
.muted { color: #687589; font-size: 14px; }

.site-footer {
    text-align: center;
    padding: 35px 7%;
    margin-top: 40px;
    background: #102b50;
    color: #ffffff;
}
.site-footer h3 { margin-bottom: 8px; }
.site-footer p { line-height: 1.6; }
.developer-card {
    max-width: 480px;
    margin: 24px auto;
    padding: 22px;
    background: #ffffff;
    color: #18253a;
    border-radius: 14px;
    box-shadow: 0 4px 16px #00000020;
}
.developer-card h4 { margin-top: 0; color: #1769aa; }
.developer-card a {
    color: #1769aa;
    text-decoration: none;
    overflow-wrap: anywhere;
}
.developer-card a:hover { text-decoration: underline; }
.site-footer .muted { color: #dceaff; }

</style>

<style>
/* Campus FindIt dashboard menu */
.menu-button {
    position: fixed;
    top: 15px;
    left: 15px;
    z-index: 1002;
    width: 45px;
    height: 45px;
    border: none;
    border-radius: 10px;
    background: #102b50;
    color: white;
    font-size: 25px;
    cursor: pointer;
}

.dashboard-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    z-index: 1000;
    display: none;
}

.dashboard-sidebar {
    position: fixed;
    top: 0;
    left: -290px;
    width: 270px;
    height: 100%;
    box-sizing: border-box;
    padding: 80px 15px 20px;
    background: #102b50;
    color: white;
    z-index: 1001;
    transition: left 0.25s ease;
    overflow-y: auto;
}

.dashboard-sidebar.open {
    left: 0;
}

.dashboard-overlay.open {
    display: block;
}

.dashboard-sidebar a {
    display: block;
    padding: 14px 12px;
    margin-bottom: 6px;
    color: white;
    text-decoration: none;
    border-radius: 8px;
}

.dashboard-sidebar a:hover {
    background: #1f4e79;
}

.dashboard-sidebar h2 {
    margin: 0 0 20px;
    font-size: 22px;
}

@media (min-width: 768px) {
    .menu-button {
        top: 20px;
        left: 20px;
    }
}
</style>
</head>
</head>
<body>

<button class="menu-button" id="menuButton"
        aria-label="Open navigation menu"
        aria-expanded="false"
        onclick="toggleDashboard()">☰</button>

<div class="dashboard-overlay" id="dashboardOverlay"
     onclick="toggleDashboard()"></div>

<nav class="dashboard-sidebar" id="dashboardSidebar">
    <h2>Campus FindIt</h2>

    <a href="/">🏠 Dashboard</a>
    <a href="/claims">📋 Claims</a>
    <a href="/search">🔎 Browse Items</a>
    <a href="/report/lost">📢 Report Lost Items</a>
    <a href="/report/found">📦 Report Found Items</a>
    <a href="/notifications">🔔 Notifications</a>
</nav>

<header>
    <h1><a href="/">KAFU Smart Lost & Found</a></h1>
    <div>Find It. Report It. Return It.</div>
    <nav>
        <a href="/">Home</a>
        <a href="/report/lost">Report Lost</a>
        <a href="/report/found">Report Found</a>
        <a href="/search">Search Reports</a>
    </nav>
</header>

{% if message %}
<main><div class="notice">{{ message }}</div></main>
{% endif %}

{% if page == 'home' %}
<section class="hero">
    <h2>Lost something on campus?</h2>
    <p>Report missing belongings, share details of items you find,
    and search existing reports to help reconnect people with their property.</p>
    <a class="btn" href="/report/lost">Report a Lost Item</a>
    <a class="btn secondary" href="/report/found">Report a Found Item</a>
</section>
<main>
    <h2>How can we help?</h2>
    <div class="grid">
        <section class="card">
            <h3>🔎 Find an Item</h3>
            <p>Search the reports submitted to the system.</p>
            <a class="btn" href="/search">Search Items</a>
        </section>
        <section class="card">
            <h3>📢 Report an Item</h3>
            <p>Tell the campus community about a lost or found item.</p>
            <a class="btn" href="/report/lost">Get Started</a>
        </section>
        <section class="card">
            <h3>🤝 Return Belongings</h3>
            <p>Help items find their way back to their owners.</p>
            <a class="btn" href="/search">View Reports</a>
        </section>
    </div>
</main>

{% elif page == 'report' %}
<main>
<section class="card">
    <h2>Report a {{ kind }} Item</h2>
    <p>Enter accurate information. Do not include passwords,
    student registration numbers, or other sensitive information.</p>
    <form method="POST">
        <label for="item_name">Item name</label>
        <input id="item_name" name="item_name" maxlength="100"
               required placeholder="e.g. Black laptop charger">

        <label for="category">Category</label>
        <select id="category" name="category" required>
            <option value="">Choose a category</option>
            <option>Electronics</option>
            <option>Identification card</option>
            <option>Books and stationery</option>
            <option>Bags and clothing</option>
            <option>Keys</option>
            <option>Other</option>
        </select>

        <label for="description">Description</label>
        <textarea id="description" name="description"
                  maxlength="1000" required
                  placeholder="Describe the item"></textarea>

        <label for="location">Location on or near campus</label>
        <input id="location" name="location" maxlength="150"
               required placeholder="e.g. Library">

        <label for="report_date">Date {{ 'lost' if kind == 'lost' else 'found' }}</label>
        <input id="report_date" name="report_date"
               type="date" required>

        <p class="muted">For safety, keep unique identifying details private.</p>
        <button class="btn" type="submit">Submit Report</button>
    </form>
</section>
</main>

{% elif page == 'search' %}
<main>
    <h2>Search Lost & Found Reports</h2>
    <form class="card" method="GET" action="/search">
        <label for="q">Search by item, category, description, or location</label>
        <input id="q" name="q" value="{{ query }}"
               placeholder="e.g. charger or library">

<label for="report_type">Filter by report</label>
<select id="report_type" name="report_type">
    <option value="">All reports</option>
    <option value="lost">Lost items</option>
    <option value="found">Found items</option>
</select>

<label for="status">Filter by status</label>
<select id="status" name="status">
    <option value="">All statuses</option>
    <option value="active">Active</option>
    <option value="recovered">Recovered</option>
</select>

        <p></p>
        <button class="btn" type="submit">Search</button>
        <a class="btn secondary" href="/search">Clear</a>
    </form>
    {% if reports %}
        <div class="grid">
        {% for item in reports %}
            <article class="card">
                <h3>{{ item['item_name'] }}</h3>
                <p><strong>Report:</strong> {{ item['report_type']|title }}</p>
                <p><strong>Category:</strong> {{ item['category'] }}</p>
                <p><strong>Description:</strong> {{ item['description'] }}</p>
                <p><strong>Location:</strong> {{ item['location'] }}</p>
                <p><strong>Date:</strong> {{ item['report_date'] }}</p>
{% if item['status'] != 'recovered' %}
<form method="POST" action="{{ url_for('recover', report_id=item['id']) }}">
    <button class="btn" type="submit">Mark as Recovered</button>
</form>
{% else %}
<p><strong>Item returned!</strong></p>
{% endif %}<p><strong>Status:</strong> {{ item['status']|title }}</p>
                <p class="muted">Report #{{ item['id'] }}</p>
            </article>
        {% endfor %}
        </div>
    {% else %}
        <section class="card">
            <p>No reports found. Try another search or submit a new report.</p>
        </section>
    {% endif %}
</main>

{% elif page == 'claims' %}
<main>
    <h2>📋 Claims & Item Returns</h2>
    <p>Review reported items and their current status.</p>

    {% if reports %}
        <div class="grid">
        {% for item in reports %}
            <article class="card">
                <h3>{{ item['item_name'] }}</h3>
                <p><strong>Report type:</strong> {{ item['report_type']|title }}</p>
                <p><strong>Category:</strong> {{ item['category'] }}</p>
                <p><strong>Location:</strong> {{ item['location'] }}</p>
                <p><strong>Status:</strong> {{ item['status']|title }}</p>
                <p class="muted">Report #{{ item['id'] }}</p>

                {% if item['status'] != 'recovered' %}
                    <form method="POST"
                          action="{{ url_for('recover', report_id=item['id']) }}">
                        <button class="btn" type="submit">
                            Mark as Recovered
                        </button>
                    </form>
                {% else %}
                    <p><strong>Item returned!</strong></p>
                {% endif %}
            </article>
        {% endfor %}
        </div>
    {% else %}
        <section class="card">
            <p>No reports have been submitted yet.</p>
        </section>
    {% endif %}
</main>

{% elif page == 'notifications' %}
<main>
    <h2>🔔 Notifications</h2>
    <p>Stay updated on activity in the KAFU Lost & Found portal.</p>

    <section class="card">
        <h3>📢 Lost and Found Reports</h3>
        <p>Visit Browse Items to see recently reported belongings.</p>
        <a class="btn" href="/search">Browse Items</a>
    </section>

    <section class="card">
        <h3>🤝 Item Returns</h3>
        <p>Check whether an item has been marked as recovered.</p>
        <a class="btn" href="/claims">View Claims & Returns</a>
    </section>

    <section class="card">
    <h3>🕒 Recent Activity</h3>

    {% if reports %}
        {% for item in reports %}
            <article class="card">
                <h4>
                    {% if item['status'] == 'recovered' %}
                        ✅ Item Recovered
                    {% elif item['report_type'] == 'lost' %}
                        🔍 Lost Item Reported
                    {% else %}
                        📦 Found Item Reported
                    {% endif %}
                </h4>

                <p><strong>Item:</strong> {{ item['item_name'] }}</p>
                <p><strong>Location:</strong> {{ item['location'] }}</p>
                <p><strong>Status:</strong> {{ item['status']|title }}</p>
                <p><strong>Submitted:</strong> {{ item['created_at'] }}</p>
            </article>
        {% endfor %}
    {% else %}
        <p>No activity yet. New lost and found reports will appear here.</p>
    {% endif %}
</section>
</main>

{% endif %}


<footer class="site-footer">

    <h3>KAFU Smart Lost &amp; Found</h3>
    <p>Find It. Report It. Return It.</p>
    <p>A student innovation project helping the KAFU community reconnect with lost belongings.</p>

    <div class="developer-card">
        <h4>About the Developer</h4>
        <p><strong>Nepstar Sunguti</strong></p>
        <p>KAFU Computer Science Student</p>
        <p>
            <a href="https://wa.me/254143467188" target="_blank" rel="noopener noreferrer">
                Chat with me on WhatsApp
            </a>
        </p>
        <p>
            <a href="mailto:nepstarsunguti@gmail.com">
                nepstarsunguti@gmail.com
            </a>
        </p>
    </div>

    <p class="muted">Developed by a KAFU Computer Science student.</p>
</footer>

<section style="text-align:center; padding:24px; margin:20px auto; max-width:500px; background:#f0f5fb; border-radius:16px;">
  <h2 style="color:#102b50;">📱 Access Our Portal Easily</h2>
  <p>Scan this QR code with your phone to open KAFU Smart Lost &amp; Found.</p>
  <img
    src="https://api.qrserver.com/v1/create-qr-code/?size=220x220&amp;data=https%3A%2F%2Fkafu-smart-lost-found.onrender.com%2F"
    alt="QR code for KAFU Smart Lost and Found"
    width="220"
    height="220"
    style="background:white; padding:10px; border-radius:8px;"
  >
  <p style="color:#334155;">Help reunite students with their lost items.</p>
</section>


<script>
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/service-worker.js")
      .catch(error => console.error("Service worker registration failed:", error));
  });
}
</script>

<script>
function toggleDashboard() {
    const sidebar = document.getElementById("dashboardSidebar");
    const overlay = document.getElementById("dashboardOverlay");
    const button = document.getElementById("menuButton");

    const isOpen = sidebar.classList.toggle("open");
    overlay.classList.toggle("open", isOpen);
    button.setAttribute("aria-expanded", isOpen);
    button.setAttribute(
        "aria-label",
        isOpen ? "Close navigation menu" : "Open navigation menu"
    );
}

document.addEventListener("keydown", function(event) {
    if (event.key === "Escape") {
        const sidebar = document.getElementById("dashboardSidebar");
        if (sidebar && sidebar.classList.contains("open")) {
            toggleDashboard();
        }
    }
});
</script>
</body>

</body>
</html>
"""


def render_page(page, **context):
    return render_template_string(PAGE, page=page, **context)



@app.route("/service-worker.js")
def service_worker():
    return app.send_static_file("service-worker.js")


@app.route("/")
def home():
    return render_page("home", message=None)


@app.route("/report/<kind>", methods=["GET", "POST"])
def report(kind):
    if kind not in ("lost", "found"):
        return "Report type not found", 404

    if request.method == "POST":
        item_name = request.form.get("item_name", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        location = request.form.get("location", "").strip()
        report_date = request.form.get("report_date", "").strip()

        if not all((item_name, category, description, location, report_date)):
            return "Please complete every field.", 400

        if (len(item_name) > 100 or len(category) > 50
                or len(description) > 1000 or len(location) > 150
                or len(report_date) > 10):
            return "One or more fields are too long.", 400

        with get_db() as db:
            db.execute("""
                INSERT INTO reports
                (report_type, item_name, category, description, location, report_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (kind, item_name, category, description, location, report_date))

        return redirect(url_for("search", saved="1"))

    return render_page("report", kind=kind, message=None)



@app.route("/recover/<int:report_id>", methods=["POST"])
def recover(report_id):
    with get_db() as db:
        db.execute(
            "UPDATE reports SET status = 'recovered' WHERE id = ?",
            (report_id,)
        )
    return redirect(url_for("search"))




@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    saved = request.args.get("saved") == "1"

    with get_db() as db:
        if query:
            term = f"%{query}%"
            reports = db.execute("""
                SELECT * FROM reports
                WHERE item_name LIKE ? OR category LIKE ?
                   OR description LIKE ? OR location LIKE ?
                ORDER BY created_at DESC
            """, (term, term, term, term)).fetchall()
        else:
            reports = db.execute("""
                SELECT * FROM reports
                ORDER BY created_at DESC
            """).fetchall()

    return render_page(
        "search",
        reports=reports,
        query=query,
        message="Your report was saved successfully." if saved else None
    )

@app.route("/claims")
def claims():
    with get_db() as db:
        reports = db.execute("""
            SELECT * FROM reports
            ORDER BY created_at DESC
        """).fetchall()

    return render_page(
        "claims",
        reports=reports,
        query="",
        message=None
    )

@app.route("/notifications")
def notifications():
    with get_db() as db:
        reports = db.execute("""
            SELECT *
            FROM reports
            ORDER BY created_at DESC
            LIMIT 50
        """).fetchall()

    return render_page(
        "notifications",
        message=None,
        reports=reports
    )




initialize_database()

if __name__ == "__main__":
    app.run(debug=True)
