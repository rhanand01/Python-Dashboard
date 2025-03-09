from flask import Flask, render_template, request, redirect, url_for
import csv
import subprocess
import time
import os
import panel as pn
from threading import Thread

app = Flask(__name__)

# Function to read user credentials from the CSV file
def read_users_from_csv(file_path='Accesslevel.csv'):
    users = {}
    # Check if the CSV file exists
    if not os.path.exists(file_path):
        return users
    
    # Read CSV and store user data in a dictionary
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            email = row['email']
            password = row['password']
            users[email] = password  # store password (assuming password is plain text for simplicity)
    return users

# Function to authenticate user using the CSV data
def authenticate_user(email, password):
    # Read users data from the CSV file
    users = read_users_from_csv()
    
    # Check if email exists and if password matches
    if email in users and users[email] == password:
        return True  # Successful authentication
    return False  # Invalid credentials

# Function to start Streamlit apps at the specified file paths (in a separate thread)
def start_streamlit_app(file_path, port):
    try:
        subprocess.Popen(['streamlit', 'run', file_path, '--server.port', str(port),'--server.headless=True'])
        time.sleep(2)  # Giving some time for the app to start
    except Exception as e:
        print(f"Error starting app {file_path} on port {port}: {e}")

# Function to create the Panel layout with Tabs for Member Dashboard
def create_member_dashboard():
    # Paths to the Streamlit apps
    overview_path = "E:/Elevatoz intern/Python Dashboard/Dashboard/overview.py"
    registrations_path = "E:/Elevatoz intern/Python Dashboard/Dashboard/Registration.py"
    trans_path = "E:/Elevatoz intern/Python Dashboard/Dashboard/Transaction.py"
    reedemptions_path = "E:/Elevatoz intern/Python Dashboard/Dashboard/Redemption.py"

    # Start the Streamlit apps in different threads (so they run concurrently)
    Thread(target=start_streamlit_app, args=(overview_path, 8501)).start()
    Thread(target=start_streamlit_app, args=(registrations_path, 8502)).start()
    Thread(target=start_streamlit_app, args=(trans_path, 8503)).start()
    Thread(target=start_streamlit_app, args=(reedemptions_path, 8504)).start()

    welcome_message = pn.pane.Markdown("# Welcome to Your Dashboard!", sizing_mode='stretch_width')


    # Create Panel tabs layout
    tabs = pn.Tabs(
        ("Overview", pn.pane.HTML(f'<iframe src="http://localhost:8501" height="100%" width="100%" frameborder="0" style="border:none; height:100vh; width:100vw;"></iframe>')),
        ("Registration", pn.pane.HTML(f'<iframe src="http://localhost:8502" height="100%" width="100%" frameborder="0" style="border:none; height:100vh; width:100vw;"></iframe>')),
        ("Transaction", pn.pane.HTML(f'<iframe src="http://localhost:8503" height="100%" width="100%" frameborder="0" style="border:none; height:100vh; width:100vw;"></iframe>')),
        ("Redemption", pn.pane.HTML(f'<iframe src="http://localhost:8504" height="100%" width="100%" frameborder="0" style="border:none; height:100vh; width:100vw;"></iframe>')),
    )

    # Set the tabs layout to stretch to the full screen
    tabs.sizing_mode = 'stretch_both'

    # Use a Column to make sure the entire layout fills the screen
    layout = pn.Column(welcome_message, tabs)
    layout.height = 100  # Set height to 100% of the screen
    layout.width = 100   # Set width to 100% of the screen
    layout.sizing_mode = 'stretch_both'

    # Save Panel layout as HTML file
    html_file_path = "member_dashboard.html"
    layout.save(html_file_path, embed=True)

    # Read the content of the saved HTML file and return it as a string
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    return html_content

@app.route('/')
def login_page():
    return render_template('login.html')

# Flask route for handling login logic
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    # Authenticate user using CSV data
    if authenticate_user(email, password):
        # If authentication is successful, redirect based on access level
        if email == "admin@example.com":  # Example of admin check
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('member_dashboard'))
    else:
        return render_template('login.html', error="Invalid credentials")

# Flask route for the Admin dashboard
@app.route('/admin-dashboard')
def admin_dashboard():
    # Paths to the Streamlit apps (just an example for the admin dashboard)
    overview_path = "E:/Elevatoz intern/Python Dashboard/Dashboard/overview.py"
    registrations_path = "E:/Elevatoz intern/Python Dashboard/Dashboard/Registration.py"
    trans_path = "E:/Elevatoz intern/Python Dashboard/Dashboard/Transaction.py"
    reedemptions_path = "E:/Elevatoz intern/Python Dashboard/Dashboard/Redemption.py"

    # Start the Streamlit apps
    start_streamlit_app(overview_path, 8501)
    time.sleep(2)
    start_streamlit_app(registrations_path, 8502)
    time.sleep(2)
    start_streamlit_app(trans_path, 8503)
    time.sleep(2)
    start_streamlit_app(reedemptions_path, 8504)

    return render_template('E:/Elevatoz intern/Python Dashboard/member_dashboard.html')

# Flask route for the Member dashboard
@app.route('/member-dashboard')
def member_dashboard():
    
    # Create Panel tabs for the Member dashboard and save as HTML
    member_dashboard_html = create_member_dashboard()

    # Return the saved HTML as a response to Flask
    return member_dashboard_html

if __name__ == '__main__':
    app.run(debug=True)
