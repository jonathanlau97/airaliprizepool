import streamlit as st
import pandas as pd
import requests
from io import StringIO

# ============================================
# CONFIGURATION - UPDATE THESE URLS
# ============================================
CSV_URL = 'https://raw.githubusercontent.com/jonathanlau97/airaliprizepool/main/airali_sales.csv'
DESKTOP_BG_URL = 'https://raw.githubusercontent.com/jonathanlau97/airaliprizepool/main/AIRALI_DESKTOP.jpg'
MOBILE_BG_URL = 'https://raw.githubusercontent.com/jonathanlau97/airaliprizepool/main/AIRALI_MOBILE.jpg'
# ============================================

# --- Page Configuration ---
st.set_page_config(
    page_title="Flight Crew Prize Pool",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Background CSS ---
def apply_background_css(desktop_bg_url, mobile_bg_url):
    use_custom_bg = not desktop_bg_url.startswith('https://raw.githubusercontent.com/YOUR_USERNAME')
    
    if use_custom_bg:
        bg_css = f"""
        <style>
            .stApp {{
                background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('{desktop_bg_url}');
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
                min-height: 100vh;
            }}
            
            @media (max-width: 768px) {{
                .stApp {{
                    background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('{mobile_bg_url}');
                    background-attachment: scroll;
                }}
            }}
        </style>
        """
    else:
        bg_css = """
        <style>
            .stApp {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
        </style>
        """
    
    st.markdown(bg_css, unsafe_allow_html=True)

# Apply custom CSS for glassmorphism
def apply_custom_css():
    st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Glassmorphism cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 1.25rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
            color: white;
            transition: all 0.3s ease;
        }
        
        .glass-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.3);
        }
        
        .carrier-section {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            padding: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .rank-badge {
            background: rgba(255, 255, 255, 0.25);
            border-radius: 50%;
            width: 32px;
            height: 32px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 0.875rem;
        }
        
        .crew-name {
            font-size: 1.1rem;
            font-weight: 600;
            margin: 0.5rem 0 0.25rem 0;
        }
        
        .crew-id {
            font-size: 0.8rem;
            opacity: 0.8;
        }
        
        .sales-value {
            font-size: 1.75rem;
            font-weight: 700;
            margin-top: 0.75rem;
        }
        
        .sales-label {
            font-size: 0.7rem;
            text-transform: uppercase;
            opacity: 0.7;
            letter-spacing: 0.05em;
        }
        
        h1, h2, h3 {
            color: white !important;
        }
        
        @media (max-width: 768px) {
            .glass-card {
                padding: 1rem;
            }
            .crew-name {
                font-size: 1rem;
            }
            .sales-value {
                font-size: 1.5rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

# --- Load CSV Data ---
@st.cache_data(ttl=300)
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
    aggregated = df.groupby(['Airline_Code', 'Crew_ID', 'Crew_Name']).agg({
        'crew_sold_quantity': 'sum'
    }).reset_index()
    
    aggregated = aggregated.sort_values(['Airline_Code', 'crew_sold_quantity'], ascending=[True, False])
    
    return aggregated

# --- Render Top 3 Scorecard ---
def render_top_scorecard(rank, crew_name, crew_id, sales):
    medals = {1: '🥇', 2: '🥈', 3: '🥉'}
    medal = medals.get(rank, '')
    
    card_html = f"""
    <div class="glass-card">
        <div style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{medal}</div>
            <div class="crew-name">{crew_name}</div>
            <div class="crew-id">{crew_id}</div>
            <div class="sales-label" style="margin-top: 0.75rem;">Total Sales</div>
            <div class="sales-value">{sales:,}</div>
        </div>
    </div>
    """
    
    return card_html

# --- Render Other Scorecard ---
def render_other_scorecard(rank, crew_name, crew_id, sales):
    card_html = f"""
    <div class="glass-card">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
            <span class="rank-badge">{rank}</span>
            <div style="flex: 1; min-width: 0;">
                <div style="font-weight: 600; font-size: 0.95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{crew_name}</div>
                <div style="font-size: 0.75rem; opacity: 0.75;">{crew_id}</div>
            </div>
        </div>
        <div style="text-align: right; margin-top: 0.5rem;">
            <div style="font-size: 1.25rem; font-weight: 700;">{sales:,}</div>
            <div style="font-size: 0.7rem; opacity: 0.7;">bottles</div>
        </div>
    </div>
    """
    
    return card_html

# --- Main App ---
def main():
    apply_background_css(DESKTOP_BG_URL, MOBILE_BG_URL)
    apply_custom_css()
    
    # Header
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0 1rem 0;'>
        <h1 style='font-size: 2.5rem; font-weight: 700; margin-bottom: 0.25rem;'>
            Flight Crew Prize Pool
        </h1>
        <p style='font-size: 1rem; opacity: 0.85; color: white;'>Top Performers</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df, error = load_csv_from_github(CSV_URL)
    
    if error:
        st.error(f"Error loading data: {error}")
        return
    
    if df is None or df.empty:
        st.warning("No data available")
        return
    
    # Process data
    processed_df = process_sales_data(df)
    carriers = processed_df['Airline_Code'].unique()
    
    # Display each carrier
    for carrier in carriers:
        carrier_data = processed_df[processed_df['Airline_Code'] == carrier].reset_index(drop=True)
        
        st.markdown(f"""
        <div class="carrier-section">
            <h2 style='font-size: 1.5rem; font-weight: 600; margin: 0 0 1.25rem 0;'>✈️ {carrier}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Top 3 in one row
        if len(carrier_data) >= 1:
            top_3 = carrier_data.head(3)
            cols = st.columns(3)
            
            for idx, (_, row) in enumerate(top_3.iterrows()):
                with cols[idx]:
                    card_html = render_top_scorecard(
                        rank=idx + 1,
                        crew_name=row['Crew_Name'],
                        crew_id=row['Crew_ID'],
                        sales=int(row['crew_sold_quantity'])
                    )
                    st.markdown(card_html, unsafe_allow_html=True)
        
        # Next 7 in grid
        if len(carrier_data) > 3:
            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
            
            next_7 = carrier_data.iloc[3:10]
            
            # 4 columns for desktop, responsive for mobile
            for i in range(0, len(next_7), 4):
                row_data = next_7.iloc[i:i+4]
                cols = st.columns(4)
                
                for idx, (_, crew) in enumerate(row_data.iterrows()):
                    with cols[idx]:
                        rank = crew.name + 1
                        card_html = render_other_scorecard(
                            rank=rank,
                            crew_name=crew['Crew_Name'],
                            crew_id=crew['Crew_ID'],
                            sales=int(crew['crew_sold_quantity'])
                        )
                        st.markdown(card_html, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
