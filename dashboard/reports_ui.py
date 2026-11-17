import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional

def render_reports_page(api, token: str, role: str, vendor_id: Optional[int] = None):
    """
    Module 6: Report Exporting Portal (PDF & Excel)
    """
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 20px; border-radius: 12px; color: white; margin-bottom: 24px;">
        <h2 style="margin:0; color: #38bdf8;">📥 ShopSense Analytics & Reporting Exports</h2>
        <p style="margin: 6px 0 0 0; color: #94a3b8; font-size: 0.95rem;">
            Download verified multi-sheet Excel workbooks and executive PDF reports with matching database analytics.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style="border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; background: white;">
            <h4 style="margin: 0; color: #0f172a;">📊 Multi-Sheet Excel Workbook (.xlsx)</h4>
            <p style="color: #64748b; font-size: 0.88rem; margin: 8px 0 16px 0;">
                Complete dataset breakdown containing 10 dedicated sheets:
                Revenue Summary, Monthly Revenue, Vendor Performance, Product Sales, Customer Analytics,
                RFM Segmentation, Inventory Summary, Demand Forecasts, Stock Alerts, and Recommendation Metrics.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📥 Generate & Download Excel Report", key="btn_download_excel", type="primary", use_container_width=True):
            with st.spinner("Compiling multi-sheet Excel report from database..."):
                try:
                    data = api.download_excel_report_bytes(token, vendor_id=vendor_id)
                    st.download_button(
                        label="💾 Click Here to Save Excel (.xlsx)",
                        data=data,
                        file_name=f"ShopSense_Analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    st.success("✅ Excel workbook generated successfully!")
                except Exception as e:
                    st.error(f"Error generating Excel report: {e}")

    with col2:
        st.markdown("""
        <div style="border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; background: white;">
            <h4 style="margin: 0; color: #0f172a;">📄 Executive PDF Summary Report (.pdf)</h4>
            <p style="color: #64748b; font-size: 0.88rem; margin: 8px 0 16px 0;">
                High-level executive briefing document featuring executive revenue summaries,
                top-selling products, machine learning model performance scores, and stock status distributions.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📥 Generate & Download PDF Report", key="btn_download_pdf", type="primary", use_container_width=True):
            with st.spinner("Rendering executive PDF report..."):
                try:
                    data = api.download_pdf_report_bytes(token, vendor_id=vendor_id)
                    st.download_button(
                        label="💾 Click Here to Save PDF (.pdf)",
                        data=data,
                        file_name=f"ShopSense_Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    st.success("✅ PDF report generated successfully!")
                except Exception as e:
                    st.error(f"Error generating PDF report: {e}")
