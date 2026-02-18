import streamlit as st
import pandas as pd

# ────────────────────────────────────────────────
#  CONFIGURATION
# ────────────────────────────────────────────────

st.set_page_config(
    page_title="Slot Car Tire Search",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title & description
st.title("🛞 Slot Car Tire Search Database")
st.markdown("""
Search for compatible tires by **brand**, **model**, **compound** (Silicone / Urethane / Rubber) and more.
Data includes Quick Slicks, Super Tires, Bobkat, Paul Gage, Indy Grip, Carrera OEM, NSR, Policar, etc.
""")

# ────────────────────────────────────────────────
# LOAD DATA
# ────────────────────────────────────────────────

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Tire_master.csv", dtype=str)
        # Clean up columns if needed
        df.columns = df.columns.str.strip()
        # Fill NaN with empty string for nicer display
        df = df.fillna("")
        return df
    except FileNotFoundError:
        st.error("File 'Tire_master.csv' not found in the current directory.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        st.stop()

df = load_data()

# ────────────────────────────────────────────────
# SIDEBAR FILTERS
# ────────────────────────────────────────────────

with st.sidebar:
    st.header("Filters")

    # Compound multi-select
    all_compounds = sorted(df["Compound"].dropna().unique())
    selected_compounds = st.multiselect(
        "Compound",
        options=["All"] + list(all_compounds),
        default=["All"]
    )

    # Brand select
    all_brands = sorted(df["Brand"].dropna().unique())
    selected_brand = st.selectbox(
        "Brand",
        options=["All"] + list(all_brands),
        index=0
    )

    # Model text search (partial match)
    model_search = st.text_input("Model (partial match, e.g. 'M4' or '917')").strip()

    # Position
    all_positions = sorted(df["Position"].dropna().unique())
    selected_position = st.selectbox(
        "Position",
        options=["All"] + list(all_positions)
    )

    # Optional: free text search in Notes or Tire_Part
    free_search = st.text_input("Search in Notes / Part #").strip()

    st.markdown("---")
    st.caption(f"Total tires in database: {len(df)}")

# ────────────────────────────────────────────────
# APPLY FILTERS
# ────────────────────────────────────────────────

filtered_df = df.copy()

if "All" not in selected_compounds:
    filtered_df = filtered_df[filtered_df["Compound"].isin(selected_compounds)]

if selected_brand != "All":
    filtered_df = filtered_df[filtered_df["Brand"] == selected_brand]

if model_search:
    filtered_df = filtered_df[
        filtered_df["Model"].str.contains(model_search, case=False, na=False)
    ]

if selected_position != "All":
    filtered_df = filtered_df[filtered_df["Position"].str.contains(selected_position, case=False, na=False)]

if free_search:
    mask = (
        filtered_df["Notes"].str.contains(free_search, case=False, na=False) |
        filtered_df["Tire_Part"].str.contains(free_search, case=False, na=False)
    )
    filtered_df = filtered_df[mask]

# ────────────────────────────────────────────────
# DISPLAY RESULTS
# ────────────────────────────────────────────────

st.subheader(f"Found {len(filtered_df)} matching tire options")

if filtered_df.empty:
    st.warning("No tires match the current filters. Try broadening your search.")
else:
    # Choose columns to show (you can reorder/add/remove)
    display_cols = [
        "Brand", "Model", "Compound", "Tire_Part",
        "OD_mm", "Width_mm", "Position", "Notes", "Source"
    ]
    # Only show columns that actually exist
    display_cols = [col for col in display_cols if col in filtered_df.columns]

    st.dataframe(
        filtered_df[display_cols].reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )

# Optional: download filtered results
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download filtered results as CSV",
    data=csv,
    file_name="filtered_slot_tires.csv",
    mime="text/csv"
)

# Footer
st.markdown("---")
st.caption("Built for slot car racers • Data compiled from Quick Slicks, Super Tires, Bobkat, Paul Gage, Carrera OEM, Professor Motor, etc. • Last updated February 2026")
