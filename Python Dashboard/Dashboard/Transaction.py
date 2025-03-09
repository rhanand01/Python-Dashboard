import streamlit as st
import pandas as pd  
import datetime  
from datetime import timedelta
import plotly.express as px
import plotly.graph_objects as go 
from io import BytesIO
import io
from io import BytesIO
import base64  
from fpdf import FPDF
from PIL import Image, ImageDraw 

# Page Configuration  
st.set_page_config(page_title='Elevatoz Dashboard', layout='wide')  

# Custom Styling
with open('E:\\Elevatoz intern\\Python Dashboard\\Dashboard\\style.css') as f:
   st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)  
   
# Function to format numbers into "k" format  
def format_to_k(value):  
   """Format numbers into 'k' format."""  
   if value >= 1000:  
      return f"{value / 1000:.1f}k"  
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
   if 'transactionDate' in df.columns:
      df['transactionDate'] = pd.to_datetime(df['transactionDate'], errors='coerce')
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
      df = df[(df['transactionDate'] >= pd.to_datetime(start_date)) &
               (df['transactionDate'] <= pd.to_datetime(end_date))]

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
      filtered_states = list(df[df['Zone'] == zone_filter]['memberState'].unique())
   else:
      filtered_states = list(df['memberState'].unique())

   with col3:
      state_filter = st.selectbox(f"Select State", ['All'] + filtered_states, key=f"state_{tab_name}")
   filtered_cities = []
   if state_filter != 'All':
      filtered_cities = list(df[df['memberState'] == state_filter]['memberCity'].unique())
   else:
      filtered_cities = list(df['memberCity'].unique())

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
      if st.button("",icon=":material/restart_alt:", key=f"reset_{tab_name}",type="secondary"):
         st.session_state[f"date_{tab_name}"] = "All"
         st.session_state[f"zone_{tab_name}"] = "All"
         st.session_state[f"state_{tab_name}"] = "All"
         st.session_state[f"city_{tab_name}"] = "All"
         st.session_state[f"tier_{tab_name}"] = "All"
         st.rerun()

   # Apply Filters
   if zone_filter != 'All':
      df = df[df['Zone'] == zone_filter]
   if state_filter != 'All':
      df = df[df['memberState'] == state_filter]
   if city_filter != 'All':
      df = df[df['memberCity'] == city_filter]
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
   
   pdf_output = io.StringIO()  
   pdf.output(pdf_output, 'S')  
   pdf_b64 = base64.b64encode(pdf_output.getvalue().encode()).decode()
   
   # Prepare JPG image output using Plotly Express for the provided figure  
   jpg_output = BytesIO()  
   fig.write_image(jpg_output, format='jpg')  # Requires kaleido for static export  
   jpg_b64 = base64.b64encode(jpg_output.getvalue()).decode()
   
   # Read from the physical GIF file from the disk  
   with open('E:\\Elevatoz intern\\Python Dashboard\\Dashboard\\download.png', 'rb') as gif_file:  
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

st.markdown("### Transaction Dashboard")
# Load transaction data
trans_file_path = 'E:\\Elevatoz intern\\Python Dashboard\\Transactions_sample.csv'
trans_data = load_data(trans_file_path)

if not trans_data.empty:
   # Apply filters
   filtered_data = apply_filters(trans_data, "Transaction")

   # Calculate metrics
   transaction_volume = len(filtered_data)
   member_count = len(filtered_data['memberID'].unique())
   total_points = filtered_data['memberPoints'].sum()
   redemption_points = filtered_data[filtered_data['pointType'] == 'Redemption']['memberPoints'].sum()

   member_engagement = (member_count / transaction_volume * 100) if transaction_volume > 0 else 0
   average_transaction_value = (total_points / transaction_volume) if transaction_volume > 0 else 0
   point_earning_rate = (total_points / member_count) if member_count > 0 else 0
   point_redemption_rate = (redemption_points / member_count) if member_count > 0 else 0

   # Calculate member retention rate
   trans_data['transactionDate'] = pd.to_datetime(trans_data['transactionDate'])
   current_period = trans_data[trans_data['transactionDate'] >= '2022-01-01']
   previous_period = trans_data[trans_data['transactionDate'] < '2022-01-01']

   if len(previous_period['memberID'].unique()) == 0:
      member_retention_rate = 0
   else:
      member_retention_rate = (
            len(current_period['memberID'].unique()) / len(previous_period['memberID'].unique())
      ) * 100

   # Count transactions by tier
   tier_counts = trans_data['memberTier'].value_counts().to_dict()
   diamond_count = tier_counts.get('Diamond', 0)
   gold_count = tier_counts.get('Gold', 0)
   platinum_count = tier_counts.get('Platinum', 0)
   silver_count = tier_counts.get('Silver', 0)

   # Summary display
   col1, col2 = st.columns([30, 70])
   with col1:
      summary_html = f"""
      <div class='summary-container'>
            <div class='summary-box'>
               <div class='summary-value'>Insight Summary
                  <div class='summary-label'><b>1.💳 Transaction Volume:</b><br> The total number of transactions in the dataset is <b>{transaction_volume}</b>.</div>   
                  <div class='summary-label'><b>2.📊 Member Engagement:</b><br>  The percentage of unique members engaged in transactions is <b>{member_engagement:.2f}%</b>.</div>   
                  <div class='summary-label'><b>3.💰 Average Transaction Value:</b><br>  The average value of a transaction is <b>{average_transaction_value:.2f}</b>.</div>   
                  <div class='summary-label'><b>4.🎯 Point Earning Rate:</b><br>  The average points earned per member is <b>{point_earning_rate:.2f}</b>.</div>       
                  <div class='summary-label'><b>6.💎 Diamond Transactions:</b><br>  The total number of Diamond-tier transactions is <b>{diamond_count}</b>.</div>  
                  <div class='summary-label'><b>7.🏆 Platinum Transactions:</b><br>  The total number of Platinum-tier transactions is <b>{platinum_count}</b>.</div>  
                  <div class='summary-label'><b>8.🥇 Gold Transactions:</b><br>  The total number of Gold-tier transactions is <b>{gold_count}</b>.</div>    
                  <div class='summary-label'><b>9.🥈 Silver Transactions:</b><br>  The total number of Silver-tier transactions is <b>{silver_count}</b>.</div>     
               </div>
            </div>
      </div>
      """
      st.markdown(summary_html, unsafe_allow_html=True)

   with col2:
      metric_html = f"""
      <div class='metric-container'>
            <div class='metric-box'>
               <div class='metric-value'>{format_to_k(transaction_volume)}</div>
               <div class='metric-label'>Transaction Volume</div>
            </div>
            <div class='metric-box'>
               <div class='metric-value'>{member_engagement:.2f}%</div>
               <div class='metric-label'>Member Engagement</div>
            </div>
            <div class='metric-box'>
               <div class='metric-value'>{average_transaction_value:.2f}</div>
               <div class='metric-label'>Avg Transaction Value</div>
            </div>
            <div class='metric-box'>
               <div class='metric-value'>{point_earning_rate:.2f}</div>
               <div class='metric-label'>Point Earning Rate</div>
            </div>
            <div class='metric-box'>
               <div class='metric-value'>{format_to_k(diamond_count)}</div>
               <div class='metric-label'>Diamond Transactions</div>
            </div>
            <div class='metric-box'>
               <div class='metric-value'>{format_to_k(platinum_count)}</div>
               <div class='metric-label'>Platinum Transactions</div>
            </div>
            <div class='metric-box'>
               <div class='metric-value'>{format_to_k(gold_count)}</div>
               <div class='metric-label'>Gold Transactions</div>
            </div>
            <div class='metric-box'>
               <div class='metric-value'>{format_to_k(silver_count)}</div>
               <div class='metric-label'>Silver Transactions</div>
            </div>
      </div>
      """
      st.markdown(metric_html, unsafe_allow_html=True)

   # Transaction percentage by tier - Pie chart
      col3, col4 = st.columns([60, 40])
      with col3:
         fig = px.bar(
                  x=["Transaction Volume", "Member Count"],
                  y=[transaction_volume, member_count],
                  text=[transaction_volume, member_count],
                  title="Transaction Volume vs Member Count",
                  labels={"x": "Metric", "y": "Count"},
                  color_discrete_sequence=['#AFDC8F', '#B6A6E9']

               )
         fig.update_layout(
               yaxis=dict(showgrid=False),
               yaxis_tickformat='d',
                     height=370, # Adjust the height as needed 
                     title_x=0.2,  # Center the title
                     title_y=0.9,
                     showlegend=True,
            )
         download_data = pd.DataFrame({
                  "Metric": ["Transaction Volume", "Member Count"],
                  "Count": [transaction_volume, member_count]
               })
         download_button(download_data, "download-transaction-member-count")

         st.plotly_chart(fig)
      
      with col4:
         fig = px.pie(
            names=["Engaged", "Not Engaged"],
            values=[member_engagement, 100 - member_engagement],
            title="Member Engagement Rate",
            hole=0.4,  # Donut Chart Style,
            color_discrete_sequence=['#F8AE54', '#B6A6E9']
         )
         fig.update_layout(
               yaxis=dict(showgrid=False),
               yaxis_tickformat='d',
                     height=370, # Adjust the height as needed 
                     title_x=0.2,  # Center the title
                     title_y=0.9,
                     showlegend=True,
                     # plot_bgcolor='rgba(0,0,0,0)',
                     # paper_bgcolor='rgba(0,0,0,0)'
            )
         download_data = pd.DataFrame({
                     "Engagement Status": ["Engaged", "Not Engaged"],
                     "Percentage": [member_engagement, 100 - member_engagement]
                  })
         download_button(download_data, "download-member-engagement-rate")

         st.plotly_chart(fig)
            
#   # Top Performers: Members contributing the most in terms of points
   top_performers = (
      trans_data.groupby(['memberID', 'memberName'])['memberPoints'].sum().sort_values(ascending=False).reset_index().head(5)
   )
   col2,col3 = st.columns([50,50])
   with col2:
      fig = px.bar(
            top_performers,
            x='memberName',
            y='memberPoints',
            title="Top 5 Performers by Points",
            labels={'memberName': 'Member Name', 'memberPoints': 'Points'},
            text='memberPoints',
            # color='memberPoints',
            color_discrete_sequence=['#ffafcc']
         )
      fig.update_traces(textposition='outside',)
      fig.update_layout(
            yaxis=dict(showgrid=False),
                  yaxis_tickformat='d',
                  height=372, # Adjust the height as needed 
                  title_x=0.2,  # Center the title
                  title_y=0.9,
                  showlegend=True,
            )
      download_button(top_performers, "download-top-performer")
      st.plotly_chart(fig)
                  
   # Repeat Customers
   repeat_data = trans_data['memberID'].value_counts()
   repeat_data = repeat_data.reset_index()
   repeat_data.columns = ['memberID', 'Transaction Count']
   repeat_data['Customer Type'] = repeat_data['Transaction Count'].apply(
      lambda x: 'Repeat' if x > 1 else 'One-Time'
   )
   churn_data = trans_data.groupby('memberStatus')['memberID'].nunique().reset_index()
   churn_data.columns = ['Member Status', 'Member Count']
   
   with col3:
      fig = px.bar(
         churn_data,
         x='Member Status',
         y='Member Count',
         title="Churn Analysis by Member Status",
         labels={'Member Status': 'Status', 'Member Count': 'Count'},
         text='Member Count',
         color_discrete_sequence=['#a2d2ff']
      )
      fig.update_traces(textposition='outside')
      fig.update_layout(
         yaxis=dict(showgrid=False),
                  yaxis_tickformat='d',
                  height=372, # Adjust the height as needed 
                  title_x=0.2,  # Center the title
                  title_y=0.9,
                  showlegend=True,
               )
      download_button(churn_data, "download-churn-data")
      st.plotly_chart(fig)
else:
   st.write("No transaction data available.")
