import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration for full-width layout
st.set_page_config(page_title="overview Dashboard", layout="wide")

# Add title for the page
st.markdown("### Dashboard Overview ")

# Sample data (replace with actual data from your CSV)
reg_file_path = pd.read_csv('E:/Elevatoz intern/Python Dashboard/Registrations_Sample.csv')  # Update path
trans_file_path = pd.read_csv('E:/Elevatoz intern/Python Dashboard/Transactions_sample.csv')  # Update path
red_file_path = pd.read_csv('E:/Elevatoz intern/Python Dashboard/Redemptions_Sample.csv')  # Update path

# Function to format large numbers like 2.3M
def format_large_number(number):
    if number >= 1_000_000:
        return f"{number/1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number/1_000:.1f}K"
    return str(number)
 
col1,col2 = st.columns(2)

with col1: 
   #Overall matrics 
   with open('E:/Elevatoz intern/Python Dashboard/Dashboard/style.css') as f:
      st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True) 
      
   # Calculate registration metrics
   total_members = len(reg_file_path)
   active_members = len(reg_file_path[reg_file_path['memberStatus'] == 'Active'])
   inactive_members = len(reg_file_path[reg_file_path['memberStatus'] == 'Inactive'])
   kyc_completed = reg_file_path[['MobileNo', 'EmailAddress', 'Address1']].notnull().all(axis=1)
   kyc_completion_rate = (kyc_completed.sum() / total_members) * 100 if total_members > 0 else 0

   # Load transaction data
   # trans_file_path = pd.read_csv(trans_file_path)

   trans_file_path['transactionDate'] = pd.to_datetime(trans_file_path['transactionDate'])
   # Calculate transaction metrics
   transaction_volume = len(trans_file_path)
   member_count = len(trans_file_path['memberID'].unique())
   total_points = trans_file_path['memberPoints'].sum()
   redemption_points = trans_file_path[trans_file_path['pointType'] == 'Redemption']['memberPoints'].sum()

   member_engagement = (member_count / transaction_volume * 100) if transaction_volume > 0 else 0
   average_transaction_value = (total_points / transaction_volume) if transaction_volume > 0 else 0
   point_earning_rate = (total_points / member_count) if member_count > 0 else 0

   current_period = trans_file_path[trans_file_path['transactionDate'] >= '2022-01-01']
   previous_period = trans_file_path[trans_file_path['transactionDate'] < '2022-01-01']

   member_retention_rate = (
      len(current_period['memberID'].unique()) / len(previous_period['memberID'].unique()) * 100
      if len(previous_period['memberID'].unique()) > 0 else 0
   )

   # Count transactions by tier
   tier_counts = trans_file_path['memberTier'].value_counts().to_dict()
   diamond_count = tier_counts.get('Diamond', 0)
   gold_count = tier_counts.get('Gold', 0)
   platinum_count = tier_counts.get('Platinum', 0)
   silver_count = tier_counts.get('Silver', 0)


   # Calculate redemption metrics
   active_members = red_file_path[red_file_path['memberStatus'] == 'Active']['memberID'].nunique()
   total_members = red_file_path['memberID'].nunique()
   customer_retention_rate = (active_members / total_members) * 100 if total_members > 0 else 0
   redeemed_members = red_file_path['memberID'].nunique()
   conversion_rate = (redeemed_members / total_members) * 100 if redeemed_members > 0 else 0

   redemptions = red_file_path['orderID'].nunique()
   redemption_rate = (redemptions / total_members) * 100 if redemptions > 0 else 0
   total_points_redeemed = red_file_path['rewardPoints'].sum()
   total_points_available = total_points_redeemed + red_file_path['balancePoints'].sum()
   point_utilization_rate = (total_points_redeemed / total_points_available) * 100 if total_points_available > 0 else 0
   average_redemption_value = red_file_path['rewardPoints'].sum() / len(red_file_path[red_file_path['rewardName'].notnull()])

   # Count redemptions by tier
   total_redemptions = red_file_path.shape[0]
   diamond_count = red_file_path[red_file_path['memberTier'] == 'Diamond'].shape[0]
   gold_count = red_file_path[red_file_path['memberTier'] == 'Gold'].shape[0]
   platinum_count = red_file_path[red_file_path['memberTier'] == 'Platinum'].shape[0]
   silver_count = red_file_path[red_file_path['memberTier'] == 'Silver'].shape[0]

   balance_points = red_file_path['balancePoints'].sum()
   bal_points = balance_points / 1_000_000

   metric_html = f"""
            <div class='met-container'>
               <!-- Registration Section -->
               <div class='met-section'>
                  <div class='met-row'>
                        <div class='met-box'>
                           <div class='met-value'>{format_large_number(total_members)}</div>
                           <div class='met-label'>Total Members</div>
                        </div>
                        <div class='met-box'>
                           <div class='met-value'>{format_large_number(active_members)}</div>
                           <div class='met-label'>Active Members</div>
                        </div>
                        <div class='met-box'>
                           <div class='met-value'>{format_large_number(inactive_members)}</div>
                           <div class='met-label'>Inactive Members</div>
                        </div>
                        <div class='met-box'>
                           <div class='met-value'>{kyc_completion_rate:.2f}%</div>
                           <div class='met-label'>KYC Completion</div>
                        </div>
                  </div>
               </div>

               <!-- Transaction Section -->
               <div class='met-section'>
                  <div class='met-row'>
                        <div class='met-box'>
                           <div class='met-value'>{format_large_number(transaction_volume)}</div>
                           <div class='met-label'>Transaction Volume</div>
                        </div>
                        <div class='met-box'>
                           <div class='met-value'>{member_engagement:.2f}%</div>
                           <div class='met-label'>Member Engagement</div>
                        </div>
                        <div class='met-box'>
                           <div class='met-value'>{average_transaction_value:.2f}</div>
                           <div class='met-label'>Avg Transaction</div>
                        </div>
                        <div class='met-box'>
                           <div class='met-value'>{point_earning_rate:.2f}</div>
                           <div class='met-label'>Point Earning Rate</div>
                        </div>
                  </div>
               </div>

               <!-- Redemption Section -->
               <div class='met-section'>
                  <div class='met-row'>
                        <div class='met-box'>
                           <div class='met-value'>{customer_retention_rate:.2f}%</div>
                           <div class='met-label'>Customer Retention</div>
                        </div>
                        <div class='met-box'>
                           <div class='met-value'>{point_utilization_rate:.2f}%</div>
                           <div class='met-label'>Point Utilization</div>
                        </div>
                        <div class='met-box'>
                           <div class='met-value'>{total_redemptions}</div>
                           <div class='met-label'>Total Redemption</div>
                        </div>
                        <div class='met-box'>
                           <div class='met-value'>{bal_points:.2f}M</div>
                           <div class='met-label'>Balance Points</div>
                        </div>
                  </div>
               </div>
            </div>
            """
   st.markdown(metric_html, unsafe_allow_html=True)

with col2:
      # Prepare state data for registrations, transactions, and redemptions
      states = reg_file_path['State'].unique()
      state_data = {}

      for state in states:
         registrations = len(reg_file_path[reg_file_path['State'] == state])
         transactions = len(trans_file_path[trans_file_path['memberState'] == state])
         redemptions = len(red_file_path[red_file_path['deliveryState'] == state])
         state_data[state] = {
            "registrations": registrations,
            "transactions": transactions,
            "redemptions": redemptions
         }

      # Prepare state data for OpenStreetMap visualization
      states = reg_file_path['State'].unique()
      state_coords = {
         "Andhra Pradesh": [15.9129, 79.7400],
         "Arunachal Pradesh": [27.0972, 93.3617],
         "Assam": [26.2006, 92.9376],
         "Bihar": [25.0961, 85.3131],
         "Chhattisgarh": [21.2787, 81.8661],
         "Goa": [15.2993, 74.1240],
         "Gujarat": [22.2587, 71.1924],
         "Haryana": [29.0588, 76.0856],
         "Himachal Pradesh": [32.0598, 77.1734],
         "Jharkhand": [23.6102, 85.2799],
         "Karnataka": [12.9716, 77.5946],
         "Kerala": [10.8505, 76.2711],
         "Madhya Pradesh": [23.2599, 77.4126],
         "Maharashtra": [19.0760, 72.8777],
         "Manipur": [24.6637, 93.9063],
         "Meghalaya": [25.4670, 91.3662],
         "Mizoram": [23.1645, 92.9376],
         "Nagaland": [26.1584, 94.5624],
         "Odisha": [20.9517, 85.0985],
         "Punjab": [31.1471, 75.3412],
         "Rajasthan": [27.0238, 74.2179],
         "Sikkim": [27.5330, 88.6140],
         "Tamil Nadu": [13.0827, 80.2707],
         "Telangana": [17.1231, 79.2085],
         "Tripura": [23.9408, 91.9882],
         "Uttar Pradesh": [26.8467, 80.9462],
         "Uttarakhand": [30.0668, 79.0193],
         "West Bengal": [22.9868, 87.8550],
         "Andaman and Nicobar Islands": [11.7401, 92.6586],
         "Chandigarh": [30.7333, 76.7794],
         "Delhi": [28.6139, 77.2090],
         "Jammu and Kashmir": [33.7782, 76.5762],
      }

      # Prepare data for OpenStreetMap visualization
      map_data = pd.DataFrame({
         "State": list(state_coords.keys()),
         "lat": [coord[0] for coord in state_coords.values()],  # Latitude
         "lon": [coord[1] for coord in state_coords.values()],  # Longitude
         "Registrations": [state_data[state]["registrations"] for state in state_coords],
         "Transactions": [state_data[state]["transactions"] for state in state_coords],
         "Redemptions": [state_data[state]["redemptions"] for state in state_coords],
      })

      fig = px.scatter_mapbox(
         map_data,
         lat="lat",  # Latitude column
         lon="lon",  # Longitude column
         hover_name="State",  # Display the state name in the tooltip
         hover_data={  # Customize hover data to include only the desired fields
            "Registrations": True,
            "Transactions": True,
            "Redemptions": True,
            "lat": False,  # Hide latitude
            "lon": False,  # Hide longitude
         },
         title="Overview",
         size="Registrations",
         size_max=40,
      )

      fig.update_layout(
         mapbox_style="open-street-map",
         height=600,
         margin={"r": 0, "t": 0, "l": 0, "b": 0},
         mapbox=dict(
            center=dict(lat=20.5937, lon=78.9629),
            zoom=4
         )
      )

      # Display map in Streamlit
      st.plotly_chart(fig, use_container_width=True)