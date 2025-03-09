import streamlit as st
import pandas as pd  
import datetime  
from datetime import timedelta
import plotly.express as px
import plotly.graph_objects as go 
import io
from io import BytesIO, StringIO
import base64  
from fpdf import FPDF
from PIL import Image, ImageDraw 
from dash import Dash, html, dcc

# Page Configuration  
st.set_page_config(page_title='Elevatoz loyalty Dashboard', layout='wide')  
  
# Custom Styling
with open('E:/Elevatoz intern/Python Dashboard/Dashboard/style.css') as f:
   st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)  
   
# Function to format numbers into "k" format  
def format_to_k(value):  
   """Format numbers into 'k' format."""   
   if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
   elif value >= 1_000:
        return f"{value / 1_000:.1f}K"
   else:
        return str(value)
  
# Load Data Function  
@st.cache_data  
def load_data(file_path):  
   """Load data from a CSV or Excel file."""  
   try:  
      if file_path.endswith('.csv'):  
        return pd.read_csv(file_path, encoding='latin1')  
      elif file_path.endswith('.xlsx'):  
        return pd.read_excel(file_path)  
   except Exception as e:  
      st.error(f"Error loading file: {e}")  
      return pd.DataFrame()

# Date Filter Options  
DATE_FILTER_OPTIONS = [  
   "All", "Today", "Yesterday", "Last 7 Days", "Last Week",  
   "Last 30 Days", "Last Month", "Last 3 Months", "Last 12 Months", "Custom Date Range"  
]  
  
# Apply filters function with zones from dataframe
def apply_filters(df, tab_name):
   """Apply filters to the data."""
   col1, col2, col3, col4, col5, col6 = st.columns([19,19,19,19,19,5])

   # Ensure 'Date' is in datetime format
   if 'RegisterDate' in df.columns:
      df['RegisterDate'] = pd.to_datetime(df['RegisterDate'], errors='coerce')
   else:
      st.warning("Date column not found in the DataFrame!")
      return df  # Exit if Date column is missing

   # Date Filter
   with col1:
      date_filter = st.selectbox(f"Select Date", DATE_FILTER_OPTIONS, key=f"date_{tab_name}")
      if date_filter == "Custom Date Range":
         date_range = st.date_input(f"Select Date Range ({tab_name})", [], key=f"custom_date_range_{tab_name}")
      else:
         date_range = []

   today = datetime.datetime.today()
   if date_filter == "Today":
      start_date, end_date = today, today
   elif date_filter == "Yesterday":
      start_date, end_date = today - timedelta(days=1), today - timedelta(days=1)
   elif date_filter == "Last 7 Days":
      start_date, end_date = today - timedelta(days=7), today
   elif date_filter == "Last Week":
      start_date = today - timedelta(days=today.weekday() + 7)
      end_date = start_date + timedelta(days=6)
   elif date_filter == "Last 30 Days":
      start_date, end_date = today - timedelta(days=30), today
   elif date_filter == "Last Month":
      start_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
      end_date = start_date + timedelta(days=30)
   elif date_filter == "Last 3 Months":
      start_date, end_date = today - timedelta(days=90), today
   elif date_filter == "Last 12 Months":
      start_date, end_date = today - timedelta(days=365), today
   elif date_filter == "Custom Date Range" and date_range == 2:
      start_date, end_date = date_range[0], date_range[1]
   else:
      start_date, end_date = None, None
      
   if start_date and end_date:
      df = df[(df['RegisterDate'] >= pd.to_datetime(start_date)) &
               (df['RegisterDate'] <= pd.to_datetime(end_date))]

   # Ensure 'Zone' column exists and handle missing values
   if 'Zone' in df.columns:
      df['Zone'] = df['Zone'].fillna('Unknown')
      df['Zone'] = df['Zone'].astype(str)
   else:
      st.warning("Zone column not found in the DataFrame!")
      return df


   # Dynamic Filters
   with col2:
      zone_filter = st.selectbox(f"Select Zone", ['All'] + sorted(df['Zone'].unique()), key=f"zone_{tab_name}")
   filtered_states = []
   if zone_filter != 'All':
      filtered_states = list(df[df['Zone'] == zone_filter]['State'].unique())
   else:
      filtered_states = list(df['State'].unique())

   with col3:
      state_filter = st.selectbox(f"Select State", ['All'] + filtered_states, key=f"state_{tab_name}")
   filtered_cities = []
   if state_filter != 'All':
      filtered_cities = list(df[df['State'] == state_filter]['City'].unique())
   else:
      filtered_cities = list(df['City'].unique())

   with col4:
      city_filter = st.selectbox(f"Select City", ['All'] + filtered_cities, key=f"city_{tab_name}")

   # Initialize tier_filter with a default value
   tier_filter = 'All'
   with col5:
      if 'memberTier' in df.columns: 
         tier_filter = st.selectbox(f"Select Tier", ['All'] + list(df['memberTier'].unique()), key=f"tier_{tab_name}")   
      else:  
         st.write("")

   # Reset Filters Button
   with col6:  
      if st.button("",icon=":material/restart_alt:",type="secondary"):
         st.session_state[f"date_{tab_name}"] = "All"
         st.session_state[f"zone_{tab_name}"] = "All"
         st.session_state[f"state_{tab_name}"] = "All"
         st.session_state[f"city_{tab_name}"] = "All"
         st.session_state[f"tier_{tab_name}"] = "All"
         st.rerun()
         
   # Initialize session state variables if not already initialized
   # for key in ['date_filter', 'zone_filter', 'state_filter', 'city_filter', 'tier_filter']:
   #    if key not in st.session_state:
   #       st.session_state[key] = 'Select'
   # with col6:
   #  if st.button("", icon=":material/restart_alt:", key="reset_emoji"):
   #      for key in ['date_filter', 'zone_filter', 'state_filter', 'city_filter', 'tier_filter']:
   #          st.session_state[key] = 'All'
   #      st.rerun()
                
   # Apply Filters
   if zone_filter != 'All':
      df = df[df['Zone'] == zone_filter]
   if state_filter != 'All':
      df = df[df['State'] == state_filter]
   if city_filter != 'All':
      df = df[df['City'] == city_filter]
   if tier_filter is not None and tier_filter != 'All':   
      df = df[df['memberTier'] == tier_filter] 

   return df

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
   pdf.cell(200, 10, txt="Transaction Report", ln=True, align='C')  
   
   # Calculate column widths based on the longest header  
   col_widths = [pdf.get_string_width(col) + 10 for col in df.columns]  
   row_height = 10  
   
   # Set table header  
   pdf.set_font("Arial", size=10, style='B')  # Bold for headers  
   for i, col in enumerate(df.columns):  
      pdf.cell(col_widths[i], row_height, col, border=1, align='C')  
   pdf.ln()  # Move to the next line  
   
   # Add table rows  
   pdf.set_font("Arial", size=10)  
   for i, row in df.iterrows():  
      for j, value in enumerate(row):  
         pdf.cell(col_widths[j], row_height, str(value), border=1, align='C')  
      pdf.ln()  
   
   # pdf_output = BytesIO()
   # pdf.output(pdf_output)  
   # pdf_b64 = base64.b64encode(pdf_output.getvalue()).decode() 
   
   pdf_output = BytesIO()
   pdf.output(pdf_output,'S')
   pdf_output.seek(0) 
   pdf_b64 = base64.b64encode(pdf_output.getvalue()).decode()
   
   # Prepare JPG image output using Plotly Express for the provided figure  
   jpg_output = BytesIO()  
   fig.write_image(jpg_output, format='jpg')  # Requires kaleido for static export  
   jpg_b64 = base64.b64encode(jpg_output.getvalue()).decode()
   
   # Read from the physical GIF file from the disk  
   with open('E:/Elevatoz intern/Python Dashboard/Dashboard/download.png', 'rb') as gif_file:  
      gif_b64 = base64.b64encode(gif_file.read()).decode()   

   # Display the download options with the correct MIME type for PNG  
   st.markdown(f"""  
      <div class="download-container">  
         <div class="dropdown-container">  
            <img src="data:image/png;base64,{gif_b64}" alt="Download Icon">  
            <div class="dropdown-content">  
               <a href="data:file/csv;base64,{csv_b64}" download="{filename}.csv">Download CSV</a>  
               <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_b64}" download="{filename}.xlsx">Download Excel</a>  
               <a href="data:application/pdf;base64,{pdf_b64}" download="{filename}.pdf">Download PDF</a>
               <a href="data:image/jpeg;base64,{jpg_b64}" download="{filename}.jpg">Download JPG</a>  
            </div>  
         </div>  
      </div>  
   """, unsafe_allow_html=True)

# Title  
st.markdown("### Registration Dashboard")   
# tab1, tab2, tab3= st.tabs(["Registration", "Transaction", "Redemption"])  
  
# Registration Tab  
# with tab1:  
reg_file_path = 'E:/Elevatoz intern/Python Dashboard/Registrations_Sample.csv'  
reg_data = load_data(reg_file_path)  

if not reg_data.empty:  
   # Apply Filters  
   filtered_data = apply_filters(reg_data, "Registration")  

   # Calculate Total Active and Inactive Members  
   total_members = len(filtered_data)  
   active_members = len(filtered_data[filtered_data['memberStatus'] == 'Active'])  
   inactive_members = len(filtered_data[filtered_data['memberStatus'] == 'Inactive'])  

   # Calculate KYC Completion Rate (based on non-null values for key fields like email, mobile)  
   kyc_completed = filtered_data[['MobileNo', 'EmailAddress', 'Address1']].notnull().all(axis=1)  
   kyc_completion_rate = (kyc_completed.sum() / total_members) * 100 if total_members > 0 else 0 
   
   #charts to 3 
   top_states = filtered_data['State'].value_counts().head(10).reset_index()
   top_states.columns = ['State', 'Count']
   
   # Calculate Member Tier Distribution
   tier_distribution = filtered_data['MemberTier'].value_counts() 

   col1, col2 = st.columns([30, 70])  
   with col1:  
      summary_html = f"""  
         <div class='summary-container'>  
            <div class='summary-box'>  
               <div class='summary-value'>Insight Summary
                  <div class='summary-label'>1. <b>📊Total Members:</b><br> The total number of filtered registrations is <b>{total_members}</b></div>  
                  <div class='summary-label'>2. <b>✅ Active Members:</b><br> There are <b>{active_members}</b> members with an "Active" status.</div>  
                  <div class='summary-label'>3. <b>❌ Inactive Members:</b><br>  There are <b>{inactive_members}</b> members with an "Inactive" status.</div>  
                  <div class='summary-label'>4. <b>📑 KYC Completion Rate:</b><br>  The percentage of members who have completed KYC is <b>{kyc_completion_rate:.2f}%</b>.</div>  
                  <div class='summary-label'>5. <b>📈 Registration Trend:</b><br>  The monthly trend of registrations shows a volume of new registrations over time.</div>  
                  <div class='summary-label'>6. <b>📝 KYC Status Distribution:</b><br>  The breakdown of KYC statuses completed versus pending KYC.</div>  
                  <div class='summary-label'>7. <b>🗺️ Top 10 States by Registrations:</b><br>  The top 10 states with the highest number of registrations .</div>  
               </div>      
            </div>  
         </div>  
      """  
      st.markdown(summary_html, unsafe_allow_html=True)
         
   with col2:
         
      metric_html = f"""  
         <div class='metric-container'>  
            <div class='metric-box'>  
               <div class='metric-value'>{format_to_k(total_members)}</div>  
               <div class='metric-label'>Total Members</div>  
            </div>  
            <div class='metric-box'>  
               <div class='metric-value'>{format_to_k(active_members)}</div>  
               <div class='metric-label'>Active Members</div>  
            </div>  
            <div class='metric-box'>  
               <div class='metric-value'>{format_to_k(inactive_members)}</div>  
               <div class='metric-label'>Inactive Members</div>  
            </div>  
            <div class='metric-box'>  
               <div class='metric-value'>{kyc_completion_rate:.2f}%</div>  
               <div class='metric-label'>KYC Completion Rate</div>  
            </div>  
         </div>  
      """  
      st.markdown(metric_html, unsafe_allow_html=True)
      
      col3, col4 = st.columns([60, 40])

      with col3:  
      #chart 1
        # Convert RegisterDate to datetime (if it's not already in datetime format)
        filtered_data['RegisterDate'] = pd.to_datetime(filtered_data['RegisterDate'],format='%d-%m-%Y %H:%M', errors='coerce')
        
        # Now group the data by month and count registrations
        registration_trend = filtered_data.groupby(filtered_data['RegisterDate'].dt.to_period('M')).size().reset_index()
        registration_trend.columns = ['RegisterDate', 'Count']
        
        # Convert the 'RegisterDate' back to a string for better display in the chart
        registration_trend['RegisterDate'] = registration_trend['RegisterDate'].astype(str)
        
        # Create a responsive line chart with Plotly
        fig = px.line(registration_trend, x='RegisterDate', y='Count', 
                    title='Registration Trend',
                    markers=True, 
                    color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(
        height=420, 
        margin=dict(l=20, r=20, t=50, b=20),  
        paper_bgcolor='rgba(255, 255, 255, 0.8)',  
        plot_bgcolor='rgba(255, 255, 255, 0.8)',  
        font=dict(size=12),  
        yaxis_tickformat='d',
        )   
        download_button(registration_trend, "download-registration_trend")
        st.plotly_chart(fig)
            
      with col4:  
      #chart 2
        # KYC Status Analysis with Donut Chart using Plotly Express
        filtered_data['KYCStatus'] = filtered_data['KYCStatus'].map({0: 'Pending', 1: 'Completed'})
        kyc_status_counts = filtered_data['KYCStatus'].value_counts()

        # Create a donut chart using Plotly Express
        fig = px.pie(names=kyc_status_counts.index, values=kyc_status_counts.values, 
                    hole=0.4, title="KYC Status Distribution",
                    color_discrete_sequence=['#F8AE54', '#B6A6E9'])
        fig.update_layout(
        yaxis_tickformat='d',
            height=420,  # Adjust the height as needed
            width=500,   # Adjust the width as needed
            title_x=0.5,  # Center the title
            title_y=0.9, # Adjust title position
            showlegend=True,
            hovermode="closest",
        )
        download_button(kyc_status_counts.reset_index(),'kyc-status')
        # Add chart styling to the container
        st.plotly_chart(fig,use_container_width=True)
         
   col4,col5 = st.columns([70,30])
   with col4:
      
      fig = px.bar(top_states, x='State', y='Count', title='Top 10 States by Registrations', text='Count', color='Count',
                  color_continuous_scale=[
                        'rgba(67, 148, 229, 0.6)',  # Light Blue
                        'rgba(135, 111, 212, 0.6)',  # Light Purple
                        'rgba(199, 199, 199, 0.6)',  # Light Gray
                        'rgba(248, 174, 84, 0.6)'   # Light Orange
                  ])
      fig.update_layout(
         height=420, 
         yaxis=dict(showgrid=False) 
      )
      download_button(tier_distribution.reset_index(),'top_states') #top_states
      # Add chart styling to the container
      st.plotly_chart(fig,use_container_width=True)
      
   
   with col5:
      # Create Donut Chart for Member Tier Distribution
      fig = px.pie(
         names=tier_distribution.index,
         values=tier_distribution.values,
         title="Member Tier Distribution",
         hole=0.4,  # Creates the donut shape
         color_discrete_sequence=['#B6A6E9' ,'#F8AE54','#92C5F9','#AFDC8F' ])
      fig.update_layout(
         height=420, 
      )
      download_button(top_states, "download-tier-distribution") #download-top-states
      # Display the Donut Chart
      st.plotly_chart(fig, use_container_width=True)
      
      
else:  
   st.write("No registration data available.")

