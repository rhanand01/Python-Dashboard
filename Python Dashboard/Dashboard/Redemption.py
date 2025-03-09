import streamlit as st
import pandas as pd  
import datetime  
from datetime import timedelta
import plotly.express as px
import base64
import plotly.graph_objects as go 
from io import BytesIO
import io
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
   if 'orderedDate' in df.columns:
      df['orderedDate'] = pd.to_datetime(df['orderedDate'], errors='coerce')
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
      df = df[(df['orderedDate'] >= pd.to_datetime(start_date)) &
               (df['orderedDate'] <= pd.to_datetime(end_date))]

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
      filtered_states = list(df[df['Zone'] == zone_filter]['deliveryState'].unique())
   else:
      filtered_states = list(df['deliveryState'].unique())

   with col3:
      state_filter = st.selectbox(f"Select State", ['All'] + filtered_states, key=f"state_{tab_name}")
   filtered_cities = []
   if state_filter != 'All':
      filtered_cities = list(df[df['deliveryState'] == state_filter]['deliveryCity'].unique())
   else:
      filtered_cities = list(df['deliveryCity'].unique())

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
         st.experimental_rerun()

   # Apply Filters
   if zone_filter != 'All':
      df = df[df['Zone'] == zone_filter]
   if state_filter != 'All':
      df = df[df['deliveryState'] == state_filter]
   if city_filter != 'All':
      df = df[df['deliveryCity'] == city_filter]
   if tier_filter is not None and tier_filter != 'All':   
      df = df[df['memberTier'] == tier_filter] 

   return df

#download files in different format
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
   fig1.write_image(jpg_output, format='jpg')  # Requires kaleido for static export  
   jpg_b64 = base64.b64encode(jpg_output.getvalue()).decode()
   
#    # Read from the physical GIF file from the disk  
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

# Redemption Tab  
st.markdown("### Redemption Dashboard")
# with tab3:  
red_file_path = 'E:/Elevatoz intern/Python Dashboard/Redemptions_Sample.csv'  
red_data = load_data(red_file_path)

if not red_data.empty:
   filtered_data = apply_filters(red_data, "Redemption")

   # 1. Customer Retention Rate
   active_members = filtered_data[filtered_data['memberStatus'] == 'Active']['memberID'].nunique()
   total_members = filtered_data['memberID'].nunique()
   customer_retention_rate = (active_members / total_members) * 100 if total_members > 0 else 0

   # 2. Conversion Rate
   redeemed_members = filtered_data['memberID'].nunique()
   conversion_rate = (redeemed_members / total_members) * 100 if redeemed_members > 0 else 0

   # 3. Redemption Rate
   redemptions = filtered_data['orderID'].nunique()
   redemption_rate = (redemptions / total_members) * 100 if redemptions > 0 else 0

   # 4. Point Utilization Rate
   total_points_redeemed = filtered_data['rewardPoints'].sum()
   total_points_available = total_points_redeemed + filtered_data['balancePoints'].sum()
   point_utilization_rate = (total_points_redeemed / total_points_available) * 100 if total_points_available > 0 else 0

# 5 .Calculate average redemption value  
   average_redemption_value = red_data['rewardPoints'].sum() / len(red_data[red_data['rewardName'].notnull()])  
   print(f'Average Redemption Value: {average_redemption_value}')  
      
# Count redemptions by each specific tier
   total_redemptions = red_data.shape[0]
   diamond_count = red_data[red_data['memberTier'] == 'Diamond'].shape[0]
   gold_count = red_data[red_data['memberTier'] == 'Gold'].shape[0]
   platinum_count = red_data[red_data['memberTier'] == 'Platinum'].shape[0]
   silver_count = red_data[red_data['memberTier'] == 'Silver'].shape[0]

# Calculate balance points  
   balance_points = red_data['balancePoints'].sum()  
   bal_points = balance_points / 1_000_000

   # Summary and metrics display
   col1, col2 = st.columns([30, 70])  
   with col1:  
      summary_html = f"""  
            <div class='summary-container'>  
               <div class='summary-box'>  
                  <div class='summary-value'>Insight Summary</div>
                  <div class='summary-label'><b>1.📈 Customer Retention Rate:</b><br> Percentage of customers who remain active and continue to make purchases is <b>{customer_retention_rate:.2f}%</b>.</div>   
                  <div class='summary-label'><b>2.⭐️ Point Utilization Rate:</b><br> percentage of points that are being used by customers is <b>{point_utilization_rate:.2f}%</b>.</div>   
                  <div class='summary-label'><b>3.🎁 Total Redemption:</b><br> Total number of redemptions made by customers is <b>{total_redemptions}<b>.</div>   
                  <div class='summary-label'><b>4.⭐️ Balance Points:</b><br> Total Remaining points after redemption is <b>{bal_points:.2f}M</b>.</div>       
                  <div class='summary-label'><b>6.💎 Diamond Redemption:</b><br>  The total number of Diamond-tier Redemption is <b>{diamond_count}</b>.</div>  
                  <div class='summary-label'><b>7.🏆 Platinum Redemption:</b><br>  The total number of Platinum-tier Redemption is <b>{platinum_count}</b>.</div>  
                  <div class='summary-label'><b>8.🥇 Gold Redemption:</b><br>  The total number of Gold-tier Redemption is <b>{gold_count}</b>.</div>    
                  <div class='summary-label'><b>9.🥈 Silver Redemption:</b><br>  The total number of Silver-tier Redemption is <b>{silver_count}</b>.</div>   
               </div>  
            </div>  
      """  
      st.markdown(summary_html, unsafe_allow_html=True)

   with col2:
      metric_html = f"""  
            <div class='metric-container'>   
               <div class='metric-box'>  
                  <div class='metric-value'>{customer_retention_rate:.2f}%</div>  
                  <div class='metric-label'>Customer Retention Rate</div>  
               </div>  
               <div class='metric-box'>  
                  <div class='metric-value'>{point_utilization_rate:.2f}%</div>  
                  <div class='metric-label'>Point Utilization Rate</div>  
               </div>  
               <div class='metric-box'>  
                  <div class='metric-value'>{total_redemptions}</div>  
                  <div class='metric-label'>Total Redemption</div>  
               </div>
               <div class='metric-box'>  
                  <div class='metric-value'>{diamond_count}</div>  
                  <div class='metric-label'>Diamond member redemption</div>  
               </div>
               <div class='metric-box'>  
                  <div class='metric-value'>{platinum_count}</div>  
                  <div class='metric-label'>Platinum member redemption</div>  
               </div>
               <div class='metric-box'>  
                  <div class='metric-value'>{gold_count}</div>  
                  <div class='metric-label'>Gold member redemption</div>  
               </div>
               <div class='metric-box'>  
                  <div class='metric-value'>{silver_count}</div>  
                  <div class='metric-label'>Silver member redemption</div>  
               </div>
               <div class='metric-box'>  
                  <div class='metric-value'>{bal_points:.2f}M</div>  
                  <div class='metric-label'>Balance Points</div>  
               </div>
               
            </div>  
      """  
      st.markdown(metric_html, unsafe_allow_html=True)
      
      col3, col4 = st.columns([60, 40])
      with col3:
         orders_by_city = red_data.groupby('deliveryState').size().reset_index(name='Order Count')
         fig1 = px.bar(orders_by_city,
                        x='deliveryState',
                        y='Order Count',
                        title="Orders by state",
                        labels={'deliveryState': 'State', 'Order Count': 'Number of Orders'},
                        color='Order Count',
                        color_continuous_scale=['#4394E5','#876FD4','#C7C7C7','#F8AE54']
                        )
         fig1.update_layout(yaxis_tickformat='d',height=372,title_x=0.7,title_y=0.9)
         download_button(orders_by_city, "download-orders-by-city")
         st.plotly_chart(fig1,use_container_width=True)
         
      with col4:
         order_count_by_member_tier = red_data.groupby('memberTier').size().reset_index(name='Order Count')
         fig2 = px.pie(order_count_by_member_tier,
                           names='memberTier',
                           values='Order Count',
                           title="Orders by Member Tier",
                           hole=0.4,
                           color='memberTier',
                           color_discrete_sequence=['#AFDC8F', '#92C5F9', '#F8AE54', '#B6A6E9'])
         fig2.update_layout(
               height=372,  # Adjust the height as needed
               # width=400,   # Adjust the width as needed
               title_x=0.5,  # Center the title
               title_y=0.9, # Adjust title position
               showlegend=True,
               hovermode="closest",
            )
         download_button(order_count_by_member_tier, "download-order-count-by-membertier")
         st.plotly_chart(fig2)
            
   red_data['orderedDate'] = pd.to_datetime(red_data['orderedDate'],format='%d-%m-%Y %H:%M', errors='coerce')
   orders_by_date = red_data.groupby(red_data['orderedDate'].dt.date).size().reset_index(name='Order Count')
   fig3 = px.line(orders_by_date,
                  x='orderedDate',
                  y='Order Count',
                  title="Orders Over Time",
                  markers=True,
                  labels={'orderedDate': 'Date', 'Order Count': 'Number of Orders'})
   fig3.update_layout(title_x=0.9,
               title_y=0.9,
               )
   download_button(orders_by_date, "download-order-by-date")
   st.plotly_chart(fig3,use_container_width=True)
else:
   st.write("No redemption data available.")

