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
    page_title="Airali : Crew Sales Performance",
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
                background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url('{desktop_bg_url}');
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
                min-height: 100vh;
            }}
            
            @media (max-width: 768px) {{
                .stApp {{
                    background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url('{mobile_bg_url}');
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
        
        /* Remove default streamlit padding */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Glassmorphism cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.18);
            padding: 1.5rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25);
            color: white;
            transition: all 0.3s ease;
            height: 100%;
        }
        
        .glass-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 48px 0 rgba(0, 0, 0, 0.35);
            background: rgba(255, 255, 255, 0.18);
        }
        
        /* Podium ladder cards */
        .podium-card {
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            padding-bottom: 1.5rem;
        }
        
        .rank-1 { min-height: 280px; }
        .rank-2 { min-height: 240px; }
        .rank-3 { min-height: 200px; }
        
        .other-card {
            min-height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        
        .rank-badge {
            background: rgba(255, 255, 255, 0.25);
            border-radius: 50%;
            width: 36px;
            height: 36px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 0.95rem;
        }
        
        h1 {
            color: white !important;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }
        
        h2 {
            color: white !important;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .glass-card {
                padding: 1.25rem;
            }
            .rank-1 { min-height: 240px; }
            .rank-2 { min-height: 200px; }
            .rank-3 { min-height: 170px; }
            .other-card {
                min-height: 110px;
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

# --- Main App ---
def main():
    apply_background_css(DESKTOP_BG_URL, MOBILE_BG_URL)
    apply_custom_css()
    
    # Header
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem 0 2rem 0;'>
        <h1 style='font-size: 2.75rem; font-weight: 700; margin: 0;'>
            Airali : Crew Sales Performance
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df, error = load_csv_from_github(CSV_URL)
    
    if error:
        st.error(f"Error: {error}")
        return
    
    if df is None or df.empty:
        st.warning("No data available")
        return
    
    # Process data
    processed_df = process_sales_data(df)
    carriers = sorted(processed_df['Airline_Code'].unique())
    
    # Display carriers side by side
    carrier_cols = st.columns(len(carriers))
    
    for carrier_idx, carrier in enumerate(carriers):
        with carrier_cols[carrier_idx]:
            carrier_data = processed_df[processed_df['Airline_Code'] == carrier].reset_index(drop=True)
            
            # Carrier header
            st.markdown(f"""
            <h2 style='font-size: 1.75rem; font-weight: 600; margin-bottom: 1.5rem; text-align: center;'>
                ✈️ {carrier}
            </h2>
            """, unsafe_allow_html=True)
            
            # Top 3 in podium ladder layout (2nd, 1st, 3rd order)
            top_3 = carrier_data.head(3)
            
            if len(top_3) >= 3:
                # Create podium order: 2nd, 1st, 3rd
                podium_order = [1, 0, 2]  # indices for 2nd, 1st, 3rd place
                medals = ['🥇', '🥈', '🥉']
                rank_classes = ['rank-1', 'rank-2', 'rank-3']
                
                # Display in 3 columns for ladder effect
                podium_cols = st.columns(3)
                
                for col_idx, rank_idx in enumerate(podium_order):
                    if rank_idx < len(top_3):
                        row = top_3.iloc[rank_idx]
                        with podium_cols[col_idx]:
                            st.markdown(f"""
                            <div class="glass-card podium-card {rank_classes[rank_idx]}">
                                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{medals[rank_idx]}</div>
                                <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 0.25rem;">{row['Crew_Name']}</div>
                                <div style="font-size: 0.75rem; opacity: 0.75; margin-bottom: 0.75rem;">{row['Crew_ID']}</div>
                                <div style="font-size: 0.65rem; text-transform: uppercase; opacity: 0.65; letter-spacing: 0.05em;">Sales</div>
                                <div style="font-size: 1.75rem; font-weight: 700;">{int(row['crew_sold_quantity']):,}</div>
                            </div>
                            """, unsafe_allow_html=True)
                
                st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
            
            elif len(top_3) > 0:
                # Fallback for less than 3 entries
                medals = ['🥇', '🥈', '🥉']
                rank_classes = ['rank-1', 'rank-2', 'rank-3']
                
                for idx, (_, row) in enumerate(top_3.iterrows()):
                    st.markdown(f"""
                    <div class="glass-card podium-card {rank_classes[idx]}">
                        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{medals[idx]}</div>
                        <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 0.25rem;">{row['Crew_Name']}</div>
                        <div style="font-size: 0.75rem; opacity: 0.75; margin-bottom: 0.75rem;">{row['Crew_ID']}</div>
                        <div style="font-size: 0.65rem; text-transform: uppercase; opacity: 0.65; letter-spacing: 0.05em;">Sales</div>
                        <div style="font-size: 1.75rem; font-weight: 700;">{int(row['crew_sold_quantity']):,}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            
            # Next 7
            next_7 = carrier_data.iloc[3:10]
            
            if len(next_7) > 0:
                st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
                
                for _, crew in next_7.iterrows():
                    rank = crew.name + 1
                    st.markdown(f"""
                    <div class="glass-card other-card">
                        <div style="display: flex; align-items: center; gap: 0.75rem;">
                            <span class="rank-badge">{rank}</span>
                            <div style="flex: 1; min-width: 0;">
                                <div style="font-weight: 600; font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{crew['Crew_Name']}</div>
                                <div style="font-size: 0.7rem; opacity: 0.7;">{crew['Crew_ID']}</div>
                            </div>
                        </div>
                        <div style="text-align: right; margin-top: 0.5rem;">
                            <div style="font-size: 1.25rem; font-weight: 700;">{int(crew['crew_sold_quantity']):,}</div>
                            <div style="font-size: 0.65rem; opacity: 0.65;">bottles</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
