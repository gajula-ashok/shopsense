import streamlit as st
import pandas as pd
from datetime import datetime

def render_vendor_applications_page(api, token, current_theme):
    """
    Admin Dashboard – Vendor Application Management Interface
    - Summary Cards: Total Applications, Pending Review, Approved, More Info Needed, Rejected
    - Application Status Filter Tabs
    - Multi-field Search (Business Name, Vendor Name, Email, Vendor ID) + Reset
    - Vendor Application Table with Review Actions
    - Detailed Review Modal / Expandable Panel (Approve, Request Info, Reject with notes)
    """
    st.title("📋 Vendor Applications")
    st.markdown("Review, verify, and approve seller applications across the marketplace.")

    # 1. Fetch All Applications to Compute Summary Cards
    try:
        all_vendors = api.get_vendors(token)
    except Exception as e:
        st.error(f"Error fetching vendor applications: {e}")
        return

    # Count by application status
    total_apps = len(all_vendors)
    pending_count = sum(1 for v in all_vendors if (v.get("application_status") == "PENDING" or (not v.get("application_status") and v.get("status") == "PENDING")))
    approved_count = sum(1 for v in all_vendors if v.get("application_status") == "APPROVED" or (not v.get("application_status") and v.get("status") == "ACTIVE"))
    info_needed_count = sum(1 for v in all_vendors if v.get("application_status") == "MORE_INFO_NEEDED")
    rejected_count = sum(1 for v in all_vendors if v.get("application_status") == "REJECTED" or (not v.get("application_status") and v.get("status") == "SUSPENDED"))

    # 2. Summary Cards Display
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        with st.container(border=True):
            st.markdown("<div style='font-size:0.85rem; color:#666; font-weight:600;'>📁 Total Applications</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:1.8rem; font-weight:800; color:#1e293b;'>{total_apps}</div>", unsafe_allow_html=True)
            st.caption("All registered seller submissions")
    with c2:
        with st.container(border=True):
            st.markdown("<div style='font-size:0.85rem; color:#d97706; font-weight:600;'>⏳ Pending Review</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:1.8rem; font-weight:800; color:#d97706;'>{pending_count}</div>", unsafe_allow_html=True)
            st.caption("Awaiting verification")
    with c3:
        with st.container(border=True):
            st.markdown("<div style='font-size:0.85rem; color:#16a34a; font-weight:600;'>✅ Approved</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:1.8rem; font-weight:800; color:#16a34a;'>{approved_count}</div>", unsafe_allow_html=True)
            st.caption("Active marketplace sellers")
    with c4:
        with st.container(border=True):
            st.markdown("<div style='font-size:0.85rem; color:#2563eb; font-weight:600;'>ℹ️ More Info Needed</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:1.8rem; font-weight:800; color:#2563eb;'>{info_needed_count}</div>", unsafe_allow_html=True)
            st.caption("Action requested from seller")
    with c5:
        with st.container(border=True):
            st.markdown("<div style='font-size:0.85rem; color:#dc2626; font-weight:600;'>❌ Rejected</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:1.8rem; font-weight:800; color:#dc2626;'>{rejected_count}</div>", unsafe_allow_html=True)
            st.caption("Applications declined")

    st.markdown("---")

    # 3. Application Filter Tabs
    tab_all, tab_pending, tab_approved, tab_info, tab_rejected = st.tabs([
        f"All Applications ({total_apps})",
        f"⏳ Pending ({pending_count})",
        f"✅ Approved ({approved_count})",
        f"ℹ️ More Info Needed ({info_needed_count})",
        f"❌ Rejected ({rejected_count})"
    ])

    filter_status = "All"
    # Manage active tab state
    tab_indices = {
        "All Applications": "All",
        "Pending": "PENDING",
        "Approved": "APPROVED",
        "More Info Needed": "MORE_INFO_NEEDED",
        "Rejected": "REJECTED"
    }

    # 4. Search and Reset Bar
    col_search, col_btn_s, col_btn_r = st.columns([4, 1, 1])
    with col_search:
        search_query = st.text_input(
            "Search Applications",
            placeholder="🔍 Search by Business Name, Vendor Name, Email, or Vendor ID...",
            label_visibility="collapsed",
            key="v_app_search_input"
        ).strip()
    with col_btn_s:
        btn_search = st.button("🔍 Search", use_container_width=True)
    with col_btn_r:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state["v_app_search_input"] = ""
            search_query = ""
            st.rerun()

    # 5. Render Filtered Table based on Selected Tab & Search
    def render_applications_list(target_status: str):
        filtered = all_vendors
        if target_status != "All":
            filtered = [
                v for v in filtered 
                if (v.get("application_status") == target_status) or 
                   (not v.get("application_status") and (
                       (target_status == "APPROVED" and v.get("status") == "ACTIVE") or
                       (target_status == "PENDING" and v.get("status") == "PENDING") or
                       (target_status == "REJECTED" and v.get("status") == "SUSPENDED")
                   ))
            ]

        if search_query:
            sq = search_query.lower()
            filtered = [
                v for v in filtered
                if sq in v.get("business_name", "").lower()
                or sq in v.get("owner_name", "").lower()
                or sq in v.get("email", "").lower()
                or sq in str(v.get("vendor_id", "")).lower()
                or sq in v.get("category", "").lower()
                or sq in str(v.get("city", "")).lower()
            ]

        if not filtered:
            st.info(f"No vendor applications found for '{target_status}' matching the search criteria.")
            return

        st.markdown(f"**Showing {len(filtered)} Applications**")

        # Table Display
        table_rows = []
        for v in filtered:
            app_st = v.get("application_status") or ("APPROVED" if v.get("status") == "ACTIVE" else "PENDING")
            badge_map = {
                "APPROVED": "🟢 Approved",
                "PENDING": "🟡 Pending Review",
                "MORE_INFO_NEEDED": "🔵 Info Needed",
                "REJECTED": "🔴 Rejected"
            }
            sub_date = v.get("created_at", "")[:10] if v.get("created_at") else "2026-10-30"
            loc = f"{v.get('city', 'N/A')}, {v.get('state', '')}" if v.get("city") else "Pan-India"
            tax = v.get("tax_id") or f"GSTIN{v['vendor_id']:02d}AAACB"

            table_rows.append({
                "Vendor ID": f"#{v['vendor_id']}",
                "Vendor & Business": f"{v['business_name']} ({v['owner_name']})",
                "Category": v["category"],
                "Contact": f"{v['email']} | {v['phone']}",
                "Location & Tax ID": f"{loc} • {tax}",
                "Status": badge_map.get(app_st, app_st),
                "Submitted Date": sub_date
            })

        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

        # 6. Detailed Application Review Section
        st.markdown("---")
        st.subheader("🔍 Review & Process Vendor Application")
        
        sel_v_id = st.selectbox(
            "Select Vendor Application to Inspect & Decide:",
            options=[v["vendor_id"] for v in filtered],
            format_func=lambda x: f"Vendor #{x} — {[v['business_name'] for v in filtered if v['vendor_id']==x][0]} ({[v.get('application_status','APPROVED') for v in filtered if v['vendor_id']==x][0]})",
            key=f"v_app_sel_{target_status}"
        )

        selected_vendor = next(v for v in filtered if v["vendor_id"] == sel_v_id)

        with st.container(border=True):
            st.markdown(f"### 🏢 {selected_vendor['business_name']}")
            st.caption(f"Application Reference: **APP-VND-{selected_vendor['vendor_id']:04d}** • Category: **{selected_vendor['category']}**")

            r1, r2, r3 = st.columns(3)
            with r1:
                st.markdown("**👤 Vendor Representative**")
                st.write(f"Name: **{selected_vendor['owner_name']}**")
                st.write(f"Email: `{selected_vendor['email']}`")
                st.write(f"Phone: `{selected_vendor['phone']}`")
            with r2:
                st.markdown("**📍 Business Location & Tax ID**")
                st.write(f"Address: {selected_vendor.get('business_address', 'N/A')}")
                st.write(f"City / State: {selected_vendor.get('city', 'Mumbai')}, {selected_vendor.get('state', 'Maharashtra')}")
                st.write(f"Pincode: `{selected_vendor.get('pincode', '400001')}`")
                st.write(f"GSTIN / Tax ID: `{selected_vendor.get('tax_id', 'GSTIN27AAACB1001C1Z1')}`")
            with r3:
                st.markdown("**📊 Application Status & Audit**")
                curr_app_st = selected_vendor.get("application_status", "APPROVED")
                st.write(f"Operational Status: **{selected_vendor['status']}**")
                st.write(f"Application Status: **{curr_app_st}**")
                st.write(f"Platform Commission: **{selected_vendor['commission_rate']}%**")
                st.write(f"Submitted Date: **{selected_vendor.get('created_at', '')[:10]}**")

            st.markdown("**📝 Current Review Notes & Activity Log:**")
            st.info(selected_vendor.get("review_notes") or "Application under standard verification.")

            st.markdown("---")
            st.markdown("##### ⚙️ Administrator Review Action")
            admin_notes = st.text_area(
                "Reviewer Comments / Clarification Notes:",
                placeholder="Enter feedback, approval notes, or reasons for rejection / information request...",
                key=f"notes_{target_status}_{selected_vendor['vendor_id']}"
            )

            btn_col1, btn_col2, btn_col3 = st.columns(3)

            with btn_col1:
                if st.button("✅ Approve Application", type="primary", use_container_width=True, key=f"btn_app_{target_status}_{selected_vendor['vendor_id']}"):
                    try:
                        api.review_vendor_application(token, selected_vendor["vendor_id"], "APPROVE", admin_notes)
                        st.success(f"Vendor #{selected_vendor['vendor_id']} ({selected_vendor['business_name']}) has been APPROVED and activated!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Approval failed: {e}")

            with btn_col2:
                if st.button("ℹ️ Request More Information", use_container_width=True, key=f"btn_req_{target_status}_{selected_vendor['vendor_id']}"):
                    if not admin_notes.strip():
                        st.warning("Please specify what additional information is required in the reviewer comments above.")
                    else:
                        try:
                            api.review_vendor_application(token, selected_vendor["vendor_id"], "REQUEST_INFO", admin_notes)
                            st.info(f"Clarification request recorded for Vendor #{selected_vendor['vendor_id']}.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Action failed: {e}")

            with btn_col3:
                if st.button("❌ Reject Application", type="secondary", use_container_width=True, key=f"btn_rej_{target_status}_{selected_vendor['vendor_id']}"):
                    if not admin_notes.strip():
                        st.warning("Please provide a reason for rejection in the reviewer comments above.")
                    else:
                        try:
                            api.review_vendor_application(token, selected_vendor["vendor_id"], "REJECT", admin_notes)
                            st.error(f"Vendor #{selected_vendor['vendor_id']} application has been REJECTED and account suspended.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Rejection failed: {e}")

    with tab_all:
        render_applications_list("All")
    with tab_pending:
        render_applications_list("PENDING")
    with tab_approved:
        render_applications_list("APPROVED")
    with tab_info:
        render_applications_list("MORE_INFO_NEEDED")
    with tab_rejected:
        render_applications_list("REJECTED")
