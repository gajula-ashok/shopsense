import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def render_inventory_intelligence_section(api, token, role, theme_module, current_theme):
    """
    Renders the complete Milestone 2 Inventory Intelligence Suite:
    - 📊 Stock Overview (Database-backed SKU counts with proper emojis)
    - 🚨 Stock Alerts (Visual Indicators: 🟢 Available & Healthy, 🟡 Low Stock, 🔴 Out of Stock)
    - 🔄 Turnover Analytics (COGS / Avg Inventory, Fast/Slow moving)
    - 📈 ML Demand Forecast (Random Forest with MAE, RMSE, MAPE)
    - 📦 Replenishment (Urgency: 🚨 Critical, 🔴 High, 🟡 Medium, 🟢 Routine)
    - 🏢 Warehouses (Capacity and location utilization)
    - 🏷️ Category Tree (Hierarchical categories)
    - 📜 Stock Movements (Movement ledger and stock adjustments)
    """
    st.title("📋 Inventory Intelligence & Warehouse Tracking")

    tab_overview, tab_alerts, tab_turnover, tab_forecast, tab_replenish, tab_warehouses, tab_categories, tab_movements = st.tabs([
        "📊 Stock Overview",
        "🚨 Stock Alerts",
        "🔄 Turnover Analytics",
        "📈 ML Demand Forecast",
        "📦 Replenishment",
        "🏢 Warehouses",
        "🏷️ Category Tree",
        "📜 Stock Movements"
    ])

    # ----------------------------------------------------
    # TAB 1: Stock Overview & Quick Restock
    # ----------------------------------------------------
    with tab_overview:
        st.subheader("📊 Stock Overview")

        try:
            all_inv = api.get_inventory(token)
            if all_inv:
                df_all = pd.DataFrame(all_inv)
                # Ensure unique SKUs are counted
                unique_skus = df_all.drop_duplicates(subset=["product_id"])

                out_stock_cnt = len(unique_skus[unique_skus["current_stock"] == 0])
                low_stock_cnt = len(unique_skus[(unique_skus["current_stock"] > 0) & (unique_skus["current_stock"] <= unique_skus["reorder_level"])])
                available_cnt = len(unique_skus[unique_skus["current_stock"] > unique_skus["reorder_level"]])

                # Stock Overview Metric Cards with required indicators
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.error(f"🔴 **Out of Stock**: {out_stock_cnt} SKUs")
                with m2:
                    st.warning(f"🟡 **Low Stock**: {low_stock_cnt} SKUs")
                with m3:
                    st.success(f"🟢 **Available**: {available_cnt} SKUs")

                st.caption(f"Total Unique Product SKUs Monitored: **{len(unique_skus)} SKUs**")
            else:
                out_stock_cnt = low_stock_cnt = available_cnt = 0
        except Exception as e:
            st.error(f"Error computing stock overview: {e}")

        st.markdown("---")
        st.markdown("##### 📦 Multi-Vendor Inventory Catalog")
        status_filter = st.selectbox(
            "Filter by Stock Status",
            ["All", "🟢 Available & Healthy", "🟡 Low Stock", "🔴 Out of Stock"],
            key="inv_ov_status"
        )

        try:
            # Map emoji filter to backend filter
            filter_map = {
                "All": "All",
                "🟢 Available & Healthy": "IN STOCK",
                "🟡 Low Stock": "LOW STOCK",
                "🔴 Out of Stock": "OUT OF STOCK"
            }
            backend_filter = filter_map.get(status_filter, "All")
            inv_items = api.get_inventory(token, status=backend_filter)

            if inv_items:
                df_inv = pd.DataFrame(inv_items)

                # Map visual status display
                def map_stock_display(row):
                    stk = row["current_stock"]
                    r_lvl = row["reorder_level"]
                    if stk == 0:
                        return "🔴 Out of Stock"
                    elif stk <= r_lvl:
                        return "🟡 Low Stock"
                    else:
                        return "🟢 Available & Healthy"

                df_inv["Stock Status"] = df_inv.apply(map_stock_display, axis=1)

                st.dataframe(
                    df_inv[["inventory_id", "product_name", "vendor_name", "current_stock", "reorder_level", "warehouse", "Stock Status", "updated_at"]],
                    use_container_width=True,
                    hide_index=True
                )

                # Restock Level Adjustment
                with st.expander("📦 Adjust Product Stock / Reorder Threshold", expanded=False):
                    sel_item_id = st.selectbox(
                        "Select product to update",
                        [item["product_id"] for item in inv_items],
                        format_func=lambda x: f"Product #{x} - {[item['product_name'] for item in inv_items if item['product_id']==x][0]}",
                        key="inv_quick_sel"
                    )
                    curr_item = next(item for item in inv_items if item["product_id"] == sel_item_id)
                    u1, u2, u3 = st.columns(3)
                    with u1:
                        new_stock = st.number_input("Current Stock Count", value=int(curr_item["current_stock"]), min_value=0, step=1, key="inv_q_stock")
                    with u2:
                        new_reorder = st.number_input("Reorder Threshold", value=int(curr_item["reorder_level"]), min_value=0, step=1, key="inv_q_reorder")
                    with u3:
                        new_wh = st.text_input("Warehouse Location", value=str(curr_item["warehouse"]), key="inv_q_wh")

                    if st.button("Save Inventory Levels", type="primary", key="inv_q_btn"):
                        try:
                            api.update_inventory(token, sel_item_id, {
                                "current_stock": new_stock,
                                "reorder_level": new_reorder,
                                "warehouse": new_wh
                            })
                            st.success("Inventory updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Update failed: {e}")
            else:
                st.info("No inventory items found matching criteria.")
        except Exception as e:
            st.error(f"Error loading inventory items: {e}")

    # ----------------------------------------------------
    # TAB 2: Low Stock Alerts
    # ----------------------------------------------------
    with tab_alerts:
        st.subheader("🚨 Stock Alerts")
        st.markdown("""
        Visual stock health indicator:
        - 🟢 **Available & Healthy**
        - 🟡 **Low Stock** (Current Stock ≤ Reorder Threshold)
        - 🔴 **Out of Stock** (0 units remaining)
        """)
        try:
            alerts = api.get_inventory_alerts(token)
            if alerts:
                # Dynamic counts
                red_cnt = sum(1 for a in alerts if a["current_stock"] == 0)
                yellow_cnt = sum(1 for a in alerts if 0 < a["current_stock"] <= a["reorder_level"])
                green_cnt = sum(1 for a in alerts if a["current_stock"] > a["reorder_level"])

                c1, c2, c3 = st.columns(3)
                c1.error(f"🔴 **Out of Stock**: {red_cnt} SKUs")
                c2.warning(f"🟡 **Low Stock**: {yellow_cnt} SKUs")
                c3.success(f"🟢 **Available**: {green_cnt} SKUs")

                # Show visual notifications for critical items
                urgent_items = [a for a in alerts if a.get("notification")]
                if urgent_items:
                    with st.expander(f"⚠️ Active Critical Notifications ({len(urgent_items)})", expanded=True):
                        for item in urgent_items:
                            if item["current_stock"] == 0:
                                st.error(f"🔴 {item['notification']} (Warehouse: {item['warehouse']})")
                            else:
                                st.warning(f"🟡 {item['notification']} (Warehouse: {item['warehouse']})")

                df_alerts = pd.DataFrame(alerts)

                # Format Indicator & Status columns with visual emoji labels (no plain RED/GREEN/YELLOW)
                def map_alert_indicator(row):
                    stk = row["current_stock"]
                    r_lvl = row["reorder_level"]
                    if stk == 0:
                        return "🔴 Out of Stock"
                    elif stk <= r_lvl:
                        return "🟡 Low Stock"
                    else:
                        return "🟢 Available & Healthy"

                df_alerts["Stock Health Status"] = df_alerts.apply(map_alert_indicator, axis=1)

                st.dataframe(
                    df_alerts[["Stock Health Status", "product_name", "vendor_name", "current_stock", "reorder_level", "warehouse"]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No alert records found.")
        except Exception as e:
            st.error(f"Error loading stock alerts: {e}")

    # ----------------------------------------------------
    # TAB 3: Inventory Turnover Analytics
    # ----------------------------------------------------
    with tab_turnover:
        st.subheader("🔄 Turnover Analytics")
        st.markdown(r"$$\text{Inventory Turnover} = \frac{\text{Cost of Goods Sold (COGS)}}{\text{Average Inventory Value}}$$")
        try:
            turnover_data = api.get_inventory_turnover(token)
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Overall Marketplace Turnover", f"{turnover_data.get('overall_turnover_rate', 0.0):.2f}x")
            with m2:
                st.metric("Total COGS Realized", f"₹{turnover_data.get('total_cogs', 0.0):,.2f}")
            with m3:
                st.metric("Average Inventory Holding", f"₹{turnover_data.get('average_inventory_value', 0.0):,.2f}")

            st.markdown("---")
            col_fast, col_slow = st.columns(2)
            with col_fast:
                st.markdown("##### ⚡ Fast-Moving Products (High Velocity)")
                fast_items = turnover_data.get("fast_moving_products", [])
                if fast_items:
                    st.dataframe(pd.DataFrame(fast_items)[["product_name", "vendor_name", "turnover_rate", "cogs"]], use_container_width=True, hide_index=True)
                else:
                    st.caption("No products currently classified as fast-moving.")

            with col_slow:
                st.markdown("##### 🐢 Slow-Moving Products (Capital Tied Up)")
                slow_items = turnover_data.get("slow_moving_products", [])
                if slow_items:
                    st.dataframe(pd.DataFrame(slow_items)[["product_name", "vendor_name", "turnover_rate", "cogs"]], use_container_width=True, hide_index=True)
                else:
                    st.caption("No products currently classified as slow-moving.")

            st.markdown("##### 🏢 Vendor-Wise Inventory Turnover Performance")
            v_perf = turnover_data.get("vendor_performance", [])
            if v_perf:
                df_vperf = pd.DataFrame(v_perf)
                fig_v = px.bar(
                    df_vperf.head(20),
                    x="vendor_name",
                    y="turnover_rate",
                    text_auto=True,
                    color="turnover_rate",
                    title="Vendor Inventory Velocity (Turnover Rate - Top 20)",
                    labels={"turnover_rate": "Turnover Ratio", "vendor_name": "Vendor"}
                )
                fig_v.update_layout(template="plotly_white", xaxis_tickangle=-45)
                st.plotly_chart(fig_v, use_container_width=True)
                st.dataframe(df_vperf, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Error loading inventory turnover: {e}")

    # ----------------------------------------------------
    # TAB 4: ML Demand Forecasting
    # ----------------------------------------------------
    with tab_forecast:
        st.subheader("📈 ML Demand Forecast")
        st.caption("Trained Random Forest Regressor predicting future monthly demand based on historical transaction volume, quarter, month, and seasonal trend dynamics.")
        try:
            with st.spinner("Training Random Forest Forecasting Engine..."):
                forecast_res = api.get_inventory_forecast(token)

            eval_metrics = forecast_res.get("evaluation", {})
            f1, f2, f3, f4 = st.columns(4)
            with f1:
                st.metric("Model Architecture", eval_metrics.get("model_name", "Random Forest"))
            with f2:
                st.metric("MAE (Mean Abs Error)", f"{eval_metrics.get('mae', 0.0):.2f} units")
            with f3:
                st.metric("RMSE", f"{eval_metrics.get('rmse', 0.0):.2f}")
            with f4:
                acc = eval_metrics.get("accuracy_percentage", 0.0)
                st.metric("Forecasting Accuracy", f"{acc:.1f}%")

            forecasts = forecast_res.get("forecasts", [])
            if forecasts:
                df_fc = pd.DataFrame(forecasts)
                # Comparison Chart
                fig_fc = px.bar(
                    df_fc.head(15),
                    x="product_name",
                    y="predicted_demand_next_month",
                    color="category",
                    text_auto=True,
                    title="Next Month Predicted Demand by Product (Sample 15)",
                    labels={"predicted_demand_next_month": "Predicted Units", "product_name": "Product"}
                )
                fig_fc.update_layout(template="plotly_white", xaxis_tickangle=-45)
                st.plotly_chart(fig_fc, use_container_width=True)

                st.markdown(f"##### All 500 Product Demand Predictions (Showing {len(df_fc)} SKUs)")
                st.dataframe(
                    df_fc[["product_id", "product_name", "category", "historical_sales_total", "predicted_demand_next_month"]],
                    use_container_width=True,
                    hide_index=True
                )
        except Exception as e:
            st.error(f"Error loading demand forecast: {e}")

    # ----------------------------------------------------
    # TAB 5: Replenishment Recommendations
    # ----------------------------------------------------
    with tab_replenish:
        st.subheader("📦 Automated Replenishment Recommendation Engine")
        st.markdown(r"$$\text{Recommended Reorder Quantity} = \max(0, \text{Target Stock Level} - \text{Current Stock})$$")
        try:
            replenish_items = api.get_replenishment_recommendations(token)
            if replenish_items:
                df_rep = pd.DataFrame(replenish_items)

                r_crit = len(df_rep[df_rep["urgency"] == "CRITICAL"])
                r_high = len(df_rep[df_rep["urgency"] == "HIGH"])
                r_med = len(df_rep[df_rep["urgency"].isin(["MEDIUM", "ROUTINE"])])
                r_routine = len(df_rep[df_rep["urgency"] == "LOW"])

                # Dynamic Summary Metrics with Required Emoji Format
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.error(f"🚨 **Critical Restock**: {r_crit} Products")
                with c2:
                    st.warning(f"🔴 **High Priority**: {r_high} Products")
                with c3:
                    st.info(f"🟡 **Medium/Routine**: {r_med} Products")

                # Map Urgency Visual Indicators (no plain text without emoji)
                urgency_display_map = {
                    "CRITICAL": "🚨 Critical",
                    "HIGH": "🔴 High",
                    "MEDIUM": "🟡 Medium",
                    "LOW": "🟢 Routine",
                    "ROUTINE": "🟢 Routine"
                }
                df_rep["Urgency"] = df_rep["urgency"].map(lambda u: urgency_display_map.get(u, f"🟢 {u}"))
                df_rep["Vendor"] = df_rep["preferred_vendor_name"]
                df_rep["Action"] = "Review & Order"

                st.dataframe(
                    df_rep[["product_id", "product_name", "Vendor", "current_stock", "reorder_level", "forecast_demand", "target_stock_level", "recommended_reorder_qty", "Urgency"]],
                    use_container_width=True,
                    hide_index=True
                )

                # Authorized User Review and Restock Action Panel
                st.markdown("---")
                st.markdown("##### 🛒 Authorized Replenishment Review & Purchase Order")
                st.caption("Review replenishment recommendation details and authorize purchase orders with selected vendors.")

                sel_rep_p = st.selectbox(
                    "Select Product to Review Recommendation:",
                    options=[r["product_id"] for r in replenish_items],
                    format_func=lambda x: f"Product #{x} - {[r['product_name'] for r in replenish_items if r['product_id']==x][0]} (Vendor: {[r['preferred_vendor_name'] for r in replenish_items if r['product_id']==x][0]} | Suggested: {[r['recommended_reorder_qty'] for r in replenish_items if r['product_id']==x][0]} units)",
                    key="rep_order_sel"
                )
                chosen_rep = next(r for r in replenish_items if r["product_id"] == sel_rep_p)

                col_det1, col_det2 = st.columns(2)
                with col_det1:
                    st.write(f"**Product:** {chosen_rep['product_name']}")
                    st.write(f"**Preferred Vendor:** {chosen_rep['preferred_vendor_name']}")
                    st.write(f"**Current Stock:** {chosen_rep['current_stock']} units")
                    st.write(f"**Reorder Threshold:** {chosen_rep['reorder_level']} units")
                with col_det2:
                    st.write(f"**Forecast Demand (30 Days):** {chosen_rep['forecast_demand']} units")
                    st.write(f"**Target Stock Level:** {chosen_rep['target_stock_level']} units")
                    st.write(f"**Suggested Reorder:** {chosen_rep['recommended_reorder_qty']} units")
                    st.write(f"**Priority:** {urgency_display_map.get(chosen_rep['urgency'], chosen_rep['urgency'])}")

                order_qty = st.number_input(
                    "Authorized Order Quantity to Deliver:",
                    min_value=1,
                    value=max(1, chosen_rep["recommended_reorder_qty"]),
                    key="rep_order_qty"
                )
                if st.button("📝 Authorize & Execute Purchase Order", type="primary", key="rep_btn_confirm"):
                    try:
                        api.record_stock_movement(token, {
                            "product_id": sel_rep_p,
                            "quantity": order_qty,
                            "movement_type": "STOCK_IN",
                            "reference": f"PO-AUTH-{sel_rep_p}-{datetime.now().strftime('%Y%m%d')}",
                            "warehouse": "Central Distribution Hub (Delhi NCR)"
                        })
                        st.success(f"Purchase Order authorized! Added {order_qty} units of '{chosen_rep['product_name']}' from vendor '{chosen_rep['preferred_vendor_name']}'. Live stock updated.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Restock authorization failed: {e}")
            else:
                st.info("No replenishment items currently suggested.")
        except Exception as e:
            st.error(f"Error loading replenishment recommendations: {e}")

    # ----------------------------------------------------
    # TAB 6: Warehouse Management
    # ----------------------------------------------------
    with tab_warehouses:
        st.subheader("🏢 Warehouses")
        if role == "ADMIN":
            with st.expander("➕ Register New Warehouse Location", expanded=False):
                with st.form("add_wh_form"):
                    w_name = st.text_input("Warehouse Name *", placeholder="e.g. Northern Express Logistics")
                    w_loc = st.text_input("City, State / Geographic Location *", placeholder="e.g. Seattle, WA")
                    w_cap = st.number_input("Max Storage Capacity (units)", min_value=100, value=15000, step=500)
                    w_ph = st.text_input("Dispatch Contact Phone", placeholder="e.g. 206-555-0199")
                    if st.form_submit_button("Register Warehouse", type="primary"):
                        if not w_name or not w_loc:
                            st.error("Warehouse name and location are required.")
                        else:
                            try:
                                api.create_warehouse(token, {
                                    "warehouse_name": w_name,
                                    "location": w_loc,
                                    "capacity": w_cap,
                                    "contact_phone": w_ph,
                                    "is_active": True
                                })
                                st.success(f"Warehouse '{w_name}' successfully added!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Warehouse creation failed: {e}")

        try:
            wh_list = api.get_warehouses(token)
            if wh_list:
                df_wh = pd.DataFrame(wh_list)
                st.dataframe(
                    df_wh[["warehouse_id", "warehouse_name", "location", "capacity", "total_units_stored", "unique_products_stored", "utilization_percentage", "contact_phone"]],
                    use_container_width=True,
                    hide_index=True
                )

                # Warehouse Capacity Chart
                fig_wh = px.bar(
                    df_wh,
                    x="warehouse_name",
                    y=["total_units_stored", "capacity"],
                    barmode="group",
                    title="Warehouse Current Units vs. Total Capacity",
                    labels={"value": "Units", "warehouse_name": "Warehouse"}
                )
                fig_wh.update_layout(template="plotly_white")
                st.plotly_chart(fig_wh, use_container_width=True)
            else:
                st.info("No warehouses registered.")
        except Exception as e:
            st.error(f"Error loading warehouses: {e}")

    # ----------------------------------------------------
    # TAB 7: Category Hierarchy
    # ----------------------------------------------------
    with tab_categories:
        st.subheader("🏷️ Category Tree")
        if role == "ADMIN":
            with st.expander("➕ Create Category or Subcategory", expanded=False):
                with st.form("add_cat_form"):
                    c_name = st.text_input("Category Name *", placeholder="e.g. Smart Wearables")
                    c_desc = st.text_input("Category Description", placeholder="e.g. Fitness trackers, smartbands")
                    all_cats = api.get_categories(token)
                    parent_opts = {0: "None (Top-Level Category)"}
                    for c in all_cats:
                        parent_opts[c["category_id"]] = c["category_name"]
                    sel_parent = st.selectbox("Parent Category", options=list(parent_opts.keys()), format_func=lambda x: parent_opts[x])
                    if st.form_submit_button("Create Category", type="primary"):
                        if not c_name:
                            st.error("Category name is required.")
                        else:
                            try:
                                api.create_category(token, {
                                    "category_name": c_name,
                                    "parent_id": None if sel_parent == 0 else sel_parent,
                                    "description": c_desc
                                })
                                st.success(f"Category '{c_name}' created!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Category creation failed: {e}")

        try:
            cats = api.get_categories(token)
            if cats:
                df_cats = pd.DataFrame(cats)
                st.dataframe(
                    df_cats[["category_id", "category_name", "parent_name", "product_count", "description"]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No categories registered.")
        except Exception as e:
            st.error(f"Error loading categories: {e}")

    # ----------------------------------------------------
    # TAB 8: Stock Movements Ledger
    # ----------------------------------------------------
    with tab_movements:
        st.subheader("📜 Stock Movements")
        with st.expander("➕ Record Manual Stock Movement (In / Out)", expanded=False):
            with st.form("add_movement_form"):
                prods = api.get_products(token)
                p_opts = {p["product_id"]: f"{p['product_name']} (Current Stock: {p['stock']})" for p in prods}
                m_pid = st.selectbox("Select Product", options=list(p_opts.keys()), format_func=lambda x: p_opts[x])
                m_qty = st.number_input("Quantity (+ for addition, - for reduction)", value=10, step=1)
                m_type = st.selectbox("Movement Type", ["STOCK_IN", "STOCK_OUT", "ADJUSTMENT", "RETURN", "RESTOCK"])
                m_ref = st.text_input("Reference / Reason", placeholder="e.g. Supplier Shipment #849")
                m_wh = st.text_input("Warehouse Location", value="Central Distribution Hub (Delhi NCR)")
                if st.form_submit_button("Record Movement", type="primary"):
                    try:
                        api.record_stock_movement(token, {
                            "product_id": m_pid,
                            "quantity": m_qty,
                            "movement_type": m_type,
                            "reference": m_ref,
                            "warehouse": m_wh
                        })
                        st.success("Stock movement recorded and live inventory updated!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to record movement: {e}")

        try:
            movements = api.get_stock_movements(token)
            if movements:
                st.dataframe(
                    pd.DataFrame(movements)[["movement_id", "product_name", "quantity", "movement_type", "warehouse", "reference", "created_at"]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No stock movements recorded yet.")
        except Exception as e:
            st.error(f"Error loading stock movements: {e}")

def render_category_tree_view(api, token):
    """Standalone category hierarchy renderer for top navbar route."""
    st.markdown("Explore and manage marketplace categories and catalog hierarchies.")
    with st.expander("➕ Create Category or Subcategory", expanded=False):
        with st.form("standalone_add_cat_form"):
            c_name = st.text_input("Category Name *", placeholder="e.g. Smart Wearables")
            c_desc = st.text_input("Category Description", placeholder="e.g. Fitness trackers, smartbands")
            all_cats = api.get_categories(token)
            parent_opts = {0: "None (Top-Level Category)"}
            for c in all_cats:
                parent_opts[c["category_id"]] = c["category_name"]
            sel_parent = st.selectbox("Parent Category", options=list(parent_opts.keys()), format_func=lambda x: parent_opts[x])
            if st.form_submit_button("Create Category", type="primary"):
                if not c_name:
                    st.error("Category name is required.")
                else:
                    try:
                        api.create_category(token, {
                            "category_name": c_name,
                            "parent_id": None if sel_parent == 0 else sel_parent,
                            "description": c_desc
                        })
                        st.success(f"Category '{c_name}' created!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Category creation failed: {e}")

    try:
        cats = api.get_categories(token)
        if cats:
            df_cats = pd.DataFrame(cats)
            st.dataframe(
                df_cats[["category_id", "category_name", "parent_name", "product_count", "description"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No categories registered.")
    except Exception as e:
        st.error(f"Error loading categories: {e}")
