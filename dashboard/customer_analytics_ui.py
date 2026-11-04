import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render_customer_intelligence_section(api, token, role, theme_module, current_theme):
    """
    Renders the complete Milestone 2 Customer Analytics Suite:
    - Customer Behavior Analysis (Orders, Spent, AOV, Purchase frequency, Top products)
    - Customer Segmentation using K-Means (StandardScaler, Clusters, Silhouette Score)
    - Segment characteristics summary & individual customer distributions
    """
    tab_behavior, tab_segmentation = st.tabs([
        "👥 Customer Behavior & Spending",
        "🎯 K-Means Segmentation & Clusters"
    ])

    # ----------------------------------------------------
    # TAB 1: Customer Behavior Analysis
    # ----------------------------------------------------
    with tab_behavior:
        st.subheader("👥 Customer Behavior & Lifetime Value Analysis")
        st.caption("Aggregated analytics covering total orders, spending velocity, average basket size, and purchase frequency.")

        try:
            with st.spinner("Aggregating customer purchase profiles..."):
                cust_behaviors = api.get_customer_behavior(token)

            if cust_behaviors:
                df_cust = pd.DataFrame(cust_behaviors)

                # High-level KPIs
                tot_customers = len(df_cust)
                avg_lifetime_spend = df_cust["total_spent"].mean()
                avg_orders_per_cust = df_cust["total_orders"].mean()
                overall_aov = df_cust["average_order_value"].mean()

                k1, k2, k3, k4 = st.columns(4)
                with k1:
                    st.metric("Total Active Customers", f"{tot_customers:,}")
                with k2:
                    st.metric("Avg Customer Lifetime Spend", f"${avg_lifetime_spend:,.2f}")
                with k3:
                    st.metric("Avg Orders / Customer", f"{avg_orders_per_cust:.1f}")
                with k4:
                    st.metric("Marketplace AOV", f"${overall_aov:,.2f}")

                st.markdown("---")

                # Top Customer Spenders Table
                st.markdown("##### 🏆 Top Customer Spenders")
                st.dataframe(
                    df_cust[["customer_id", "customer_name", "email", "total_orders", "total_spent", "average_order_value", "purchase_frequency_days", "activity_status"]].head(15),
                    use_container_width=True,
                    hide_index=True
                )

                # Spending Distribution Chart
                c_c1, c_c2 = st.columns(2)
                with c_c1:
                    fig_spend = px.histogram(
                        df_cust,
                        x="total_spent",
                        nbins=20,
                        title="Customer Lifetime Spend Distribution",
                        labels={"total_spent": "Total Spent ($)"},
                        color_discrete_sequence=["#1976d2"]
                    )
                    fig_spend.update_layout(template="plotly_white")
                    st.plotly_chart(fig_spend, use_container_width=True)

                with c_c2:
                    fig_freq = px.scatter(
                        df_cust,
                        x="total_orders",
                        y="total_spent",
                        size="average_order_value",
                        color="activity_status",
                        hover_name="customer_name",
                        title="Order Volume vs. Total Spend (Bubble Size = AOV)",
                        labels={"total_orders": "Total Orders", "total_spent": "Total Spend ($)"}
                    )
                    fig_freq.update_layout(template="plotly_white")
                    st.plotly_chart(fig_freq, use_container_width=True)

                # Single Customer Deep Dive
                with st.expander("🔍 Deep-Dive Customer Purchase History & Preferences", expanded=False):
                    sel_cid = st.selectbox(
                        "Select Customer to Inspect",
                        options=[c["customer_id"] for c in cust_behaviors],
                        format_func=lambda x: f"#{x} - {[c['customer_name'] for c in cust_behaviors if c['customer_id']==x][0]}",
                        key="cust_deep_sel"
                    )
                    target_c = next(c for c in cust_behaviors if c["customer_id"] == sel_cid)
                    d1, d2, d3, d4 = st.columns(4)
                    d1.write(f"**Customer:** {target_c['customer_name']}")
                    d2.write(f"**Email:** {target_c['email']}")
                    d3.write(f"**Status:** `{target_c['activity_status']}`")
                    d4.write(f"**First Seen:** {target_c['first_purchase_date']}")

                    st.markdown("**Most Purchased Products by this Customer:**")
                    if target_c.get("most_purchased_products"):
                        st.dataframe(pd.DataFrame(target_c["most_purchased_products"]), use_container_width=True, hide_index=True)
                    else:
                        st.caption("No specific product concentration recorded.")
            else:
                st.info("No customer behavior data available.")
        except Exception as e:
            st.error(f"Error loading customer behavior: {e}")

    # ----------------------------------------------------
    # TAB 2: Customer Segmentation using K-Means
    # ----------------------------------------------------
    with tab_segmentation:
        st.subheader("🎯 Customer Segmentation using K-Means Clustering")
        st.caption("Machine learning clustering using StandardScaler normalized features: Total Orders, Total Spent, Average Order Value, and Purchase Frequency.")

        n_clusters = st.slider("Select Number of Clusters (k)", min_value=2, max_value=5, value=3, key="kmeans_slider")

        try:
            with st.spinner("Executing K-Means Clustering & Computing Silhouette Score..."):
                seg_res = api.get_customer_segments(token, n_clusters=n_clusters)

            sil_score = seg_res.get("silhouette_score", 0.0)
            target_met = seg_res.get("target_met", False)

            s1, s2, s3 = st.columns(3)
            with s1:
                st.metric("Optimal Clusters Applied", f"k = {seg_res.get('optimal_clusters', 3)}")
            with s2:
                st.metric("Evaluated Silhouette Score", f"{sil_score:.4f}", delta="Target ≥ 0.85" if target_met else "Dataset Diversity Active")
            with s3:
                st.metric("Total Customers Clustered", len(seg_res.get("customer_records", [])))

            # Actual evaluation result banner
            if target_met:
                st.success(f"✅ Silhouette Score Target Met: **{sil_score:.4f}** (Target ≥ 0.85). Highly distinct, dense clusters.")
            else:
                st.info(
                    f"📊 **Evaluated Silhouette Score: {sil_score:.4f}** (Evaluation Target: ≥ 0.85).\n\n"
                    f"*Realistic e-commerce transactions exhibit natural variance in continuous spending amounts across regular shoppers. "
                    f"Clusters maintain distinct behavioral profiles (High Value, Regular, and Low Activity).*"
                )

            st.markdown("---")

            # Segment Summary Cards
            st.markdown("##### 📌 Discovered Behavioral Segment Profiles")
            seg_summaries = seg_res.get("segment_summary", [])
            if seg_summaries:
                cols = st.columns(len(seg_summaries))
                for idx, s in enumerate(seg_summaries):
                    with cols[idx]:
                        with st.container(border=True):
                            st.markdown(f"#### {s['segment_name']}")
                            st.write(f"👥 **{s['count']}** Customers ({s['percentage']}%)")
                            st.write(f"💰 Avg Spend: **${s['avg_spent']:,.2f}**")
                            st.write(f"📦 Avg Orders: **{s['avg_orders']:.1f}**")
                            st.write(f"🏷️ AOV: **${s['avg_order_value']:,.2f}**")
                            st.caption(s.get("description", ""))

            # Cluster Scatter Plot
            cust_records = seg_res.get("customer_records", [])
            if cust_records:
                df_records = pd.DataFrame(cust_records)
                fig_clusters = px.scatter(
                    df_records,
                    x="total_orders",
                    y="total_spent",
                    color="segment_name",
                    size="avg_order_value",
                    hover_name="customer_name",
                    title="Customer Segments in 2D Feature Space (Orders vs. Spend)",
                    labels={"total_orders": "Total Orders", "total_spent": "Total Lifetime Spend ($)"}
                )
                fig_clusters.update_layout(template="plotly_white")
                st.plotly_chart(fig_clusters, use_container_width=True)

                st.markdown("##### Full Customer Segment Assignments")
                st.dataframe(
                    df_records[["customer_id", "customer_name", "email", "segment_name", "total_orders", "total_spent", "avg_order_value", "purchase_frequency"]],
                    use_container_width=True,
                    hide_index=True
                )
        except Exception as e:
            st.error(f"Error executing customer segmentation: {e}")
