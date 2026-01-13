import streamlit as st
import pandas as pd
import requests
from io import StringIO

# ============================================
# CONFIGURATION - UPDATE THESE URLS
# ============================================
CSV_URL = 'https://raw.githubusercontent.com/jonathanlau97/airaliprizepool/main/airali_sales.csv'
#DESKTOP_BG_URL = 'https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/desktop-bg.jpg'
#MOBILE_BG_URL = 'https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/mobile-bg.jpg'
# ============================================

# --- Page Configuration ---
st.set_page_config(
    page_title="Flight Crew Prize Pool",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Background CSS ---
def apply_background_css(desktop_bg_url, mobile_bg_url):
    # Check if URLs are configured
    use_custom_bg = not desktop_bg_url.startswith('https://raw.githubusercontent.com/YOUR_USERNAME')
    
    if use_custom_bg:
        bg_css = f"""
        <style>
            /* Background Images */
            .stApp {{
                background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url('{desktop_bg_url}');
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
                min-height: 100vh;
            }}
            
            /* Mobile Background */
            @media (max-width: 768px) {{
                .stApp {{
                    background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url('{mobile_bg_url}');
                    background-attachment: scroll;
                }}
            }}
        </style>
        """
    else:
        # Fallback gradient background
        bg_css = """
        <style>
            .stApp {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
        </style>
        """
    
    st.markdown(bg_css, unsafe_allow_html=True)

# Apply custom CSS for card styling
def apply_custom_css():
    st.markdown("""
    <style>
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Card Styles */
        .scorecard {
            padding: 1.5rem;
            border-radius: 1rem;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            margin-bottom: 1rem;
            color: white;
            transition: transform 0.3s;
        }
        
        .scorecard:hover {
            transform: scale(1.05);
        }
        
        .gold-card {
            background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        }
        
        .silver-card {
            background: linear-gradient(135deg, #d1d5db 0%, #9ca3af 100%);
        }
        
        .bronze-card {
            background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
        }
        
        .other-card {
            background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
            color: #1e40af;
            border: 2px solid #93c5fd;
        }
        
        .carrier-header {
            background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
            padding: 1.5rem;
            border-radius: 1rem;
            color: white;
            margin-bottom: 1.5rem;
        }
        
        .crew-name {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .crew-id {
            font-size: 0.875rem;
            opacity: 0.9;
            margin-bottom: 1rem;
        }
        
        .sales-value {
            font-size: 2rem;
            font-weight: bold;
            margin-top: 1rem;
        }
        
        .sales-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            opacity: 0.9;
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .scorecard {
                padding: 1rem;
            }
            .crew-name {
                font-size: 1.2rem;
            }
            .sales-value {
                font-size: 1.5rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

# --- Load CSV Data ---
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_csv_from_github(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)
        return df, None
    except Exception as e:
        return None, str(e)

# --- Process Data ---
def process_sales_data(df):
    # Aggregate sales by Crew and Airline
    aggregated = df.groupby(['Airline_Code', 'Crew_ID', 'Crew_Name']).agg({
        'crew_sold_quantity': 'sum'
    }).reset_index()
    
    # Sort by sales within each carrier
    aggregated = aggregated.sort_values(['Airline_Code', 'crew_sold_quantity'], ascending=[True, False])
    
    return aggregated

# --- Render Scorecard ---
def render_scorecard(rank, crew_name, crew_id, sales, card_type='other'):
    medals = {1: '🥇', 2: '🥈', 3: '🥉'}
    medal = medals.get(rank, '')
    
    card_classes = {
        'gold': 'gold-card',
        'silver': 'silver-card',
        'bronze': 'bronze-card',
        'other': 'other-card'
    }
    
    card_html = f"""
    <div class="scorecard {card_classes.get(card_type, 'other-card')}">
        <div style="font-size: 2.5rem; margin-bottom: 1rem;">{medal}</div>
        <div class="crew-name">{crew_name}</div>
        <div class="crew-id">ID: {crew_id}</div>
        <div class="sales-label">Total Sales</div>
        <div class="sales-value">{sales:,}</div>
        <div style="font-size: 0.75rem; margin-top: 0.5rem;">bottles sold</div>
    </div>
    """
    
    return card_html

# --- Main App ---
def main():
    # Apply styling
    apply_background_css(DESKTOP_BG_URL, MOBILE_BG_URL)
    apply_custom_css()
    
    # Header
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0; color: white;'>
        <h1 style='font-size: 3rem; font-weight: bold; margin-bottom: 0.5rem;'>
            🚀 Flight Crew Prize Pool
        </h1>
        <p style='font-size: 1.1rem; opacity: 0.9;'>Track top performers across all carriers</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    with st.spinner('Loading data from GitHub...'):
        df, error = load_csv_from_github(CSV_URL)
    
    if error:
        st.error(f"❌ Error loading CSV: {error}")
        st.info(f"CSV URL: {CSV_URL}")
        if st.button("🔄 Retry"):
            st.rerun()
        return
    
    if df is None or df.empty:
        st.warning("⚠️ No data available. Please check your CSV file.")
        return
    
    # Add refresh button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Process data
    processed_df = process_sales_data(df)
    
    # Get unique carriers
    carriers = processed_df['Airline_Code'].unique()
    
    # Display data for each carrier
    for carrier in carriers:
        carrier_data = processed_df[processed_df['Airline_Code'] == carrier].reset_index(drop=True)
        
        # Carrier Header
        st.markdown(f"""
        <div class="carrier-header">
            <h2 style='font-size: 2rem; font-weight: bold; margin: 0;'>✈️ {carrier}</h2>
            <p style='margin: 0; opacity: 0.9;'>Top Performers</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Top 3 Scorecards
        if len(carrier_data) >= 1:
            top_3 = carrier_data.head(3)
            card_types = ['gold', 'silver', 'bronze']
            
            cols = st.columns(min(3, len(top_3)))
            for idx, (_, row) in enumerate(top_3.iterrows()):
                with cols[idx]:
                    card_html = render_scorecard(
                        rank=idx + 1,
                        crew_name=row['Crew_Name'],
                        crew_id=row['Crew_ID'],
                        sales=int(row['crew_sold_quantity']),
                        card_type=card_types[idx]
                    )
                    st.markdown(card_html, unsafe_allow_html=True)
        
        # Next 7 Performers
        if len(carrier_data) > 3:
            st.markdown("<h3 style='color: white; margin-top: 2rem; margin-bottom: 1rem;'>📊 Other Top Performers</h3>", unsafe_allow_html=True)
            
            next_7 = carrier_data.iloc[3:10]
            
            # Create rows of 4 columns for better mobile display
            rows = [next_7.iloc[i:i+4] for i in range(0, len(next_7), 4)]
            
            for row_data in rows:
                cols = st.columns(min(4, len(row_data)))
                for idx, (_, crew) in enumerate(row_data.iterrows()):
                    with cols[idx]:
                        rank = crew.name + 1  # crew.name is the index
                        card_html = f"""
                        <div class="scorecard other-card">
                            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                                <span style="background: #4f46e5; color: white; border-radius: 50%; width: 2rem; height: 2rem; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.875rem;">
                                    {rank}
                                </span>
                                <div style="font-weight: bold; font-size: 1.1rem; color: #1e40af; flex: 1; overflow: hidden; text-overflow: ellipsis;">
                                    {crew['Crew_Name']}
                                </div>
                            </div>
                            <div style="font-size: 0.75rem; color: #4b5563; margin-bottom: 0.5rem;">ID: {crew['Crew_ID']}</div>
                            <div style="font-size: 1.5rem; font-weight: bold; color: #4f46e5;">{int(crew['crew_sold_quantity']):,}</div>
                            <div style="font-size: 0.75rem; color: #6b7280;">bottles sold</div>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Configuration note if using default background
    if DESKTOP_BG_URL.startswith('https://raw.githubusercontent.com/YOUR_USERNAME'):
        st.info("💡 **Tip:** Update `DESKTOP_BG_URL` and `MOBILE_BG_URL` in the code with your GitHub image URLs for custom backgrounds.")

if __name__ == "__main__":

    main()


