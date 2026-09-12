import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="SuperKart Sales Predictor",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 SuperKart Total Store Sales Prediction")

# Secure Token Input via Sidebar to keep the codebase secure
st.sidebar.header("🔑 Authentication Setup")
user_token = st.sidebar.text_input("Enter your GitHub Personal Access Token (ghp_...)", type="password")

# Backend endpoints running on port 8000
BACKEND_URL_SINGLE = "https://github.dev"
BACKEND_URL_BATCH = "https://github.dev_batch"

tab1, tab2 = st.tabs(["Single Item Prediction", "Batch Prediction"])

with tab1:
    if not user_token:
        st.warning("⚠️ Please provide your GitHub PAT token in the sidebar to authorize requests to your secure Codespace backend.")
        
    col1, col2 = st.columns(2)
    with col1:
        product_id_char = st.selectbox("Product Category Code (Product_Id_Char)", ["FD", "DR", "NC"])
        product_weight = st.number_input("Product Weight", value=12.5, step=0.1)
        product_sugar_content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
        product_allocated_area = st.number_input("Product Allocated Area", value=0.025, format="%.4f")
        product_type_category = st.selectbox("Product Type Category", ['Food', 'Drink', 'Non-Consumable', 'Others'])
        product_mrp = st.number_input("Product MRP ($)", value=117.0, step=1.0)

    with col2:
        store_age_years = st.number_input("Store Age (Years)", value=15, step=1)
        store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
        store_location_city_type = st.selectbox("City Type", ["Tier 1", "Tier 2", "Tier 3"])
        store_type = st.selectbox("Store Type", ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"])

    if st.button("Predict Sales") and user_token:
        payload = {
            "Product_Weight": float(product_weight),
            "Product_Sugar_Content": product_sugar_content,
            "Product_Allocated_Area": float(product_allocated_area),
            "Product_MRP": float(product_mrp),
            "Store_Size": store_size,
            "Store_Location_City_Type": store_location_city_type,
            "Store_Type": store_type,
            "Product_Id_Char": product_id_char,
            "Store_Age_Years": int(store_age_years),
            "Product_Type_Category": product_type_category
        }

        headers = {
            "X-Github-Token": user_token,
            "Authorization": f"Bearer {user_token}",
            "Accept": "application/json"
        }

        try:
            response = requests.post(BACKEND_URL_SINGLE, json=payload, headers=headers)
            if response.status_code == 200:
                result = response.json()
                st.success(f"Predicted Sales: ${result.get('Predicted_Store_Sales', 0):,.2f}")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Could not connect to backend server: {e}")

with tab2:
    st.header("Batch Sales Prediction")
    if not user_token:
        st.warning("⚠️ Please provide your GitHub PAT token in the sidebar to process batch requests.")
        
    uploaded_file = st.file_uploader("Upload CSV file for predictions", type=["csv"])

    if uploaded_file is not None and user_token:
        df_batch = pd.read_csv(uploaded_file)
        st.write("Uploaded Data Preview:", df_batch.head())

        if st.button("Predict Batch"):
            headers = {
                "X-Github-Token": user_token,
                "Authorization": f"Bearer {user_token}",
                "Accept": "application/json"
            }
            try:
                files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'text/csv')}
                response = requests.post(BACKEND_URL_BATCH, files=files, headers=headers)

                if response.status_code == 200:
                    predictions_dict = response.json()
                    predictions_df = pd.DataFrame(predictions_dict.items(), columns=['Product_Id', 'Predicted_Sales'])
                    st.write("Prediction Results:", predictions_df)
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")
