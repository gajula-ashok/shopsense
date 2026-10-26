import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys

# Add parent and dashboard directories to sys.path
_PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_DASHBOARD_DIR = os.path.abspath(os.path.dirname(__file__))
for _p in (_PARENT_DIR, _DASHBOARD_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import importlib

try:
    import dashboard.api_client as _api_module
    importlib.reload(_api_module)
    ApiClient = _api_module.ApiClient
except Exception:
    import api_client as _api_module
    importlib.reload(_api_module)
    ApiClient = _api_module.ApiClient

try:
    import dashboard.theme as _theme_module
    importlib.reload(_theme_module)
except Exception:
    import theme as _theme_module
    importlib.reload(_theme_module)

# Page configuration
st.set_page_config(
    page_title="ShopSense – Multi-Vendor Analytics & Marketplace",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State Defaults
if "theme" not in st.session_state:
    st.session_state["theme"] = _theme_module.DEFAULT_THEME

# Initialize API Client
BACKEND_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
api = ApiClient(base_url=BACKEND_URL)

# Inject Dynamic E-Commerce Styling
st.markdown(_theme_module.generate_ecommerce_css(st.session_state["theme"]), unsafe_allow_html=True)

# Session State Initialization
if "token" not in st.session_state:
    st.session_state["token"] = None
if "user" not in st.session_state:
    st.session_state["user"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None
if "vendor_id" not in st.session_state:
    st.session_state["vendor_id"] = None

def logout():
    st.session_state["token"] = None
    st.session_state["user"] = None
    st.session_state["role"] = None
    st.session_state["vendor_id"] = None
    st.rerun()

# ==========================================
# 1. AUTHENTICATION (LOGIN / REGISTER)
# ==========================================
def render_auth_page():
    theme_name = st.session_state.get("theme", _theme_module.DEFAULT_THEME)
    cfg = _theme_module.get_theme_config(theme_name)

    # Top Brand Bar for Auth Page
    st.markdown(f"""
    <div class="ss-navbar" style="justify-content: center; text-align: center; padding: 18px 24px;">
        <div style="text-align: center;">
            <div class="ss-navbar-logo" style="justify-content: center;">
                🛍️ ShopSense <span class="ss-navbar-pill" style="font-size:0.75rem; margin-left:8px;">{cfg["brand_badge"]}</span>
            </div>
            <div class="ss-navbar-tagline" style="margin-top: 4px;">
                India's Multi-Vendor Marketplace • Smart Shopping & Instant Delivery
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Theme Switcher on Auth Screen
    col_t1, col_t2, col_t3 = st.columns([1, 2, 1])
    with col_t2:
        col_lbl, col_sel = st.columns([1, 2])
        with col_lbl:
            st.markdown("<div style='font-size:0.85rem; font-weight:700; color:#555; padding-top:6px; text-align:right;'>🎨 Select UI Style:</div>", unsafe_allow_html=True)
        with col_sel:
            chosen_auth_theme = st.selectbox(
                "Theme",
                list(_theme_module.THEME_CONFIGS.keys()),
                index=list(_theme_module.THEME_CONFIGS.keys()).index(st.session_state["theme"]),
                key="auth_theme_select",
                label_visibility="collapsed"
            )
            if chosen_auth_theme != st.session_state["theme"]:
                st.session_state["theme"] = chosen_auth_theme
                st.rerun()

    _, col1, _ = st.columns([1, 2, 1])

    with col1:
        # Quick Demo Credentials Hint
        with st.expander("🔑 Quick Demo Credentials (Click to preview)", expanded=False):
            st.markdown("""
            - 👑 **Admin:** `admin@shopsense.com` | Password: `Admin@123`
            - 🏪 **Vendor:** `techworld@example.com` | Password: `Vendor@123`
            - 🛍️ **Customer:** `customer@shopsense.com` | Password: `Customer@123`
            """)

        tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Create Account"])

        with tab_login:
            login_role = st.selectbox(
                "I want to sign in as:",
                ["ADMIN", "VENDOR", "CUSTOMER"],
                format_func=lambda r: {
                "ADMIN": "🛡️ Admin",
                "VENDOR": "🏪 Vendor",
                "CUSTOMER": "🛍️ Customer"
                }[r],
                key="login_role"
            )
            
            if login_role == "ADMIN":
            # Redirect to Admin Dashboard
                pass
            elif login_role == "VENDOR":
            # Redirect to Vendor Dashboard
                pass
            elif login_role == "CUSTOMER":
            # Redirect to Customer Dashboard
                pass
            login_email = st.text_input("Email Address", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")

            if st.button("Sign In", type="primary", use_container_width=True):
                if not login_email or not login_password:
                    st.error("Please enter both email and password.")
                else:
                    try:
                        with st.spinner("Authenticating..."):
                            resp = api.login(login_email.strip(), login_password)
                            st.session_state["token"] = resp["access_token"]
                            st.session_state["user"] = resp["email"]
                            st.session_state["user_name"] = resp["full_name"]
                            st.session_state["role"] = resp["role"]
                            st.session_state["vendor_id"] = resp.get("vendor_id")
                            st.success(f"Welcome back, {resp['full_name']}!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Login failed: {str(e)}")

            # Forgot Password Section
            st.markdown("---")
            with st.expander("🔑 Forgot Password?", expanded=False):
                st.markdown("<p style='font-size:0.9rem; color:#666;'>Enter your registered email and set a new password.</p>", unsafe_allow_html=True)
                fp_email = st.text_input("Registered Email", key="fp_email", placeholder="Enter your registered email")
                fp_new_pw = st.text_input("New Password (min 6 chars)", type="password", key="fp_new_pw")
                fp_confirm_pw = st.text_input("Confirm New Password", type="password", key="fp_confirm_pw")

                if st.button("Reset Password", type="primary", use_container_width=True, key="fp_submit"):
                    if not fp_email or not fp_new_pw or not fp_confirm_pw:
                        st.error("All fields are required.")
                    elif len(fp_new_pw) < 6:
                        st.error("Password must be at least 6 characters.")
                    elif fp_new_pw != fp_confirm_pw:
                        st.error("Passwords do not match.")
                    else:
                        try:
                            with st.spinner("Resetting password..."):
                                result = api.reset_password(fp_email.strip(), fp_new_pw)
                                st.success(result.get("message", "Password reset successfully! You can now sign in with your new password."))
                        except Exception as e:
                            st.error(f"Password reset failed: {str(e)}")

        with tab_register:
            st.subheader("Register New Account")

            # Role selection comes first
            reg_role = st.selectbox(
                "I want to register as:",
                ["CUSTOMER", "VENDOR"],
                format_func=lambda r: {"CUSTOMER": "🛍️ Customer", "VENDOR": "🏪 Vendor"}[r],
                key="reg_role"
            )

            reg_name = st.text_input("Full Name", key="reg_name")
            reg_email = st.text_input("Email", key="reg_email")
            reg_pw = st.text_input("Password (min 6 chars)", type="password", key="reg_pw")
            reg_pw_confirm = st.text_input("Confirm Password", type="password", key="reg_pw_confirm")

            reg_phone = None
            reg_bname = None
            reg_cat = None

            if reg_role == "VENDOR":
                st.markdown("##### 🏪 Vendor Details")
                reg_bname = st.text_input("Business / Store Name", key="reg_bname", placeholder="e.g. Apex Electronics")
                reg_phone = st.text_input("Phone Number", key="reg_phone", placeholder="e.g. 9876543210")
                reg_cat = st.selectbox(
                    "Store Category",
                    ["Electronics", "Fashion", "Books", "Home & Kitchen", "Beauty & Personal Care", "General"],
                    key="reg_cat"
                )

            if st.button("Create Account", type="primary", use_container_width=True):
                if not reg_name or not reg_email or not reg_pw or not reg_pw_confirm:
                    st.error("All fields are required.")
                elif len(reg_pw) < 6:
                    st.error("Password must be at least 6 characters.")
                elif reg_pw != reg_pw_confirm:
                    st.error("Passwords do not match.")
                elif reg_role == "VENDOR" and not reg_phone:
                    st.error("Phone number is required for Vendor onboarding.")
                else:
                    try:
                        with st.spinner("Creating account..."):
                            resp = api.register(
                                reg_name.strip(),
                                reg_email.strip(),
                                reg_pw,
                                reg_role,
                                phone=reg_phone.strip() if reg_phone else None,
                                business_name=reg_bname.strip() if reg_bname else None,
                                category=reg_cat.strip() if reg_cat else None
                            )
                            st.success(f"Account for '{reg_name}' created successfully! You can now sign in.")
                    except Exception as e:
                        st.error(f"Registration error: {str(e)}")

        st.markdown("""
        <div class="ss-auth-trust-footer">
            🔒 By continuing, you agree to ShopSense Conditions of Use and Privacy Notice.<br/>
            100% Secure Checkout • 256-Bit SSL Protection
        </div>
        """, unsafe_allow_html=True)

    st.markdown(_theme_module.render_trust_footer(), unsafe_allow_html=True)


# ==========================================
# 2. DASHBOARD VIEW (ADMIN / VENDOR)
# ==========================================
def render_dashboard_page():
    role = st.session_state["role"]
    token = st.session_state["token"]
    user_name = st.session_state.get("user_name", "User")
    current_theme = st.session_state.get("theme", _theme_module.DEFAULT_THEME)

    st.markdown(_theme_module.render_top_navbar(user_name,role , current_theme), unsafe_allow_html=True)
    st.title(f"📊 {'Marketplace Executive Dashboard' if role == 'ADMIN' else 'Vendor Performance Portal'}")
    st.markdown(f"Logged in as **{user_name}** • Seller Central & Analytics Portal")

    # Fetch Summary KPIs
    try:
        summary = api.get_summary(token)
    except Exception as e:
        st.error(f"Could not load analytics summary: {e}")
        return

    # Top KPI Metrics
    if role == "ADMIN":
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1:
            st.metric("Total Revenue", f"${summary['total_revenue']:,.2f}")
        with c2:
            st.metric("Total Orders", f"{summary['total_transactions']:,}")
        with c3:
            st.metric("Units Sold", f"{summary['total_quantity_sold']:,}")
        with c4:
            st.metric("Avg Order Value", f"${summary['average_transaction_value']:,.2f}")
        with c5:
            st.metric("Total Vendors", f"{summary['total_vendors']}")
        with c6:
            st.metric("Total Products", f"{summary['total_products']}")
    else:
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric("Total Revenue", f"${summary['total_revenue']:,.2f}")
        with c2:
            st.metric("Total Orders", f"{summary['total_transactions']:,}")
        with c3:
            st.metric("Units Sold", f"{summary['total_quantity_sold']:,}")
        with c4:
            st.metric("Avg Order Value", f"${summary['average_transaction_value']:,.2f}")
        with c5:
            st.metric("Total Products", f"{summary['total_products']}")

    st.markdown("---")

    # Visualizations
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("📈 Revenue Over Time")
        trend_data = api.get_revenue_trend(token)
        if trend_data:
            df_trend = pd.DataFrame(trend_data)
            fig_trend = px.area(
                df_trend,
                x="date",
                y="revenue",
                title="Daily Revenue Trend",
                labels={"date": "Transaction Date", "revenue": "Revenue ($)"},
                markers=True
            )
            fig_trend.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No transaction history recorded yet.")

    with col_right:
        st.subheader("🥧 Category Distribution")
        cat_data = api.get_category_performance(token)
        if cat_data:
            df_cat = pd.DataFrame(cat_data)
            fig_cat = px.pie(
                df_cat,
                names="category",
                values="revenue",
                title="Revenue by Product Category",
                hole=0.4
            )
            fig_cat.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("No category data available.")

    # Second row of charts
    c_bottom1, c_bottom2 = st.columns(2)

    with c_bottom1:
        if role == "ADMIN":
            st.subheader("🏆 Vendor Performance Breakdown")
            v_perf = api.get_vendor_performance(token)
            if v_perf:
                df_v = pd.DataFrame(v_perf)
                fig_v = px.bar(
                    df_v,
                    x="business_name",
                    y="total_revenue",
                    color="category",
                    title="Revenue by Vendor",
                    labels={"business_name": "Vendor", "total_revenue": "Revenue ($)"}
                )
                fig_v.update_layout(template="plotly_white")
                st.plotly_chart(fig_v, use_container_width=True)
            else:
                st.info("No vendor metrics recorded.")
        else:
            st.subheader("📦 Product Sales Performance")
            p_perf = api.get_product_performance(token)
            if p_perf:
                df_p = pd.DataFrame(p_perf)
                fig_p = px.bar(
                    df_p,
                    x="product_name",
                    y="total_revenue",
                    color="quantity_sold",
                    title="Revenue by Product",
                    labels={"product_name": "Product", "total_revenue": "Revenue ($)"}
                )
                fig_p.update_layout(template="plotly_white")
                st.plotly_chart(fig_p, use_container_width=True)
            else:
                st.info("No product metrics available.")

    with c_bottom2:
        st.subheader("📊 Top Selling Products")
        p_perf = api.get_product_performance(token)
        if p_perf:
            df_top = pd.DataFrame(p_perf).sort_values(by="quantity_sold", ascending=False).head(5)
            fig_top = px.bar(
                df_top,
                x="quantity_sold",
                y="product_name",
                orientation="h",
                title="Top 5 Products by Units Sold",
                labels={"quantity_sold": "Units Sold", "product_name": "Product"}
            )
            fig_top.update_layout(template="plotly_white", yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_top, use_container_width=True)
        else:
            st.info("No sales data available.")

    st.markdown(_theme_module.render_trust_footer(), unsafe_allow_html=True)

# ==========================================
# 3. VENDOR MANAGEMENT PAGE (ADMIN ONLY)
# ==========================================
def render_vendors_page():
    token = st.session_state["token"]
    role = st.session_state["role"]
    user_name = st.session_state.get("user_name", "User")
    current_theme = st.session_state.get("theme", _theme_module.DEFAULT_THEME)

    st.markdown(_theme_module.render_top_navbar(user_name, role, current_theme), unsafe_allow_html=True)
    st.title("🏢 Vendor Management & Onboarding")

    if role != "ADMIN":
        st.warning("Only Marketplace Administrators can manage vendor accounts.")
        return

    # Add Vendor Expandable Form
    with st.expander("➕ Onboard New Vendor", expanded=False):
        with st.form("add_vendor_form"):
            c1, c2 = st.columns(2)
            with c1:
                b_name = st.text_input("Business Name *")
                o_name = st.text_input("Owner Name *")
                v_email = st.text_input("Vendor Email *")
            with c2:
                v_phone = st.text_input("Phone Number * (10-15 digits)")
                v_cat = st.selectbox("Category *", [
                    "Electronics", "Fashion", "Books", "Home & Kitchen",
                    "Beauty & Personal Care", "Sports & Fitness", "Automotive", "Other"
                ])
                v_comm = st.number_input("Commission Rate (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5)

            submitted = st.form_submit_button("Register & Activate Vendor", type="primary")
            if submitted:
                if not b_name or not o_name or not v_email or not v_phone:
                    st.error("Please complete all required fields.")
                else:
                    try:
                        api.create_vendor(token, {
                            "business_name": b_name,
                            "owner_name": o_name,
                            "email": v_email,
                            "phone": v_phone,
                            "category": v_cat,
                            "commission_rate": v_comm,
                            "status": "ACTIVE"
                        })
                        st.success(f"Vendor '{b_name}' successfully onboarded!")
                        st.rerun()
                    except Exception as e:
                        err_msg = str(e)
                        if "409" in err_msg or "already registered" in err_msg:
                            st.error(f"⚠️ A vendor with that email is already registered. If they self-registered, you can find them in the list below and change their status to ACTIVE.")
                        else:
                            st.error(f"Vendor onboarding error: {err_msg}")

    # Filter and Search
    f1, f2, f3 = st.columns([2, 1, 1])
    with f1:
        search_kw = st.text_input("🔍 Search vendors...", "")
    with f2:
        cat_filter = st.selectbox("Category Filter", ["All", "Electronics", "Fashion", "Books", "Home & Kitchen", "Beauty & Personal Care"])
    with f3:
        status_filter = st.selectbox("Status Filter", ["All", "ACTIVE", "PENDING", "SUSPENDED"])

    try:
        vendors = api.get_vendors(token, search=search_kw, category=cat_filter, status=status_filter)
        if vendors:
            df_v = pd.DataFrame(vendors)
            st.dataframe(
                df_v[["vendor_id", "business_name", "owner_name", "email", "phone", "category", "commission_rate", "status", "created_at"]],
                use_container_width=True,
                hide_index=True
            )

            # Quick Actions Section
            st.subheader("⚙️ Vendor Actions")
            sel_vendor_id = st.selectbox("Select Vendor to manage", [v["vendor_id"] for v in vendors], format_func=lambda x: f"Vendor #{x} - {[v['business_name'] for v in vendors if v['vendor_id']==x][0]}")
            curr_vendor = next(v for v in vendors if v["vendor_id"] == sel_vendor_id)

            col_act1, col_act2, col_act3 = st.columns(3)
            with col_act1:
                new_status = st.selectbox("Change Status", ["ACTIVE", "PENDING", "SUSPENDED"], index=["ACTIVE", "PENDING", "SUSPENDED"].index(curr_vendor["status"]))
                if st.button("Update Status"):
                    try:
                        api.update_vendor(token, sel_vendor_id, {"status": new_status})
                        st.success(f"Status for Vendor #{sel_vendor_id} changed to {new_status}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Update failed: {e}")
            with col_act2:
                new_rate = st.number_input("Update Commission (%)", value=float(curr_vendor["commission_rate"]), min_value=0.0, max_value=100.0)
                if st.button("Save Commission"):
                    try:
                        api.update_vendor(token, sel_vendor_id, {"commission_rate": new_rate})
                        st.success("Commission updated.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to update commission: {e}")
            with col_act3:
                st.write("Danger Zone:")
                if st.button("🗑️ Delete Vendor", type="secondary"):
                    try:
                        api.delete_vendor(token, sel_vendor_id)
                        st.success(f"Vendor #{sel_vendor_id} removed.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Deletion failed: {e}")
        else:
            st.info("No vendors found matching criteria.")
    except Exception as e:
        st.error(f"Error loading vendors: {e}")

    st.markdown(_theme_module.render_trust_footer(), unsafe_allow_html=True)

# ==========================================
# 4. PRODUCT CATALOG PAGE
# ==========================================
def render_products_page():
    token = st.session_state["token"]
    role = st.session_state["role"]
    user_name = st.session_state.get("user_name", "User")
    current_theme = st.session_state.get("theme", _theme_module.DEFAULT_THEME)

    st.markdown(_theme_module.render_top_navbar(user_name, role, current_theme), unsafe_allow_html=True)
    st.title("📦 Product Catalog Management")

    # Add Product Form
    with st.expander("➕ Add New Product", expanded=False):
        with st.form("add_product_form"):
            c1, c2 = st.columns(2)
            with c1:
                p_name = st.text_input("Product Name *")
                p_cat = st.selectbox("Category *", [
                    "Electronics", "Fashion", "Books", "Home & Kitchen",
                    "Beauty & Personal Care", "Sports & Fitness", "Toys & Games", "Other"
                ])
                p_price = st.number_input("Unit Price ($) *", min_value=0.01, value=49.99, step=1.0)
            with c2:
                p_stock = st.number_input("Initial Inventory Stock *", min_value=0, value=20, step=1)
                p_vendor_id = None
                if role == "ADMIN":
                    all_vendors = api.get_vendors(token)
                    v_options = {v["vendor_id"]: v["business_name"] for v in all_vendors}
                    if v_options:
                        p_vendor_id = st.selectbox("Assign to Vendor", options=list(v_options.keys()), format_func=lambda x: f"{v_options[x]} (ID: {x})")
                    else:
                        st.warning("No vendors available. Please onboard a vendor first.")

            submitted = st.form_submit_button("Add Product to Catalog", type="primary")
            if submitted:
                if not p_name:
                    st.error("Product name is required.")
                else:
                    payload = {
                        "product_name": p_name,
                        "category": p_cat,
                        "price": p_price,
                        "stock": p_stock
                    }
                    if role == "ADMIN" and p_vendor_id:
                        payload["vendor_id"] = p_vendor_id
                    try:
                        api.create_product(token, payload)
                        st.success(f"Product '{p_name}' successfully added and inventory initialized!")
                        st.rerun()
                    except Exception as e:
                        err_msg = str(e)
                        if "409" in err_msg or "already exists" in err_msg:
                            st.error(f"⚠️ A product with that name already exists in this vendor's catalog. Use a different name or update the existing product.")
                        else:
                            st.error(f"Product creation failed: {err_msg}")

    # Search & Filters
    f1, f2 = st.columns([3, 1])
    with f1:
        search_kw = st.text_input("🔍 Search products...", "")
    with f2:
        cat_filter = st.selectbox("Category", ["All", "Electronics", "Fashion", "Books", "Home & Kitchen", "Beauty & Personal Care"])

    try:
        products = api.get_products(token, search=search_kw, category=cat_filter)
        if products:
            df_p = pd.DataFrame(products)
            st.dataframe(
                df_p[["product_id", "product_name", "category", "price", "stock", "vendor_name", "created_at"]],
                use_container_width=True,
                hide_index=True
            )

            # Edit/Delete Product Section
            st.subheader("✏️ Edit Product Details")
            sel_prod_id = st.selectbox("Select product to edit", [p["product_id"] for p in products], format_func=lambda x: f"#{x} - {[p['product_name'] for p in products if p['product_id']==x][0]}")
            curr_prod = next(p for p in products if p["product_id"] == sel_prod_id)

            e1, e2, e3 = st.columns(3)
            with e1:
                edit_price = st.number_input("New Price ($)", value=float(curr_prod["price"]), min_value=0.01, step=1.0)
            with e2:
                edit_stock = st.number_input("Sync Stock", value=int(curr_prod["stock"]), min_value=0, step=1)
            with e3:
                st.write("Actions:")
                col_save, col_del = st.columns(2)
                with col_save:
                    if st.button("Save Edits"):
                        try:
                            api.update_product(token, sel_prod_id, {"price": edit_price, "stock": edit_stock})
                            st.success("Product updated!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Update failed: {e}")
                with col_del:
                    if st.button("🗑️ Delete"):
                        try:
                            api.delete_product(token, sel_prod_id)
                            st.success("Product deleted.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Delete failed: {e}")
        else:
            st.info("No products found.")
    except Exception as e:
        st.error(f"Error fetching products: {e}")

    st.markdown(_theme_module.render_trust_footer(), unsafe_allow_html=True)

# ==========================================
# 5. INVENTORY MANAGEMENT PAGE
# ==========================================
def render_inventory_page():
    token = st.session_state["token"]
    role = st.session_state.get("role", "VENDOR")
    user_name = st.session_state.get("user_name", "User")
    current_theme = st.session_state.get("theme", _theme_module.DEFAULT_THEME)

    st.markdown(_theme_module.render_top_navbar(user_name, role, current_theme), unsafe_allow_html=True)
    st.title("📋 Inventory Management & Warehouse Tracking")

    status_filter = st.selectbox("Filter by Stock Status", ["All", "IN STOCK", "LOW STOCK", "OUT OF STOCK"])

    try:
        inv_items = api.get_inventory(token, status=status_filter)
        if inv_items:
            df_inv = pd.DataFrame(inv_items)

            # Summary KPIs for Inventory
            i1, i2, i3, i4 = st.columns(4)
            with i1:
                st.metric("Total Tracked Items", len(df_inv))
            with i2:
                in_stock_cnt = len(df_inv[df_inv["status"] == "IN STOCK"])
                st.metric("In Stock", in_stock_cnt)
            with i3:
                low_stock_cnt = len(df_inv[df_inv["status"] == "LOW STOCK"])
                st.metric("Low Stock Alerts", low_stock_cnt)
            with i4:
                out_stock_cnt = len(df_inv[df_inv["status"] == "OUT OF STOCK"])
                st.metric("Out of Stock", out_stock_cnt)

            st.dataframe(
                df_inv[["inventory_id", "product_name", "vendor_name", "current_stock", "reorder_level", "warehouse", "status", "updated_at"]],
                use_container_width=True,
                hide_index=True
            )

            # Stock Adjustment Section
            st.subheader("📦 Update Inventory Levels")
            sel_item_id = st.selectbox("Select product to restock", [item["product_id"] for item in inv_items], format_func=lambda x: f"Product #{x} - {[item['product_name'] for item in inv_items if item['product_id']==x][0]}")
            curr_item = next(item for item in inv_items if item["product_id"] == sel_item_id)

            u1, u2, u3 = st.columns(3)
            with u1:
                new_stock = st.number_input("Current Stock Count", value=int(curr_item["current_stock"]), min_value=0, step=1)
            with u2:
                new_reorder = st.number_input("Reorder Threshold", value=int(curr_item["reorder_level"]), min_value=0, step=1)
            with u3:
                new_warehouse = st.text_input("Warehouse Location", value=str(curr_item["warehouse"]))

            if st.button("Update Inventory Record", type="primary"):
                try:
                    api.update_inventory(token, sel_item_id, {
                        "current_stock": new_stock,
                        "reorder_level": new_reorder,
                        "warehouse": new_warehouse
                    })
                    st.success("Inventory updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Update failed: {e}")
        else:
            st.info("No inventory records found.")
    except Exception as e:
        st.error(f"Error loading inventory: {e}")

    st.markdown(_theme_module.render_trust_footer(), unsafe_allow_html=True)

# ==========================================
# 6. TRANSACTIONS PAGE
# ==========================================
def render_transactions_page():
    token = st.session_state["token"]
    role = st.session_state["role"]
    user_name = st.session_state.get("user_name", "User")
    current_theme = st.session_state.get("theme", _theme_module.DEFAULT_THEME)

    st.markdown(_theme_module.render_top_navbar(user_name, role, current_theme), unsafe_allow_html=True)
    st.title("💳 Transaction Management & Sales Ledger")

    # Transaction Creation Form
    with st.expander("🛒 Record New Sale / Order", expanded=False):
        products = api.get_products(token)
        if products:
            p_dict = {p["product_id"]: p for p in products if p["stock"] > 0}
            if p_dict:
                sel_p_id = st.selectbox(
                    "Select Product to Sell",
                    options=list(p_dict.keys()),
                    format_func=lambda x: f"{p_dict[x]['product_name']} | Price: ${p_dict[x]['price']} | Available: {p_dict[x]['stock']} in stock"
                )
                selected_prod = p_dict[sel_p_id]
                col_q, col_calc = st.columns(2)
                with col_q:
                    qty = st.number_input("Quantity to purchase", min_value=1, max_value=selected_prod["stock"], value=1, step=1)
                with col_calc:
                    est_total = float(selected_prod["price"]) * qty
                    st.write(f"**Total Transaction Value:** `${est_total:,.2f}`")

                if st.button("Confirm & Complete Transaction", type="primary"):
                    try:
                        resp = api.create_transaction(token, {
                            "product_id": sel_p_id,
                            "quantity": qty
                        })
                        st.success(f"Transaction #{resp['transaction_id']} executed! Stock automatically decremented.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Transaction failed: {e}")
            else:
                st.warning("All products are currently out of stock. Please restock via the Inventory tab.")
        else:
            st.info("No products available to purchase.")

    # Historical Transactions Table
    try:
        tx_list = api.get_transactions(token)
        if tx_list:
            df_tx = pd.DataFrame(tx_list)
            st.subheader(f"📜 Sales History ({len(df_tx)} Total Transactions)")
            st.dataframe(
                df_tx[["transaction_id", "product_name", "vendor_name", "quantity", "amount", "transaction_date"]],
                use_container_width=True,
                hide_index=True
            )

            # Export to CSV
            csv = df_tx.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Transactions CSV",
                data=csv,
                file_name=f"shopsense_transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )
        else:
            st.info("No transaction records recorded yet.")
    except Exception as e:
        st.error(f"Error fetching transactions: {e}")

    st.markdown(_theme_module.render_trust_footer(), unsafe_allow_html=True)

# ==========================================
# 7. ANALYTICS & REPORTING PAGE
# ==========================================
def render_analytics_page():
    token = st.session_state["token"]
    role = st.session_state["role"]
    user_name = st.session_state.get("user_name", "User")
    current_theme = st.session_state.get("theme", _theme_module.DEFAULT_THEME)

    st.markdown(_theme_module.render_top_navbar(user_name, role, current_theme), unsafe_allow_html=True)
    st.title("📈 Marketplace Analytics & Performance Reports")

    # Overview KPIs
    summary = api.get_summary(token)
    if role == "ADMIN":
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        with m1:
            st.metric("Total Revenue", f"${summary['total_revenue']:,.2f}")
        with m2:
            st.metric("Total Transactions", f"{summary['total_transactions']:,}")
        with m3:
            st.metric("Units Sold", f"{summary['total_quantity_sold']:,}")
        with m4:
            st.metric("Avg Order Value", f"${summary['average_transaction_value']:,.2f}")
        with m5:
            st.metric("Total Vendors", f"{summary['total_vendors']}")
        with m6:
            st.metric("Total Products", f"{summary['total_products']}")
    else:
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.metric("Total Revenue", f"${summary['total_revenue']:,.2f}")
        with m2:
            st.metric("Total Transactions", f"{summary['total_transactions']:,}")
        with m3:
            st.metric("Units Sold", f"{summary['total_quantity_sold']:,}")
        with m4:
            st.metric("Avg Order Value", f"${summary['average_transaction_value']:,.2f}")
        with m5:
            st.metric("Total Products", f"{summary['total_products']}")

    st.markdown("---")

    # Revenue Trend Chart
    st.subheader("📅 Time-Series Revenue Aggregation")
    trend_data = api.get_revenue_trend(token)
    if trend_data:
        df_trend = pd.DataFrame(trend_data)
        fig = px.bar(
            df_trend,
            x="date",
            y="revenue",
            text_auto=True,
            title="Revenue Aggregated by Date",
            labels={"date": "Date", "revenue": "Revenue ($)"}
        )
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    # Vendor & Product Performance Tables
    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.subheader("🏢 Vendor Revenue Breakdown")
        v_data = api.get_vendor_performance(token)
        if v_data:
            df_v = pd.DataFrame(v_data)
            st.dataframe(
                df_v[["business_name", "category", "total_revenue", "total_transactions", "total_quantity_sold"]],
                use_container_width=True,
                hide_index=True
            )
            csv_v = df_v.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export Vendor Metrics CSV",
                csv_v,
                "vendor_performance.csv",
                "text/csv"
            )

    with col_t2:
        st.subheader("🏷️ Product Sales Ranking")
        p_data = api.get_product_performance(token)
        if p_data:
            df_p = pd.DataFrame(p_data)
            st.dataframe(
                df_p[["product_name", "category", "total_revenue", "quantity_sold", "inventory_status"]],
                use_container_width=True,
                hide_index=True
            )
            csv_p = df_p.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export Product Metrics CSV",
                csv_p,
                "product_performance.csv",
                "text/csv"
            )

    st.markdown(_theme_module.render_trust_footer(), unsafe_allow_html=True)

# ==========================================
# 8. CUSTOMER VIEWS
# ==========================================
def render_customer_catalog():
    token = st.session_state["token"]
    user_name = st.session_state.get("user_name", "Customer")
    role = st.session_state.get("role", "CUSTOMER")
    current_theme = st.session_state.get("theme", _theme_module.DEFAULT_THEME)

    # 1. Top E-Commerce Header Bar
    st.markdown(_theme_module.render_top_navbar(user_name, role, current_theme), unsafe_allow_html=True)

    try:
        products = api.get_products(token)
    except Exception as e:
        st.error(f"Error fetching products: {e}")
        return

    if not products:
        st.info("No products currently listed in the marketplace.")
        return

    # Extract all categories
    categories = ["All Categories"] + sorted(list(set(p.get("category", "General") for p in products)))

    # Category Ribbon
    cat_selection = st.session_state.get("customer_cat_filter", "All Categories")
    st.markdown(_theme_module.render_category_ribbon(cat_selection), unsafe_allow_html=True)

    # Search, Category Filter & Sort Options
    col_search, col_cat, col_sort = st.columns([3, 2, 2])
    with col_search:
        search_query = st.text_input(
            "Search Products",
            placeholder="🔍 Search for headphones, fashion, books, home essentials...",
            label_visibility="collapsed",
            key="cust_search_input"
        ).strip().lower()
    with col_cat:
        selected_category = st.selectbox(
            "Category Filter",
            categories,
            index=categories.index(cat_selection) if cat_selection in categories else 0,
            label_visibility="collapsed",
            key="cust_cat_select"
        )
        st.session_state["customer_cat_filter"] = selected_category
    with col_sort:
        sort_by = st.selectbox(
            "Sort Order",
            ["Featured Deals", "Price: Low to High", "Price: High to Low", "Product Name: A to Z"],
            label_visibility="collapsed",
            key="cust_sort_select"
        )

    # Filtered products
    filtered = products
    if search_query:
        filtered = [
            p for p in filtered 
            if search_query in p.get("product_name", "").lower() 
            or search_query in p.get("category", "").lower()
            or search_query in str(p.get("vendor_name", "")).lower()
        ]
    if selected_category != "All Categories":
        filtered = [p for p in filtered if p.get("category") == selected_category]

    # Sorting
    if sort_by == "Price: Low to High":
        filtered = sorted(filtered, key=lambda x: float(x.get("price", 0.0)))
    elif sort_by == "Price: High to Low":
        filtered = sorted(filtered, key=lambda x: float(x.get("price", 0.0)), reverse=True)
    elif sort_by == "Product Name: A to Z":
        filtered = sorted(filtered, key=lambda x: x.get("product_name", "").lower())

    st.markdown(
        f"<div style='font-size:0.95rem; font-weight:700; color:#555; margin: 6px 0 16px 0;'>"
        f"Showing <strong style='color:var(--ss-primary);'>{len(filtered)}</strong> products for you"
        f"</div>",
        unsafe_allow_html=True
    )

    if not filtered:
        st.warning("No products matched your search or category filters. Try resetting filters.")
        return

    cols_per_row = 3
    for i in range(0, len(filtered), cols_per_row):
        row_cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(filtered):
                p = filtered[i + j]
                with row_cols[j]:
                    # Render modern product card
                    st.markdown(_theme_module.render_product_card_html(p, current_theme), unsafe_allow_html=True)

                    stock_qty = p.get("stock", 0)
                    if stock_qty > 0:
                        c_qty, c_btn = st.columns([1, 2])
                        with c_qty:
                            qty = st.number_input(
                                "Qty",
                                min_value=1,
                                max_value=stock_qty,
                                value=1,
                                step=1,
                                key=f"cust_qty_{p['product_id']}",
                                label_visibility="collapsed"
                            )
                        with c_btn:
                            if st.button("⚡ Buy Now", key=f"cust_buy_{p['product_id']}", type="primary", use_container_width=True):
                                try:
                                    res = api.create_transaction(token, {
                                        "product_id": p["product_id"],
                                        "quantity": qty
                                    })
                                    st.success(f"🎉 Order placed! Order ID: #{res['transaction_id']}")
                                    st.rerun()
                                except Exception as err:
                                    st.error(f"Error placing order: {err}")
                    else:
                        st.button("❌ Out of Stock", key=f"cust_out_{p['product_id']}", disabled=True, use_container_width=True)

    # Trust Footer
    st.markdown(_theme_module.render_trust_footer(), unsafe_allow_html=True)


def render_customer_orders():
    token = st.session_state["token"]
    user_name = st.session_state.get("user_name", "Customer")
    role = st.session_state.get("role", "CUSTOMER")
    current_theme = st.session_state.get("theme", _theme_module.DEFAULT_THEME)

    st.markdown(_theme_module.render_top_navbar(user_name, role, current_theme), unsafe_allow_html=True)
    st.title("📦 Your Orders & Purchase History")

    try:
        txs = api.get_transactions(token)
        if txs:
            # Summary Metrics for Orders
            total_spent = sum(float(tx.get("amount", 0.0)) for tx in txs)
            total_items = sum(int(tx.get("quantity", 0)) for tx in txs)

            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Total Orders Placed", len(txs))
            with m2:
                st.metric("Total Items Purchased", f"{total_items:,} units")
            with m3:
                st.metric("Total Amount Spent", f"${total_spent:,.2f}")

            st.markdown("---")

            # Render individual order cards
            for tx in txs:
                st.markdown(_theme_module.render_order_card_html(tx, current_theme), unsafe_allow_html=True)

            # Raw Ledger Table in Expander
            with st.expander("📜 View Raw Transaction Ledger Table", expanded=False):
                df = pd.DataFrame(txs)
                st.dataframe(
                    df[["transaction_id", "product_name", "vendor_name", "quantity", "amount", "transaction_date"]],
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info("🛒 You have not placed any orders yet. Check out the Products catalog to start shopping!")
    except Exception as e:
        st.error(f"Error fetching orders: {e}")

    st.markdown(_theme_module.render_trust_footer(), unsafe_allow_html=True)


def render_customer_profile():
    user_name = st.session_state.get("user_name", "Customer")
    user_email = st.session_state.get("user", "")
    role = st.session_state.get("role", "CUSTOMER")
    current_theme = st.session_state.get("theme", _theme_module.DEFAULT_THEME)

    st.markdown(_theme_module.render_top_navbar(user_name, role, current_theme), unsafe_allow_html=True)
    st.title("👤 My Account & Membership")

    # Member Profile Card
    st.markdown(_theme_module.render_customer_profile_card(user_name, user_email, role, current_theme), unsafe_allow_html=True)

    # Address and Preferences Cards
    col_addr, col_sec = st.columns(2)
    with col_addr:
        with st.container(border=True):
            st.subheader("📍 Default Delivery Address")
            st.write(f"**{user_name}**")
            st.write("#42, Tech Boulevard, Koramangala 4th Block")
            st.write("Bangalore, Karnataka – 560034")
            st.write("📞 Contact: +91 98765 43210")
            st.caption("⚡ Verified primary shipping address for 1-day delivery")

    with col_sec:
        with st.container(border=True):
            st.subheader("🔒 Account Security & Preferences")
            st.write(f"Account Email: **{user_email}**")
            st.write("Two-Factor Authentication: **Enabled (SMS)**")
            st.write("Currency: **USD ($) / INR (₹)**")
            st.write("Notification Preferences: **Email & SMS Orders**")

    st.markdown(_theme_module.render_trust_footer(), unsafe_allow_html=True)


# ==========================================
# MAIN APPLICATION ROUTER
# ==========================================
def main():
    if not st.session_state["token"]:
        render_auth_page()
    else:
        role = st.session_state["role"]
        user_email = st.session_state["user"]
        user_name = st.session_state.get("user_name", "User")

        # Sidebar Navigation
        with st.sidebar:
            st.markdown("""
            <div class="ss-sidebar-header">
                <div style="font-size: 1.35rem; font-weight: 800; display:flex; align-items:center; gap:8px;">
                    🛍️ ShopSense
                </div>
                <div style="font-size: 0.75rem; opacity: 0.9; margin-top:2px;">
                    Multi-Vendor Marketplace & Analytics
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Theme Switcher
            st.markdown("<div style='font-size:0.8rem; font-weight:700; color:#555; margin-bottom:4px;'>🎨 APP UI THEME</div>", unsafe_allow_html=True)
            theme_choice = st.selectbox(
                "UI Theme",
                list(_theme_module.THEME_CONFIGS.keys()),
                index=list(_theme_module.THEME_CONFIGS.keys()).index(st.session_state["theme"]),
                key="sidebar_theme_switcher",
                label_visibility="collapsed"
            )
            if theme_choice != st.session_state["theme"]:
                st.session_state["theme"] = theme_choice
                st.rerun()

            st.markdown(f"""
            <div class="ss-sidebar-user-card">
                <div style="font-size: 0.88rem; font-weight: 700; color: #212121;">👤 {user_name}</div>
                <div style="font-size: 0.75rem; color: #666; margin-top: 2px; overflow:hidden; text-overflow:ellipsis;">📧 {user_email}</div>
                <div style="margin-top: 8px;">
                    <span class="status-badge-active">{role}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")

            # Nav items depend on role
            if role == "CUSTOMER":
                nav_options = ["🛍️ Products", "📦 Orders", "👤 Profile"]
            elif role == "ADMIN":
                nav_options = ["📊 Dashboard", "🏢 Vendors", "📦 Products", "📋 Inventory", "💳 Transactions", "📈 Analytics"]
            else:  # VENDOR
                nav_options = ["📊 Dashboard", "📦 Products", "📋 Inventory", "💳 Transactions", "📈 Analytics"]

            chosen_page = st.radio("Navigation", nav_options, index=0)

            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                logout()

        # Render chosen page based on role and selection
        if role == "CUSTOMER":
            if "Products" in chosen_page:
                render_customer_catalog()
            elif "Orders" in chosen_page:
                render_customer_orders()
            elif "Profile" in chosen_page:
                render_customer_profile()
        else:
            if "Dashboard" in chosen_page:
                render_dashboard_page()
            elif "Vendors" in chosen_page:
                render_vendors_page()
            elif "Products" in chosen_page:
                render_products_page()
            elif "Inventory" in chosen_page:
                render_inventory_page()
            elif "Transactions" in chosen_page:
                render_transactions_page()
            elif "Analytics" in chosen_page:
                render_analytics_page()

if __name__ == "__main__":
    main()

