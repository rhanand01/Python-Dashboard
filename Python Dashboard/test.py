# from flask import Flask, render_template, request, redirect, url_for
# import csv
# import subprocess
# import time
# import os
# import panel as pn
# from threading import Thread
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# app = Flask(__name__)

# # Function to read user credentials from the CSV file
# def read_users_from_csv(file_path='Accesslevel.csv'):
#     users = {}
#     if not os.path.exists(file_path):
#         return users

#     with open(file_path, mode='r', newline='', encoding='utf-8') as file:
#         csv_reader = csv.DictReader(file)
#         for row in csv_reader:
#             email = row['email']
#             password = row['password']
#             users[email] = {'password': password}
#     return users

# # Function to authenticate user using the CSV data
# def authenticate_user(email, password):
#     # Read users data from the CSV file
#     users = read_users_from_csv()
    
#     # Check if email exists and if password matches
#     if email in users and users[email]['password'] == password:
#         return True  # Successful authentication
#     return False  # Invalid credentials

# # Function to start Streamlit apps at the specified file paths (in a separate thread)
# def start_streamlit_app(file_path, port):
#     try:
#         subprocess.Popen(['streamlit', 'run', file_path, '--server.port', str(port), '--server.headless=True'])
#         time.sleep(2)  # Giving some time for the app to start
#     except Exception as e:
#         print(f"Error starting app {file_path} on port {port}: {e}")

# # Function to create the Panel layout with Tabs for Member Dashboard
# def create_member_dashboard():
#     # Paths to the Streamlit apps
#     overview_path = "E:\\Elevatoz intern\\Python Dashboard\\Dashboard\\overview.py"
#     registrations_path = "E:\\Elevatoz intern\\Python Dashboard\\Dashboard\\Registration.py"
#     trans_path = "E:\\Elevatoz intern\\Python Dashboard\\Dashboard\\Transaction.py"
#     reedemptions_path = "E:\\Elevatoz intern\\Python Dashboard\\Dashboard\\Redemption.py"

#     # Start the Streamlit apps in different threads (so they run concurrently)
#     Thread(target=start_streamlit_app, args=(overview_path, 8501)).start()
#     Thread(target=start_streamlit_app, args=(registrations_path, 8502)).start()
#     Thread(target=start_streamlit_app, args=(trans_path, 8503)).start()
#     Thread(target=start_streamlit_app, args=(reedemptions_path, 8504)).start()

#     welcome_message = pn.pane.Markdown("# Welcome to Panasonic Samriddhi", sizing_mode='stretch_width')


#     # Create Panel tabs layout
#     tabs = pn.Tabs(
#         ("Overview", pn.pane.HTML(f'<iframe src="http://localhost:8501" height="100%" width="100%" frameborder="0" style="border:none; height:100vh; width:100vw;"></iframe>')),
#         ("Registration", pn.pane.HTML(f'<iframe src="http://localhost:8502" height="100%" width="100%" frameborder="0" style="border:none; height:100vh; width:100vw;"></iframe>')),
#         ("Transaction", pn.pane.HTML(f'<iframe src="http://localhost:8503" height="100%" width="100%" frameborder="0" style="border:none; height:100vh; width:100vw;"></iframe>')),
#         ("Redemption", pn.pane.HTML(f'<iframe src="http://localhost:8504" height="100%" width="100%" frameborder="0" style="border:none; height:100vh; width:100vw;"></iframe>')),
#     )

#     # Set the tabs layout to stretch to the full screen
#     tabs.sizing_mode = 'stretch_both'

#     # Use a Column to make sure the entire layout fills the screen
#     layout = pn.Column(welcome_message, tabs)
#     layout.height = 100  # Set height to 100% of the screen
#     layout.width = 100   # Set width to 100% of the screen
#     layout.sizing_mode = 'stretch_both'

#     # Save Panel layout as HTML file
#     html_file_path = "member_dashboard.html"
#     layout.save(html_file_path, embed=True)

#     # Read the content of the saved HTML file and return it as a string
#     with open(html_file_path, 'r', encoding='utf-8') as f:
#         html_content = f.read()

#     return html_content

# @app.route('/')
# def login_page():
#     return render_template('login.html')


# def send_password_reset_email(email, username):
#     def send_email():
#         smtp_server = "smtp.gmail.com"
#         port = 587
#         sender_email = "gangpriyanshi@gmail.com"
#         password = "kiwa ywae liyv tebk"
#         admin_email = "priyanshi62577@gmail.com"

#         try:
#             with smtplib.SMTP(smtp_server, port) as server:
#                 server.starttls()
#                 server.login(sender_email, password)
#                 message = MIMEMultipart()
#                 message["From"] = sender_email
#                 message["To"] = admin_email
#                 message["Subject"] = "Password Reset Request"
#                 body = f"Hi Admin,\n\nUser {username} ({email}) has requested a password reset."
#                 message.attach(MIMEText(body, "plain"))
#                 server.sendmail(sender_email, admin_email, message.as_string())
#                 print(f"Password reset request sent to Admin")
#         except Exception as e:
#             print(f"Failed to send email: {e}")

#     Thread(target=send_email).start()


# # Flask route for handling login logic
# @app.route('/login', methods=['POST'])
# def login():
#     email = request.form['email']
#     password = request.form['password']

#     # Debugging: print the email and password received
#     print(f"Received email: {email}, password: {password}")

#     # Authenticate user using CSV data
#     if authenticate_user(email, password):
#         print(f"User {email} authenticated successfully.")  # Debugging
#         # If authentication is successful, redirect based on access level
#         if email == "admin@example.com":  # Example of admin check
#             return redirect(url_for('admin_dashboard'))
#         else:
#             return redirect(url_for('member_dashboard'))
#     else:
#         print(f"Authentication failed for {email}.")  # Debugging
#         return render_template('login.html', error="Invalid credentials")

# @app.route('/forgot-password', methods=['GET', 'POST'])
# def forgot_password():
#     if request.method == 'POST':
#         email = request.form['email']
#         users = read_users_from_csv()
#         if email in users:
#             name = users[email]['name']
#             send_password_reset_email(email, name)
#             return render_template('forgot_pass.html', message="Password reset email sent successfully!")
#         else:
#             return render_template('forgot_pass.html', error="Email not found")
#     return render_template('forgot_pass.html')


# # Flask route for the Admin dashboard
# @app.route('/admin-dashboard')
# def admin_dashboard():
#     # Paths to the Streamlit apps (just an example for the admin dashboard)
#     overview_path = "E:\\Elevatoz intern\\Python Dashboard\\Dashboard\\overview.py"
#     registrations_path = "E:\\Elevatoz intern\\Python Dashboard\\Dashboard\\Registration.py"
#     trans_path = "E:\\Elevatoz intern\\Python Dashboard\\Dashboard\\Transaction.py"
#     reedemptions_path = "E:\\Elevatoz intern\\Python Dashboard\\Dashboard\\Redemption.py"

#     # Start the Streamlit apps
#     start_streamlit_app(overview_path, 8501)
#     time.sleep(2)
#     start_streamlit_app(registrations_path, 8502)
#     time.sleep(2)
#     start_streamlit_app(trans_path, 8503)
#     time.sleep(2)
#     start_streamlit_app(reedemptions_path, 8504)

#     return render_template('admin_dashboard.html')

# # Flask route for the Member dashboard
# @app.route('/member-dashboard')
# def member_dashboard():
    
#     # Create Panel tabs for the Member dashboard and save as HTML
#     member_dashboard_html = create_member_dashboard()

#     # Return the saved HTML as a response to Flask
#     return member_dashboard_html

# if __name__ == '_main_':
#     app.run(debug=True)


import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime, timedelta
from fpdf import FPDF
import base64

st.set_page_config(page_title="Registration Dashboard", layout="wide")


# Load external CSS
with open("/Users/anushas/Documents/cross filtering/style.css") as f:
    custom_css = f.read()

st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)

# Load Data
@st.cache_data
def load_data():
    return pd.read_csv('/Users/anushas/Documents/cross filtering/Registrations_Sample.csv')

# Filter Data
def filter_data(df, zone, state, city, tier, start_date=None, end_date=None):
    # Convert RegisterDate to datetime
    df['RegisterDate'] = pd.to_datetime(df['RegisterDate'], errors='coerce')  # Coerce invalid dates to NaT
    
    if start_date and end_date:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        df = df[(df['RegisterDate'] >= start_date) & (df['RegisterDate'] <= end_date)]
        
    if zone:
        df = df[df['Zone'] == zone]
    if state:
        df = df[df['State'] == state]
    if city:
        df = df[df['City'] == city]
    if tier:
        df = df[df['MemberTier'] == tier]
    return df

# Download Filtered Data (Dynamic for Each Chart)
def download_button(df, filename):
    # Prepare CSV
    csv_output = BytesIO()
    df.to_csv(csv_output, index=False)
    csv_b64 = base64.b64encode(csv_output.getvalue()).decode()

    # Prepare Excel
    excel_output = BytesIO()
    with pd.ExcelWriter(excel_output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    excel_b64 = base64.b64encode(excel_output.getvalue()).decode()

    # Prepare PDF using fpdf2
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    

    # Add header
    pdf.cell(200, 10, txt="Registration Report", ln=True, align='C')

    # Calculate column widths based on the longest header
    col_widths = [pdf.get_string_width(col) + 10 for col in df.columns]
    row_height = 10

    # Set table header
    pdf.set_font("Arial", size=10, style='B')  # Bold for headers
    for i, col in enumerate(df.columns):
        pdf.cell(col_widths[i], row_height, col, border=1, align='C')
    pdf.ln()  # Move to the next line

    # Add table rows
    pdf.set_font("Arial", size=8)
    for i, row in df.iterrows():
        for j, value in enumerate(row):
            pdf.cell(col_widths[j], row_height, str(value), border=1, align='C')
        pdf.ln()

    pdf_output = BytesIO()
    pdf.output(pdf_output,'S')
    pdf_b64 = base64.b64encode(pdf_output.getvalue()).decode()

    # HTML with download button positioned to the right of the chart
    st.markdown(f"""
    <style>
        .download-container {{
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 1;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }}
        .dropdown-container {{
            position: relative;
            display: inline-block;
        }}
        .dropdown-content {{
            display: none;
            position: absolute;
            background-color: white;
            border: 1px solid #ddd;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
            z-index: 1;
            min-width: 120px;
        }}
        .dropdown-content a {{
            color: black;
            padding: 10px 12px;
            text-decoration: none;
            display: block;
            font-size: 14px;
        }}
        .dropdown-content a:hover {{
            background-color: #f4f4f4;
        }}
        .dropdown-container:hover .dropdown-content {{
            display: block;
        }}
        .dropdown-container img {{
            cursor: pointer;
            width: 16px;  /* Reduced the image size */
            height: 16px;
        }}
    </style>
    <div class="download-container">
        <div class="dropdown-container">
            <img src="data:image/png;base64,{base64.b64encode(open('/Users/anushas/Documents/cross filtering/download.png', 'rb').read()).decode()}" alt="Download Icon">
            <div class="dropdown-content">
                <a href="data:file/csv;base64,{csv_b64}" download="{filename}.csv">Download CSV</a>
                <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_b64}" download="{filename}.xlsx">Download Excel</a>
                <a href="data:application/pdf;base64,{pdf_b64}" download="{filename}.pdf">Download PDF</a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Load Data
df = load_data()

# Function to filter the data
def filter_data(df, zone, state, city, tier, start_date=None, end_date=None):
    df['RegisterDate'] = pd.to_datetime(df['RegisterDate'], errors='coerce')
    
    if start_date and end_date:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        df = df[(df['RegisterDate'] >= start_date) & (df['RegisterDate'] <= end_date)]
        
    if zone and zone != 'Select':
        df = df[df['Zone'] == zone]
    if state and state != 'Select':
        df = df[df['State'] == state]
    if city and city != 'Select':
        df = df[df['City'] == city]
    if tier and tier != 'Select':
        df = df[df['MemberTier'] == tier]
    
    return df

# Initialize session state variables if not already initialized
for key in ['date_filter', 'zone_filter', 'state_filter', 'city_filter', 'member_tier_filter']:
    if key not in st.session_state:
        st.session_state[key] = 'Select'

# Reset Filters Button
col1, col2 = st.columns([5, 1])
with col1:
    st.title("Registration Dashboard")
with col2:
    if st.button("", icon=":material/restart_alt:", key="reset_emoji"):
        for key in ['date_filter', 'zone_filter', 'state_filter', 'city_filter', 'member_tier_filter']:
            st.session_state[key] = 'Select'
        st.rerun()

# Filters at the top
filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns(5)

# Date Filter
with filter_col1:
    date_filter = st.selectbox(
        "Select Date Range",
        ['Select', 'Today', 'Yesterday', 'Last Week', 'Last Month', 'Last 3 Months', 'Last 12 Months', 'Custom Range'],
        key='date_filter'
    )

    start_date, end_date = None, None
    if date_filter == 'Today':
        start_date = end_date = datetime.now().date()
    elif date_filter == 'Yesterday':
        start_date = end_date = datetime.now().date() - timedelta(days=1)
    elif date_filter == 'Last Week':
        start_date = datetime.now().date() - timedelta(days=7)
        end_date = datetime.now().date()
    elif date_filter == 'Last Month':
        start_date = datetime.now().date() - timedelta(days=30)
        end_date = datetime.now().date()
    elif date_filter == 'Last 3 Months':
        start_date = datetime.now().date() - timedelta(days=90)
        end_date = datetime.now().date()
    elif date_filter == 'Last 12 Months':
        start_date = datetime.now().date() - timedelta(days=365)
        end_date = datetime.now().date()
    elif date_filter == 'Custom Range':
        start_date = st.date_input("Start Date", datetime.now().date() - timedelta(days=30))
        end_date = st.date_input("End Date", datetime.now().date())

# Zone Filter
with filter_col2:
    zone = st.selectbox(
        "Zone",
        options=['Select'] + sorted(df['Zone'].dropna().unique()),
        key="zone_filter"
    )

# Filter available states based on selected zone
filtered_states = df['State'].dropna().unique()
if zone != 'Select':
    filtered_states = df[df['Zone'] == zone]['State'].dropna().unique()

# State Filter
with filter_col3:
    state = st.selectbox(
        'Select State',
        ['Select'] + sorted(filtered_states),
        key='state_filter'
    )

# Filter available cities based on selected state
filtered_cities = df['City'].dropna().unique()
if state != 'Select':
    filtered_cities = df[df['State'] == state]['City'].dropna().unique()

# City Filter
with filter_col4:
    city = st.selectbox(
        'Select City',
        ['Select'] + sorted(filtered_cities),
        key='city_filter'
    )

# Member Tier Filter
with filter_col5:
    tier = st.selectbox(
        'Select Member Tier',
        ['Select'] + sorted(df['MemberTier'].dropna().unique()),
        key='member_tier_filter'
    )

# Filter data using the filter_data function
filtered_df = filter_data(df, zone, state, city, tier, start_date, end_date)


def format_number(number):
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.1f}K"
    else:
        return str(number)
    
# Score Cards with Individual Boxes and 3D Effect
st.markdown(
    f"""
    <div class='metric-container'>
        <div class='metric-box'>
            <div class='metric-value'>{format_number(filtered_df['memberID'].nunique())}</div>
            <div class='metric-label' style="font-size: 18px; font-weight: bold;" >Total Members</div>
        </div>
        <div class='metric-box'>
            <div class='metric-value'>{format_number(filtered_df[filtered_df['memberStatus'] == 'Active'].shape[0])}</div>
            <div class='metric-label' style="font-size: 18px; font-weight: bold;" >Active Members</div>
        </div>
        <div class='metric-box'>
            <div class='metric-value'>{format_number(filtered_df[filtered_df['KYCStatus'] == 1].shape[0])}</div>
            <div class='metric-label' style="font-size: 18px; font-weight: bold;" >Pending KYC</div>
        </div>
        <div class='metric-box'>
            <div class='metric-value'>{format_number(len(filtered_df) - len(filtered_df.drop_duplicates(subset=['memberID'])))}</div>
            <div class='metric-label' style="font-size: 18px; font-weight: bold;" >Duplicate Registrations</div>
        </div>
        <div class='metric-box'>
            <div class='metric-value'>{format_number(len(filtered_df.drop_duplicates(subset=['memberID'])))}</div>
            <div class='metric-label' style="font-size: 18px; font-weight: bold;" >Unique Registrations</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
        /* Target all Plotly charts only */
        [data-testid="stPlotlyChart"] {
            border-radius: 15px; /* Curved corners */
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* Optional shadow */
            overflow: hidden; /* Ensure content fits within rounded corners */
            background-color: white; /* Optional background color */
        }
    </style>
    """,
    unsafe_allow_html=True
)


col1, col2 = st.columns([1,2])
with col1:
    # Total Registrations
    total_registrations = len(filtered_df)
    
    # Today's Total Registrations
    registrations_on_date = len(filtered_df[filtered_df["RegisterDate"].dt.date == pd.Timestamp.today().date()])
    
    # Silver and Gold Members
    silver_members = len(filtered_df[filtered_df["MemberTier"] == "Silver"])
    gold_members = len(filtered_df[filtered_df["MemberTier"] == "Gold"])
    
    # Completed KYC
    completed_kyc = len(filtered_df[filtered_df["KYCStatus"] == 1])
    
    # Filtering for Most Active
    if city:  # If city filter is applied
        filtered_city_df = filtered_df[filtered_df["City"] == city]
        most_active_label = "Most Active District"
        most_active_value = (
            filtered_city_df["District"].mode()[0] if not filtered_city_df.empty else "No Data"
        )
        
        if tier:  # If tier filter is also applied along with city filter
            filtered_city_tier_df = filtered_city_df[filtered_city_df["MemberTier"] == tier]
            most_active_label = "Most Active District for Tier"
            most_active_value = (
                filtered_city_tier_df["District"].mode()[0] if not filtered_city_tier_df.empty else "No Data"
            )
            
    elif state:  # If state filter is applied
        filtered_state_df = filtered_df[filtered_df["State"] == state]
        most_active_label = "Most Active City"
        most_active_value = filtered_state_df["City"].mode()[0] if not filtered_state_df.empty else "No Data"
        
    elif zone:  # If zone filter is applied
        filtered_zone_df = filtered_df[filtered_df["Zone"] == zone]
        most_active_label = "Most Active State"
        most_active_value = filtered_zone_df["State"].mode()[0] if not filtered_zone_df.empty else "No Data"
        
    elif tier and city and state and zone:  # If all filters are applied
        filtered_all_df = filtered_df[
            (filtered_df["MemberTier"] == tier) &
            (filtered_df["Zone"] == zone) &
            (filtered_df["State"] == state) &
            (filtered_df["City"] == city)
        ]
        most_active_label = "Most Active District"
        most_active_value = (
            filtered_all_df["District"].mode()[0] if not filtered_all_df.empty else "No Data"
        )

    else:  # No filters applied
        most_active_label = "Most Active Zone"
        most_active_value = filtered_df["Zone"].mode()[0] if not filtered_df.empty else "No Data"

    # Streamlit Insights Display
    summary_html = f"""  
    <div class='summary-container' style="height: 470px; width: 100%; margin-top: -18px;">  
        <div class='summary-box'>  
            <div class='summary-value'>Insight Summary
                <div class='summary-label' style="font-size: 18px;">1. <b>🔢 Total Registrations:</b><br> The total number of registrations is <b>{total_registrations}</b> members.</div>  
                <div class='summary-label' style="font-size: 18px;">2. <b>📅 Today's Total Registration:</b><br> The number of registrations completed today is <b>{registrations_on_date}</b> members.</div>  
                <div class='summary-label' style="font-size: 18px;">3. <b>⭐ Silver Members:</b><br> There are <b>{silver_members}</b> members registered as Silver Members.</div>  
                <div class='summary-label' style="font-size: 18px;">4. <b>🏅 Gold Members:</b><br> The total number of Gold Members is <b>{gold_members}</b>.</div>  
                <div class='summary-label' style="font-size: 18px;">5. <b>🌍 Most Active Region:</b><br> The <b>{most_active_label}</b> based on registrations is <b>{most_active_value}</b>.</div>  
                <div class='summary-label' style="font-size: 18px;">6. <b>📋 Completed KYC:</b><br> The number of members who have completed their KYC is <b>{completed_kyc}</b>.</div>  
            </div>      
        </div>  
    </div>  """ 
    st.markdown(summary_html, unsafe_allow_html=True)




# Ensure 'RegisterDate' is in datetime format and handle invalid dates
filtered_df['RegisterDate'] = pd.to_datetime(filtered_df['RegisterDate'], errors='coerce')

# Drop rows with NaT in 'RegisterDate' to avoid NaT errors
filtered_df = filtered_df.dropna(subset=['RegisterDate'])

# Now, check if the 'RegisterDate' column is not empty before proceeding
if not filtered_df['RegisterDate'].empty:
    # Extract month and year from the valid dates
    filtered_df['Month'] = filtered_df['RegisterDate'].dt.month
    filtered_df['Year'] = filtered_df['RegisterDate'].dt.year

    # Generate all months for the x-axis
    all_months = pd.date_range(start=filtered_df['RegisterDate'].min(), 
                               end=filtered_df['RegisterDate'].max(), freq='MS').strftime('%b %Y')

    # Group by Year and Month, and calculate Registration count
    monthly_registration = filtered_df.groupby(['Year', 'Month'])['memberID'].count().reset_index(name='Registration')

    # Create 'Month-Year' column for plotting or display
    monthly_registration['Month-Year'] = pd.to_datetime(
        monthly_registration['Year'].astype(str) + '-' + monthly_registration['Month'].astype(str).str.zfill(2)
    ).dt.strftime('%b %Y')

    # Verify column names after modification
    print(monthly_registration.columns)
else:
    # Handle the case when there are no valid dates available
    all_months = []
    monthly_registration = pd.DataFrame()  # Empty DataFrame or handle as needed
    print("No valid date data available.")

# Ensure all months are represented
def fill_missing_months(data, all_months):
    data = data.set_index('Month-Year')
    data = data.reindex(all_months, fill_value=0)
    data.reset_index(inplace=True)
    data.rename(columns={'index': 'Month-Year'}, inplace=True)
    return data

# Now, ensure that you're using the correct column names and checking for empty DataFrame
if not monthly_registration.empty:
    filled_monthly = fill_missing_months(monthly_registration[['Month-Year', 'Registration']], all_months)
else:
    print("monthly_registration DataFrame is empty.")
    filled_monthly = pd.DataFrame()  # Handle the empty case

# Proceed with plotting if data exists
if not filled_monthly.empty:
    fig1 = px.bar(
        filled_monthly,
        x='Month-Year',
        y='Registration',
        title="Monthly Registration",
        color_discrete_sequence=px.colors.sequential.Blues
    )
    fig1.update_xaxes(type='category')

    with col2:
        download_button(filled_monthly, "download-monthly-report")
        st.plotly_chart(fig1, use_container_width=True, key='fig1')
else:
    print("No data to display for monthly Registration.")



col3, col4 = st.columns([2,2])

# Quaterly Chart
filtered_df['Quarter'] = filtered_df['RegisterDate'].dt.to_period('Q')
quarterly_registration = filtered_df.groupby(filtered_df['RegisterDate'].dt.to_period('Q'))['memberID'].count().reset_index(name='Registration')

# Format Quarter for display
quarterly_registration['Quarter'] = quarterly_registration['RegisterDate'].apply(lambda x: f"{x.start_time.strftime('%b')}-{x.end_time.strftime('%b')} {x.start_time.year}")
# Plot the chart
fig2 = px.bar(
    quarterly_registration,
    x='Quarter',
    y='Registration',  # Ensure this matches the column name in the DataFrame
    title="Quarterly Registration",
    color_discrete_sequence=px.colors.sequential.Greens
)
fig2.update_xaxes(type='category')

# Display the chart and download button
with col3:    
    download_button(quarterly_registration, "download-quarterly-report")
    st.plotly_chart(fig2)

# Yearly Chart
yearly_registration = filtered_df.groupby(filtered_df['RegisterDate'].dt.year)['memberID'].count().reset_index(name='Registration')
yearly_registration.columns = ['Year', 'Registration']

# Pie chart instead of line chart
fig3 = px.pie(
    yearly_registration,
    names='Year',
    values='Registration',
    title="Yearly Registration Distribution",
    color='Year',
    color_discrete_sequence=px.colors.qualitative.Set2
)
fig3.update_traces(textinfo='percent+label')
with col4:
    download_button(yearly_registration, "download-yearly-report")
    st.plotly_chart(fig3)

col5, col6 = st.columns([2,2])
total_registered = len(filtered_df)  # Total members in the dataset
active_members = len(filtered_df[filtered_df['memberStatus'] == 'Active'])  # Active members

# Creating a DataFrame for the comparison
comparison_data = pd.DataFrame({
    'memberStatus': ['Total Registered', 'Active Members'],
    'count': [total_registered, active_members]
})

# Plotting the comparison bar chart
fig_comparison = px.bar(
    comparison_data, x='memberStatus', y='count', 
    title='Total Registered vs Active Members', text='count', 
    color='memberStatus', color_discrete_sequence=['#ADD8E6', '#E6E6FA']
)
with col5:
    download_button(comparison_data, "total_vs_active_members_comparison")
    st.plotly_chart(fig_comparison, use_container_width=True)

# Grouping by memberStatus to show count of active and inactive members
member_status = filtered_df['memberStatus'].value_counts().reset_index(name='count')
member_status.columns = ['memberStatus', 'count']  # Rename columns for clarity

# Plotting the bar chart for Active vs Inactive Members
fig_member_status = px.bar(
    member_status, x='memberStatus', y='count', 
    title='Active vs Inactive Members', text='count', 
    color='memberStatus', color_discrete_sequence=['#ADD8E6', '#E6E6FA']
)

# Display the chart in Streamlit
with col6:
    download_button(member_status, "active_vs_inactive_members")
    st.plotly_chart(fig_member_status, use_container_width=True)

col7, col8 = st.columns([2,2])
kyc_pending = filtered_df[filtered_df['KYCStatus'] == 0]
kyc_status_count = kyc_pending['MemberType'].value_counts().reset_index()
kyc_status_count.columns = ['MemberType', 'count']
fig6 = px.bar(
    kyc_status_count, x='MemberType', y='count', 
    title='Pending KYC Status by Member Type', text='count', color_discrete_sequence=['#FFDAB9']
)
with col7:
    download_button(kyc_status_count, "kyc_pending_count")
    st.plotly_chart(fig6, use_container_width=True)


member_tier_count = filtered_df['MemberTier'].value_counts().reset_index()
member_tier_count.columns = ['MemberTier', 'count']
fig5 = px.bar(
    member_tier_count, x='MemberTier', y='count', 
    title='Count by Member Tier', text='count', color_discrete_sequence=['#FFB6C1']
)
with col8:
    download_button(member_tier_count, "member_tier_count")
    st.plotly_chart(fig5, use_container_width=True)