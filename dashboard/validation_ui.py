import streamlit as st
import pandas as pd
from datetime import datetime

def render_validation_and_testing_page(api, token: str, theme_module, current_theme: str):
    """
    Module 8: Dashboard Data-Consistency Validation
    Module 7: API Performance & Latency Benchmarks
    """
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 20px; border-radius: 12px; color: white; margin-bottom: 24px;">
        <h2 style="margin:0; color: #38bdf8;">🛡️ Data Consistency & API Performance Benchmarks</h2>
        <p style="margin: 6px 0 0 0; color: #94a3b8; font-size: 0.95rem;">
            Real-time automated auditing comparing raw PostgreSQL ground-truth with analytical outputs, and Locust API latency benchmarking.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_val, tab_perf = st.tabs([
        "✅ Dashboard Data-Consistency Validation (Target: ≥99%)",
        "⚡ API Latency & Throughput Testing (Target: ≤300ms)"
    ])

    # ==========================================
    # DATA CONSISTENCY VALIDATION
    # ==========================================
    with tab_val:
        st.subheader("Automated Cross-System Data Consistency Audit")
        st.markdown("""
        Compares 6 primary metrics between PostgreSQL ground-truth queries and analytical dashboard endpoints:
        Marketplace Revenue, Product Count, Customer Count, Vendor Count, Inventory Stock, and Transaction Counts.
        """)

        col_run, col_kpi = st.columns([1, 2])
        with col_run:
            if st.button("🔍 Run Full Consistency Audit", key="btn_run_val", type="primary", use_container_width=True):
                with st.spinner("Auditing dashboard outputs against PostgreSQL..."):
                    try:
                        res = api.run_consistency_validation(token)
                        st.success(f"Audit Complete! Consistency Score: {res['consistency_percentage']}%")
                    except Exception as e:
                        st.error(f"Validation failed: {e}")

        # Fetch latest validation history
        try:
            history = api.get_validation_history(token, limit=5)
            if history:
                latest = history[0]
                with col_kpi:
                    k1, k2, k3 = st.columns(3)
                    with k1:
                        st.metric("Latest Consistency", f"{latest['consistency_percentage']}%", "Target: >= 99%")
                    with k2:
                        st.metric("Audit Status", latest["status"])
                    with k3:
                        st.metric("Last Audited", latest["validation_time"].split()[1] if ' ' in latest['validation_time'] else latest['validation_time'])

                st.markdown("##### 📋 Entity Comparison Results")
                df_comp = pd.DataFrame(latest.get("comparisons", []))
                if not df_comp.empty:
                    st.dataframe(
                        df_comp[["metric", "db_value", "dashboard_value", "diff", "match"]].rename(columns={
                            "metric": "Entity / Metric",
                            "db_value": "Database Ground Truth",
                            "dashboard_value": "Dashboard Calculated",
                            "diff": "Absolute Delta",
                            "match": "Consistent Match"
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
            else:
                st.info("No prior consistency audits found. Click 'Run Full Consistency Audit' above to execute.")
        except Exception as e:
            st.error(f"Error fetching validation history: {e}")

    # ==========================================
    # API PERFORMANCE BENCHMARKS
    # ==========================================
    with tab_perf:
        st.subheader("⚡ API Response Time & Throughput Benchmarking")
        st.markdown("""
        Evaluates core analytics and ML endpoints against the Milestone 3 performance SLA of **Response Time ≤ 300 ms**.
        """)

        p_col_run, p_col_kpi = st.columns([1, 2])
        with p_col_run:
            iterations = st.slider("Benchmark Requests per Endpoint", min_value=3, max_value=15, value=5, step=1)
            if st.button("🚀 Run Live Latency Benchmarks", key="btn_run_perf", type="primary", use_container_width=True):
                with st.spinner(f"Sending {iterations} benchmark requests across critical APIs..."):
                    try:
                        bench_res = api.run_performance_benchmarks(token, iterations=iterations)
                        st.success("Benchmarks completed successfully!")
                    except Exception as e:
                        st.error(f"Benchmark execution failed: {e}")

        try:
            perf_history = api.get_performance_history(token, limit=10)
            if perf_history:
                st.markdown("##### ⏱️ Recent Benchmark Results")
                df_p = pd.DataFrame(perf_history)
                st.dataframe(
                    df_p[["test_time", "endpoint", "avg_response_time_ms", "min_response_time_ms", "max_response_time_ms", "p95_response_time_ms", "requests_per_sec", "status"]].rename(columns={
                        "test_time": "Timestamp",
                        "endpoint": "API Endpoint",
                        "avg_response_time_ms": "Avg Latency (ms)",
                        "min_response_time_ms": "Min (ms)",
                        "max_response_time_ms": "Max (ms)",
                        "p95_response_time_ms": "P95 (ms)",
                        "requests_per_sec": "Throughput (RPS)",
                        "status": "SLA Status"
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No latency benchmark logs available. Click 'Run Live Latency Benchmarks' above.")
        except Exception as e:
            st.error(f"Error loading performance history: {e}")
