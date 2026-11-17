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

try:
    import dashboard.inventory_ui as _inv_ui
    importlib.reload(_inv_ui)
except Exception:
    import inventory_ui as _inv_ui
    importlib.reload(_inv_ui)

try:
    import dashboard.customer_analytics_ui as _cust_ui
    importlib.reload(_cust_ui)
except Exception:
    import customer_analytics_ui as _cust_ui
    importlib.reload(_cust_ui)

try:
    import dashboard.recommendation_ui as _rec_ui
    importlib.reload(_rec_ui)
except Exception:
    import recommendation_ui as _rec_ui
    importlib.reload(_rec_ui)

try:
    import dashboard.vendor_applications_ui as _vapp_ui
    importlib.reload(_vapp_ui)
except Exception:
    import vendor_applications_ui as _vapp_ui
    importlib.reload(_vapp_ui)

try:
    import dashboard.bi_dashboard_ui as _bi_ui
    importlib.reload(_bi_ui)
except Exception:
    import bi_dashboard_ui as _bi_ui
    importlib.reload(_bi_ui)

try:
    import dashboard.reports_ui as _reports_ui
    importlib.reload(_reports_ui)
except Exception:
    import reports_ui as _reports_ui
    importlib.reload(_reports_ui)

try:
    import dashboard.validation_ui as _val_ui
    importlib.reload(_val_ui)
except Exception:
    import validation_ui as _val_ui
    importlib.reload(_val_ui)

# Page configuration
st.set_page_config(
    page_title="ShopSense – Multi-Vendor Analytics & Marketplace",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed"
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
if "user_phone" not in st.session_state:
    st.session_state["user_phone"] = None
if "vendor_id" not in st.session_state:
    st.session_state["vendor_id"] = None

def logout():
    st.session_state["token"] = None
    st.session_state["user"] = None
    st.session_state["role"] = None
    st.session_state["user_phone"] = None
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
                            actual_role = resp["role"]
                            
                            # Validate that the authenticated user matches the chosen sign-in role
                            if actual_role != login_role:
                                role_names = {"ADMIN": "Admin", "VENDOR": "Vendor", "CUSTOMER": "Customer"}
                                st.error(f"Access Denied: This account is registered as '{role_names.get(actual_role, actual_role)}', not as '{role_names.get(login_role, login_role)}'. Please select '{role_names.get(actual_role, actual_role)}' to sign in.")
                            else:
                                st.session_state["token"] = resp["access_token"]
                                st.session_state["user"] = resp["email"]
                                st.session_state["user_name"] = resp["full_name"]
                                st.session_state["user_phone"] = resp.get("phone")
                                st.session_state["role"] = resp["role"]
                                st.session_state["vendor_id"] = resp.get("vendor_id")
                                st.session_state["user_id"] = resp.get("user_id")
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
            reg_phone = st.text_input("Phone Number (10–15 digits) *", key="reg_phone", placeholder="e.g. 9876543210")
            reg_pw = st.text_input("Password (min 6 chars)", type="password", key="reg_pw")
            reg_pw_confirm = st.text_input("Confirm Password", type="password", key="reg_pw_confirm")

            reg_bname = None
            reg_cat = None

            if reg_role == "VENDOR":
                st.markdown("##### 🏪 Vendor Store Details")
                reg_bname = st.text_input("Business / Store Name *", key="reg_bname", placeholder="e.g. Apex Electronics")
                reg_cat = st.selectbox(
                    "Store Category *",
                    ["Electronics", "Fashion", "Books", "Home & Kitchen", "Beauty & Personal Care", "General"],
                    key="reg_cat"
                )

            if st.button("Create Account", type="primary", use_container_width=True):
                if not reg_name or not reg_email or not reg_phone or not reg_pw or not reg_pw_confirm:
                    st.error("All fields are required.")
                elif len(reg_pw) < 6:
                    st.error("Password must be at least 6 characters.")
                elif reg_pw != reg_pw_confirm:
                    st.error("Passwords do not match.")
                elif reg_role == "VENDOR" and not reg_bname:
                    st.error("Business / Store Name is required for Vendor onboarding.")
                else:
                    try:
                        with st.spinner("Creating account..."):
                            resp = api.register(
                                reg_name.strip(),
                                reg_email.strip(),
                                reg_pw,
                                reg_role,
                                phone=reg_phone.strip(),
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

    # If Admin, show Quick Intelligence Tabs for Customer Analytics & Recommendations
    if role == "ADMIN":
        st.subheader("🧠 Platform Intelligence & Analytics")
        dash_tab_sales, dash_tab_customers, dash_tab_recs = st.tabs([
            "📈 Sales & Vendor Performance",
            "👥 Customer Analytics & Segmentation",
            "💡 Recommendation Engine & Model Evaluation"
        ])

        with dash_tab_sales:
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

        with dash_tab_customers:
            _cust_ui.render_customer_intelligence_section(api, token, role, _theme_module, current_theme)

        with dash_tab_recs:
            admin_user_id = st.session_state.get("user_id", 1)
            _rec_ui.render_recommendation_intelligence_section(api, token, role, admin_user_id, _theme_module, current_theme)

    else:
        # Vendor dashboard visualizations
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

        c_bottom1, c_bottom2 = st.columns(2)
        with c_bottom1:
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
    st.title("🏢 Vendors Management")

    if role != "ADMIN":
        st.warning("Only Marketplace Administrators can manage vendor accounts.")
        return

    tab_overview, tab_apps = st.tabs([
        "📋 All Vendors & Management",
        "📝 Applications & Approvals"
    ])

    with tab_apps:
        _vapp_ui.render_vendor_applications_page(api, token, current_theme)

    with tab_overview:

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
                p_img = st.text_input("Product Image URL (Optional)", placeholder="https://images.unsplash.com/...")
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
                    if p_img and p_img.strip():
                        payload["image_url"] = p_img.strip()
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
            cols_to_show = ["product_id", "product_name", "category", "price", "stock", "image_url", "vendor_name", "created_at"]
            display_cols = [c for c in cols_to_show if c in df_p.columns]
            st.dataframe(
                df_p[display_cols],
                use_container_width=True,
                hide_index=True
            )

            # Edit/Delete Product Section
            st.subheader("✏️ Edit Product Details & Image")
            sel_prod_id = st.selectbox("Select product to edit", [p["product_id"] for p in products], format_func=lambda x: f"#{x} - {[p['product_name'] for p in products if p['product_id']==x][0]}")
            curr_prod = next(p for p in products if p["product_id"] == sel_prod_id)

            # Product image preview & input
            prev_col, edit_col = st.columns([1, 2])
            with prev_col:
                prod_preview_img = curr_prod.get("image_url") or _theme_module.get_product_image(curr_prod["product_name"], curr_prod.get("category", "General"))
                st.markdown(f"""
                <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 6px; text-align: center; background: #fff;">
                    <img src="{prod_preview_img}" alt="{curr_prod['product_name']}" style="max-height: 140px; max-width: 100%; object-fit: contain; border-radius: 6px;" />
                    <div style="font-size: 0.75rem; color: #64748b; margin-top: 4px;">Live Image Preview</div>
                </div>
                """, unsafe_allow_html=True)
            with edit_col:
                edit_img_url = st.text_input("Product Image URL", value=curr_prod.get("image_url") or "", key=f"edit_img_{curr_prod['product_id']}")

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
                            update_payload = {"price": edit_price, "stock": edit_stock}
                            if edit_img_url.strip():
                                update_payload["image_url"] = edit_img_url.strip()
                            api.update_product(token, sel_prod_id, update_payload)
                            st.success("Product and image updated successfully!")
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
    # Render complete Milestone 2 Inventory Intelligence Suite
    _inv_ui.render_inventory_intelligence_section(api, token, role, _theme_module, current_theme)

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

    if not filtered:
        st.warning("No products matched your search or category filters. Try resetting filters.")
        return

    # Pagination Settings (18 products per page for fast rendering)
    PAGE_SIZE = 18
    total_products = len(filtered)
    total_pages = max(1, (total_products + PAGE_SIZE - 1) // PAGE_SIZE)

    # Manage page state
    if "cust_catalog_page" not in st.session_state:
        st.session_state["cust_catalog_page"] = 1
    
    # Ensure current page is within valid range
    if st.session_state["cust_catalog_page"] > total_pages:
        st.session_state["cust_catalog_page"] = 1

    current_page = st.session_state["cust_catalog_page"]
    start_idx = (current_page - 1) * PAGE_SIZE
    end_idx = min(start_idx + PAGE_SIZE, total_products)
    page_items = filtered[start_idx:end_idx]

    # Header with page summary and pagination controls
    head_c1, head_c2 = st.columns([3, 2])
    with head_c1:
        st.markdown(
            f"<div style='font-size:0.95rem; font-weight:700; color:#555; padding-top: 8px;'>"
            f"Showing <strong style='color:var(--ss-primary);'>{start_idx + 1}–{end_idx}</strong> of "
            f"<strong style='color:var(--ss-primary);'>{total_products}</strong> products (Page {current_page} of {total_pages})"
            f"</div>",
            unsafe_allow_html=True
        )
    with head_c2:
        if total_pages > 1:
            p_prev, p_info, p_next = st.columns([1, 2, 1])
            with p_prev:
                if st.button("◀ Prev", disabled=(current_page <= 1), use_container_width=True, key="cat_btn_prev"):
                    st.session_state["cust_catalog_page"] -= 1
                    st.rerun()
            with p_info:
                st.markdown(f"<div style='text-align:center; padding-top:6px; font-weight:600; font-size:0.85rem; color:#64748b;'>Page {current_page} / {total_pages}</div>", unsafe_allow_html=True)
            with p_next:
                if st.button("Next ▶", disabled=(current_page >= total_pages), use_container_width=True, key="cat_btn_next"):
                    st.session_state["cust_catalog_page"] += 1
                    st.rerun()

    st.markdown("<hr style='margin: 8px 0 16px 0; border: none; border-top: 1px solid #f1f5f9;'/>", unsafe_allow_html=True)

    cols_per_row = 3
    for i in range(0, len(page_items), cols_per_row):
        row_cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(page_items):
                p = page_items[i + j]
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

    # Bottom pagination controls
    if total_pages > 1:
        st.markdown("<hr style='margin: 20px 0 10px 0; border: none; border-top: 1px solid #e2e8f0;'/>", unsafe_allow_html=True)
        bot_prev, bot_info, bot_next = st.columns([1, 3, 1])
        with bot_prev:
            if st.button("◀ Previous Page", disabled=(current_page <= 1), use_container_width=True, key="cat_bot_prev"):
                st.session_state["cust_catalog_page"] -= 1
                st.rerun()
        with bot_info:
            st.markdown(f"<div style='text-align:center; padding-top:6px; font-weight:700; color:#475569;'>Page {current_page} of {total_pages} ({total_products} items total)</div>", unsafe_allow_html=True)
        with bot_next:
            if st.button("Next Page ▶", disabled=(current_page >= total_pages), use_container_width=True, key="cat_bot_next"):
                st.session_state["cust_catalog_page"] += 1
                st.rerun()

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
    token = st.session_state.get("token")
    role = st.session_state.get("role", "CUSTOMER")
    current_theme = st.session_state.get("theme", _theme_module.DEFAULT_THEME)

    # Fetch live profile data from backend API
    db_profile = None
    if role == "VENDOR":
        try:
            db_profile = api.get_vendor_profile(token)
            st.session_state["user_name"] = db_profile.get("full_name") or db_profile.get("owner_name")
            st.session_state["user_phone"] = db_profile.get("phone")
            st.session_state["vendor_name"] = db_profile.get("business_name")
            st.session_state["avatar_url"] = db_profile.get("avatar_url")
        except Exception:
            pass
    else:
        try:
            db_profile = api.get_customer_profile(token)
            st.session_state["user_name"] = db_profile.get("full_name")
            st.session_state["user_phone"] = db_profile.get("phone")
            st.session_state["avatar_url"] = db_profile.get("avatar_url")
        except Exception:
            pass

    user_name = st.session_state.get("user_name", "User")
    user_email = st.session_state.get("user", "")
    user_phone = st.session_state.get("user_phone") or "+91 98765 43210"
    avatar_url = st.session_state.get("avatar_url")

    st.markdown(_theme_module.render_top_navbar(user_name, role, current_theme), unsafe_allow_html=True)
    st.title("👤 My Account & Membership")

    # Member Profile Card with Edit Profile toggle
    st.markdown(_theme_module.render_customer_profile_card(user_name, user_email, role, current_theme, phone=user_phone, avatar_url=avatar_url), unsafe_allow_html=True)

    # Edit Profile State Management
    if "is_editing_profile" not in st.session_state:
        st.session_state["is_editing_profile"] = False

    col_btn, _ = st.columns([2, 5])
    with col_btn:
        if not st.session_state["is_editing_profile"]:
            if st.button("✏️ Edit Profile", type="primary", use_container_width=True):
                st.session_state["is_editing_profile"] = True
                st.rerun()
        else:
            if st.button("❌ Cancel Editing", type="secondary", use_container_width=True):
                st.session_state["is_editing_profile"] = False
                st.rerun()

    # ==========================================
    # EDIT PROFILE FORM VIEW
    # ==========================================
    if st.session_state["is_editing_profile"]:
        st.markdown("<hr style='margin: 14px 0;'/>", unsafe_allow_html=True)
        st.subheader("✏️ Edit Account & Profile Information")

        if role == "VENDOR":
            v_prof = db_profile or {}
            with st.form("edit_vendor_profile_form"):
                st.markdown("#### 👤 1. Personal Details")
                cp1, cp2 = st.columns(2)
                with cp1:
                    f_name = st.text_input("Full Name (Owner Name) *", value=v_prof.get("full_name") or user_name)
                    f_phone = st.text_input("Mobile Contact Number *", value=v_prof.get("phone") or user_phone)
                with cp2:
                    st.text_input("Registered Email Address", value=user_email, disabled=True)
                    f_avatar = st.text_input("Profile Avatar Image URL", value=v_prof.get("avatar_url") or "", placeholder="https://example.com/avatar.jpg")

                st.markdown("#### 🏢 2. Business Details")
                cb1, cb2 = st.columns(2)
                with cb1:
                    b_name = st.text_input("Business / Store Name *", value=v_prof.get("business_name") or "")
                    b_desc = st.text_area("Business Description", value=v_prof.get("description") or "", height=85)
                with cb2:
                    b_addr = st.text_input("Business Street Address", value=v_prof.get("business_address") or "")
                    c_city, c_state, c_pin = st.columns(3)
                    with c_city:
                        b_city = st.text_input("City", value=v_prof.get("city") or "")
                    with c_state:
                        b_state = st.text_input("State", value=v_prof.get("state") or "")
                    with c_pin:
                        b_pin = st.text_input("PIN Code", value=v_prof.get("pincode") or "")

                st.markdown("#### ⚙️ 3. Preferences")
                c_pref1, c_pref2 = st.columns(2)
                v_prefs = v_prof.get("preferences") or {}
                with c_pref1:
                    pref_curr = st.selectbox("Preferred Currency", ["USD", "INR", "EUR", "GBP"], index=["USD", "INR", "EUR", "GBP"].index(v_prefs.get("currency", "USD")) if v_prefs.get("currency") in ["USD", "INR", "EUR", "GBP"] else 0)
                with c_pref2:
                    pref_email = st.checkbox("Email Notifications (Order & Account Alerts)", value=v_prefs.get("email_notifications", True))
                    pref_sms = st.checkbox("SMS Notifications (Dispatch & Security)", value=v_prefs.get("sms_notifications", True))

                btn_sub = st.form_submit_button("💾 Save Vendor Profile", type="primary", use_container_width=True)
                if btn_sub:
                    if not f_name or not b_name:
                        st.error("Name and Business Name cannot be empty.")
                    else:
                        try:
                            updated = api.update_vendor_profile(token, {
                                "full_name": f_name,
                                "phone": f_phone,
                                "avatar_url": f_avatar,
                                "business_name": b_name,
                                "description": b_desc,
                                "business_address": b_addr,
                                "city": b_city,
                                "state": b_state,
                                "pincode": b_pin,
                                "preferences": {
                                    "currency": pref_curr,
                                    "email_notifications": pref_email,
                                    "sms_notifications": pref_sms
                                }
                            })
                            st.session_state["user_name"] = updated.get("full_name") or f_name
                            st.session_state["user_phone"] = updated.get("phone") or f_phone
                            st.session_state["vendor_name"] = updated.get("business_name") or b_name
                            st.session_state["avatar_url"] = updated.get("avatar_url") or f_avatar
                            st.session_state["is_editing_profile"] = False
                            st.success("✅ Vendor profile updated and synchronized successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to update profile: {e}")
        else:
            # CUSTOMER EDIT FORM
            c_prof = db_profile or {}
            with st.form("edit_customer_profile_form"):
                st.markdown("#### 👤 1. Personal Details")
                cp1, cp2 = st.columns(2)
                with cp1:
                    cust_name = st.text_input("Full Name *", value=c_prof.get("full_name") or user_name)
                    cust_phone = st.text_input("Mobile Contact Number *", value=c_prof.get("phone") or user_phone)
                with cp2:
                    st.text_input("Registered Email Address", value=user_email, disabled=True)
                    cust_avatar = st.text_input("Profile Avatar Image URL", value=c_prof.get("avatar_url") or "", placeholder="https://example.com/avatar.jpg")

                st.markdown("#### ⚙️ 2. Shopping & Notification Preferences")
                c_pref1, c_pref2 = st.columns(2)
                c_prefs = c_prof.get("preferences") or {}
                with c_pref1:
                    pref_curr = st.selectbox("Preferred Currency", ["USD", "INR", "EUR", "GBP"], index=["USD", "INR", "EUR", "GBP"].index(c_prefs.get("currency", "USD")) if c_prefs.get("currency") in ["USD", "INR", "EUR", "GBP"] else 0)
                with c_pref2:
                    pref_email = st.checkbox("Email Notifications (Order & Account Alerts)", value=c_prefs.get("email_notifications", True))
                    pref_sms = st.checkbox("SMS Notifications (Dispatch & Security)", value=c_prefs.get("sms_notifications", True))
                    pref_orders = st.checkbox("Real-Time Order Tracking Notifications", value=c_prefs.get("order_notifications", True))

                btn_sub_c = st.form_submit_button("💾 Save Customer Details", type="primary", use_container_width=True)
                if btn_sub_c:
                    if not cust_name:
                        st.error("Name cannot be empty.")
                    else:
                        try:
                            updated = api.update_customer_profile(token, {
                                "full_name": cust_name,
                                "phone": cust_phone,
                                "avatar_url": cust_avatar,
                                "preferences": {
                                    "currency": pref_curr,
                                    "email_notifications": pref_email,
                                    "sms_notifications": pref_sms,
                                    "order_notifications": pref_orders
                                }
                            })
                            st.session_state["user_name"] = updated.get("full_name") or cust_name
                            st.session_state["user_phone"] = updated.get("phone") or cust_phone
                            st.session_state["avatar_url"] = updated.get("avatar_url") or cust_avatar
                            st.session_state["is_editing_profile"] = False
                            st.success("✅ Profile details updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to update profile: {e}")

    # ==========================================
    # DISPLAY VIEW (MATCHING REFERENCE UI)
    # ==========================================
    col_addr, col_sec = st.columns(2)

    with col_addr:
        with st.container(border=True):
            if role == "VENDOR":
                st.subheader("🏢 Registered Business Address")
                v_p = db_profile or {}
                st.write(f"**{v_p.get('business_name') or user_name}**")
                b_addr_str = v_p.get("business_address") or "#42, Commercial Avenue, Sector 5"
                b_city_str = f"{v_p.get('city') or 'Bangalore'}, {v_p.get('state') or 'Karnataka'} – {v_p.get('pincode') or '560034'}"
                st.write(b_addr_str)
                st.write(b_city_str)
                st.write(f"📞 Contact: {v_p.get('phone') or user_phone}")
                st.caption("⚡ Registered vendor fulfillment hub & dispatch location")
            else:
                st.subheader("📍 Default Delivery Address")
                c_p = db_profile or {}
                def_addr = c_p.get("default_address")
                if def_addr:
                    st.write(f"**{def_addr.get('recipient_name') or user_name}**")
                    bld = f"{def_addr.get('house_building')}, " if def_addr.get('house_building') else ""
                    st.write(f"{bld}{def_addr.get('street_address')}")
                    st.write(f"{def_addr.get('city')}, {def_addr.get('state')} – {def_addr.get('pincode')}")
                    st.write(f"📞 Contact: {def_addr.get('phone') or user_phone}")
                else:
                    st.write(f"**{user_name}**")
                    st.write("#42, Tech Boulevard, Koramangala 4th Block")
                    st.write("Bangalore, Karnataka – 560034")
                    st.write(f"📞 Contact: {user_phone}")
                st.caption("⚡ Verified primary shipping address for 1-day delivery")

                # Expandable multi-address management for Customer
                with st.expander("📋 Manage Delivery Addresses"):
                    addrs = c_p.get("addresses", [])
                    if addrs:
                        for a in addrs:
                            c_a1, c_a2 = st.columns([3, 1])
                            with c_a1:
                                is_def_badge = " *(Default)*" if a.get("is_default") else ""
                                st.markdown(f"**{a.get('recipient_name')}** ({a.get('address_type', 'HOME')}){is_def_badge}")
                                st.caption(f"{a.get('street_address')}, {a.get('city')}, {a.get('state')} - {a.get('pincode')} | 📞 {a.get('phone')}")
                            with c_a2:
                                if not a.get("is_default"):
                                    if st.button("Set Default", key=f"set_def_{a.get('address_id')}", use_container_width=True):
                                        api.set_default_address(token, a.get("address_id"))
                                        st.rerun()

                    # Add new address form
                    with st.form("add_new_address_form"):
                        st.markdown("##### ➕ Add New Address")
                        na1, na2 = st.columns(2)
                        with na1:
                            r_name = st.text_input("Recipient Name", value=user_name)
                            r_phone = st.text_input("Contact Phone", value=user_phone)
                            r_street = st.text_input("Street / Area Address")
                        with na2:
                            r_city = st.text_input("City")
                            r_state = st.text_input("State")
                            r_pin = st.text_input("PIN Code")
                        r_def = st.checkbox("Set as default shipping address", value=True)
                        if st.form_submit_button("Save New Address"):
                            if not r_name or not r_street or not r_city or not r_pin:
                                st.error("Please fill all required address fields.")
                            else:
                                api.create_address(token, {
                                    "recipient_name": r_name,
                                    "phone": r_phone,
                                    "street_address": r_street,
                                    "city": r_city,
                                    "state": r_state,
                                    "pincode": r_pin,
                                    "is_default": r_def,
                                    "address_type": "HOME"
                                })
                                st.success("Address added!")
                                st.rerun()

    with col_sec:
        with st.container(border=True):
            st.subheader("🔒 Account Security & Preferences")
            st.write(f"Account Email: **{user_email}**")
            st.write("Two-Factor Authentication: **Verified Password Authentication**")
            curr_pref = (db_profile or {}).get("preferences", {}).get("currency", "USD ($) / INR (₹)")
            st.write(f"Currency: **{curr_pref}**")
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
        current_theme = st.session_state.get("theme", _theme_module.DEFAULT_THEME)

        # Top Horizontal Navigation Header
        top_col_brand, top_col_theme, top_col_user = st.columns([4, 3, 2])
        with top_col_brand:
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:10px; padding: 6px 0;">
                <span style="font-size: 1.6rem; font-weight: 800; color: var(--ss-primary, #0284c7);">🛍️ ShopSense</span>
                <span style="background: rgba(2,132,199,0.12); color: var(--ss-primary, #0284c7); padding: 3px 10px; border-radius: 9999px; font-size: 0.75rem; font-weight: 700;">
                    {_theme_module.get_theme_config(current_theme).get('brand_badge', 'Marketplace')}
                </span>
            </div>
            """, unsafe_allow_html=True)
        with top_col_theme:
            st.selectbox(
                "UI Theme",
                list(_theme_module.THEME_CONFIGS.keys()),
                index=list(_theme_module.THEME_CONFIGS.keys()).index(current_theme),
                key="top_navbar_theme_switcher",
                label_visibility="collapsed"
            )
            if st.session_state.get("top_navbar_theme_switcher") and st.session_state["top_navbar_theme_switcher"] != current_theme:
                st.session_state["theme"] = st.session_state["top_navbar_theme_switcher"]
                st.rerun()
        with top_col_user:
            u_col1, u_col2 = st.columns([2, 1])
            with u_col1:
                st.markdown(f"""
                <div style="text-align:right; padding-top:4px;">
                    <span style="font-weight:700; font-size:0.88rem; color:#1e293b;">👤 {user_name}</span>
                    <span style="background:#e2e8f0; color:#475569; padding:2px 8px; border-radius:6px; font-size:0.7rem; font-weight:700; margin-left:4px;">{role}</span>
                </div>
                """, unsafe_allow_html=True)
            with u_col2:
                if st.button("🚪 Logout", key="top_logout_btn", use_container_width=True):
                    logout()

        # Define Role-based Horizontal Navigation Menus
        if role == "ADMIN":
            nav_options = [
                "📊 Dashboard",
                "📊 Business Intelligence",
                "🏢 Vendors Management",
                "📦 Products",
                "🏷️ Categories",
                "📦 Orders",
                "📋 Inventory",
                "👥 Customer Analytics",
                "💡 Recommendations",
                "📈 Analytics",
                "📥 Reports",
                "🛡️ Data Validation"
            ]
        elif role == "VENDOR":
            nav_options = [
                "📊 Dashboard",
                "📦 My Products",
                "📋 Inventory",
                "📦 Orders",
                "📈 Sales Analytics",
                "📥 Reports",
                "👤 Profile"
            ]
        else:  # CUSTOMER
            nav_options = [
                "🛍️ Home",
                "📦 Products",
                "🏷️ Categories",
                "📦 My Orders",
                "💡 Recommendations",
                "👤 Profile"
            ]

        # Horizontal Nav Bar
        chosen_page = st.radio(
            "ShopSense Navigation",
            nav_options,
            index=0,
            horizontal=True,
            label_visibility="collapsed",
            key="horizontal_main_navbar"
        )
        st.markdown("<hr style='margin: 8px 0 20px 0; border: none; border-top: 1px solid #e2e8f0;'/>", unsafe_allow_html=True)

        # Route to Selected Page
        token = st.session_state["token"]
        user_id = st.session_state.get("user_id", 1)

        if role == "CUSTOMER":
            if chosen_page in ("🛍️ Home", "📦 Products"):
                render_customer_catalog()
            elif chosen_page == "🏷️ Categories":
                render_customer_catalog()
            elif chosen_page == "📦 My Orders":
                render_customer_orders()
            elif chosen_page == "💡 Recommendations":
                st.markdown(_theme_module.render_top_navbar(user_name, role, current_theme), unsafe_allow_html=True)
                st.title("💡 Personalized Recommendations")
                _rec_ui.render_recommendation_intelligence_section(api, token, role, user_id, _theme_module, current_theme)
                st.markdown(_theme_module.render_trust_footer(), unsafe_allow_html=True)
            elif chosen_page == "👤 Profile":
                render_customer_profile()
        else:
            # ADMIN & VENDOR Views
            if chosen_page == "📊 Dashboard":
                render_dashboard_page()
            elif chosen_page in ("🏢 Vendors", "🏢 Vendors Management", "📋 Vendor Profiles"):
                render_vendors_page()
            elif chosen_page in ("📦 Products", "📦 My Products"):
                render_products_page()
            elif chosen_page == "🏷️ Categories":
                st.markdown(_theme_module.render_top_navbar(user_name, role, current_theme), unsafe_allow_html=True)
                st.title("🏷️ Marketplace Category Hierarchy")
                _inv_ui.render_category_tree_view(api, token)
                st.markdown(_theme_module.render_trust_footer(), unsafe_allow_html=True)
            elif chosen_page in ("📦 Orders", "💳 Transactions"):
                render_transactions_page()
            elif chosen_page in ("📋 Inventory", "📋 Inventory Intelligence"):
                render_inventory_page()
            elif chosen_page in ("📈 Analytics", "📈 Sales Analytics"):
                render_analytics_page()
            elif chosen_page == "👥 Customer Analytics":
                st.markdown(_theme_module.render_top_navbar(user_name, role, current_theme), unsafe_allow_html=True)
                st.title("👥 Customer Intelligence & Segmentation")
                _cust_ui.render_customer_intelligence_section(api, token, role, _theme_module, current_theme)
                st.markdown(_theme_module.render_trust_footer(), unsafe_allow_html=True)
            elif chosen_page == "💡 Recommendations":
                st.markdown(_theme_module.render_top_navbar(user_name, role, current_theme), unsafe_allow_html=True)
                st.title("💡 Recommendation Engine & Model Evaluation")
                _rec_ui.render_recommendation_intelligence_section(api, token, role, user_id, _theme_module, current_theme)
                st.markdown(_theme_module.render_trust_footer(), unsafe_allow_html=True)
            elif chosen_page == "📊 Business Intelligence":
                st.markdown(_theme_module.render_top_navbar(user_name, role, current_theme), unsafe_allow_html=True)
                _bi_ui.render_bi_dashboard(api, token, role, _theme_module, current_theme)
                st.markdown(_theme_module.render_trust_footer(), unsafe_allow_html=True)
            elif chosen_page == "📥 Reports":
                st.markdown(_theme_module.render_top_navbar(user_name, role, current_theme), unsafe_allow_html=True)
                _v_id = st.session_state.get("vendor_id") if role == "VENDOR" else None
                _reports_ui.render_reports_page(api, token, role, vendor_id=_v_id)
                st.markdown(_theme_module.render_trust_footer(), unsafe_allow_html=True)
            elif chosen_page == "🛡️ Data Validation":
                st.markdown(_theme_module.render_top_navbar(user_name, role, current_theme), unsafe_allow_html=True)
                _val_ui.render_validation_and_testing_page(api, token, _theme_module, current_theme)
                st.markdown(_theme_module.render_trust_footer(), unsafe_allow_html=True)
            elif chosen_page == "👤 Profile":
                render_customer_profile()

if __name__ == "__main__":
    main()

