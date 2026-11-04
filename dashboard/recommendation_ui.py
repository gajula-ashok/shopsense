import streamlit as st
import pandas as pd
import plotly.express as px

def render_recommendation_intelligence_section(api, token, role, user_id, theme_module, current_theme):
    """
    Renders the Recommendation Engine Suite:
    - Customer View: Clean, authentic e-commerce recommendations (12 curated products, no technical sliders/tables)
    - Admin View: Full platform model inspection with customer selector, scoring table, and Precision@K evaluation
    """
    if role == "CUSTOMER":
        # Realistic e-commerce customer experience: fixed 12 curated recommendations
        sel_cid = user_id or 1
        top_n = 12

        st.markdown(
            """
            <div style="background: linear-gradient(135deg, rgba(40,116,240,0.06) 0%, rgba(251,100,27,0.06) 100%); padding: 18px 24px; border-radius: 12px; margin-bottom: 22px; border: 1px solid var(--ss-border, #e0e0e0);">
                <div style="font-size: 1.35rem; font-weight: 800; color: var(--ss-text-main, #212121);">
                    ✨ Recommended For You
                </div>
                <div style="font-size: 0.88rem; color: var(--ss-text-muted, #666); margin-top: 4px;">
                    Handpicked products tailored to your browsing and shopping taste across India's largest multi-vendor catalog.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        try:
            with st.spinner("Finding best picks for you..."):
                rec_res = api.get_recommendations(token, customer_id=sel_cid, top_n=top_n)

            recs = rec_res.get("recommendations", [])

            if recs:
                cols_per_row = 3
                for i in range(0, len(recs), cols_per_row):
                    row_cols = st.columns(cols_per_row)
                    for j in range(cols_per_row):
                        if i + j < len(recs):
                            r = recs[i + j]
                            with row_cols[j]:
                                # Render as full e-commerce card with image & badges
                                prod_mock = {
                                    "product_id": r["product_id"],
                                    "product_name": r["product_name"],
                                    "category": r["category"],
                                    "price": r["price"],
                                    "stock": 50,
                                    "image_url": r.get("image_url"),
                                    "vendor_name": "ShopSense Verified Partner"
                                }
                                st.markdown(theme_module.render_product_card_html(prod_mock, current_theme), unsafe_allow_html=True)
                                
                                st.caption(f"💡 *{r.get('reason', 'Top recommendation for you')}*")
                                if st.button("⚡ Buy Now", key=f"rec_cust_buy_{r['product_id']}_{i+j}", type="primary", use_container_width=True):
                                    try:
                                        res = api.create_transaction(token, {
                                            "product_id": r["product_id"],
                                            "quantity": 1
                                        })
                                        st.success(f"🎉 Order placed! Order ID: #{res['transaction_id']}")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Purchase failed: {e}")
            else:
                st.info("No personalized recommendations yet. Browse and purchase products to tailor your picks!")
        except Exception as e:
            st.error(f"Error loading recommendations: {e}")

    else:
        # Admin / Staff Diagnostic View
        st.subheader("💡 Collaborative Filtering Recommendation Engine")
        st.caption("Personalized product recommendations computed via user-item interaction matrix, cosine customer affinity, and item taste clustering.")

        # 1. Customer Selection
        try:
            cust_list = api.get_customer_behavior(token)
            if cust_list:
                sel_cid = st.selectbox(
                    "Select Customer to Generate Personalized Recommendations for:",
                    options=[c["customer_id"] for c in cust_list],
                    format_func=lambda x: f"Customer #{x} - {[c['customer_name'] for c in cust_list if c['customer_id']==x][0]} ({[c['email'] for c in cust_list if c['customer_id']==x][0]})",
                    key="rec_cust_sel"
                )
            else:
                sel_cid = user_id or 1
        except Exception:
            sel_cid = user_id or 1

        top_n = st.slider("Number of Recommendations (Top-N)", min_value=3, max_value=15, value=10, key="rec_slider_top_n")

        # 2. Recommendations Display
        try:
            with st.spinner("Computing Cosine Similarity & Matrix Vector Affinities..."):
                rec_res = api.get_recommendations(token, customer_id=sel_cid, top_n=top_n)

            recs = rec_res.get("recommendations", [])
            st.markdown(f"#### 🎯 Recommended for **{rec_res.get('customer_name', 'Customer')}**")

            if recs:
                cols = st.columns(min(len(recs), 5))
                for idx, r in enumerate(recs[:5]):
                    with cols[idx]:
                        with st.container(border=True):
                            st.markdown(f"**{r['product_name']}**")
                            st.caption(f"🏷️ {r['category']}")
                            st.write(f"💲 **${r['price']:,.2f}**")
                            st.write(f"⭐ **Score: {r['score']:.2f}**")
                            st.info(f"💡 {r['reason']}")

                st.markdown("##### Detailed Recommendation Scoring Table")
                df_recs = pd.DataFrame(recs)
                st.dataframe(
                    df_recs[["product_id", "product_name", "category", "price", "score", "reason"]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No recommendations found for this customer profile.")

        except Exception as e:
            st.error(f"Error fetching recommendations: {e}")

        st.markdown("---")

        # 3. Precision@K Model Evaluation Report
        st.subheader("📊 Recommendation Quality & Precision@K Evaluation")
        try:
            with st.spinner("Evaluating Collaborative Filtering Precision@K..."):
                eval_res = api.get_recommendation_evaluation(token, k=5)

            p_k = eval_res.get("precision_at_k", 0.0)
            p_target = eval_res.get("precision_target", 0.75)
            p_met = eval_res.get("target_met", False)

            e1, e2, e3 = st.columns(3)
            with e1:
                st.metric("Recommendation Precision@5", f"{p_k * 100:.1f}%", delta="Target ≥ 75%" if p_met else "Evaluated Baseline")
            with e2:
                st.metric("Precision Target Threshold", f"{p_target * 100:.1f}%")
            with e3:
                st.metric("Test Customer Cohorts Evaluated", eval_res.get("total_customers_evaluated", 0))

            if p_met:
                st.success(f"✅ Recommendation Relevance Target Met: **{p_k * 100:.1f}%** (Target ≥ 75%) based on holdout category affinity validation.")
            else:
                st.info(
                    f"📊 **Evaluated Recommendation Precision@K: {p_k * 100:.1f}%**.\n\n"
                    f"*Precision@K measures the proportion of recommended items matching customer category affinities across test holdout interactions.*"
                )

        except Exception as e:
            st.error(f"Error evaluating recommendations: {e}")
