import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
from datetime import datetime
import tempfile

# --- Page Configuration ---
st.set_page_config(
    page_title="HealthKart Advanced ROI Dashboard",
    page_icon="🚀",
    layout="wide"
)

# --- Custom CSS ---
def load_css():
    st.markdown("""
        <style>
        .main { background-color: #F5F5F5; }
        [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
            border: 1px solid #e6e6e6; border-radius: 10px; padding: 20px;
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.02); background-color: white;
        }
        [data-testid="stMetric"] { background-color: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 10px; padding: 15px; }
        [data-testid="stMetricValue"] { color: #262730; }
        [data-testid="stMetricLabel"] { color: #5A5A5A; }
        h2 { color: #1a1a1a; font-weight: 600; }
        h3 { color: #333333; font-weight: 500; }
        </style>
    """, unsafe_allow_html=True)

# --- PDF Generation Function (with layout fixes) ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Influencer Campaign Report', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(kpis, charts, df):
    pdf = PDF()
    pdf.add_page()
    
    # --- Executive Summary ---
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Executive Summary', 0, 1, 'L')
    pdf.set_font('Arial', '', 11)
    
    # KPIs Table (2x2 Grid)
    pdf.set_font('Arial', 'B', 12)
    pdf.ln(5)
    kpi_items = list(kpis.items())
    line_height = pdf.font_size * 2
    col_width = pdf.w / 2.2

    pdf.cell(col_width, line_height, f"{kpi_items[0][0]}: {kpi_items[0][1]}", border=1)
    pdf.cell(col_width, line_height, f"{kpi_items[1][0]}: {kpi_items[1][1]}", border=1)
    pdf.ln(line_height)
    
    pdf.cell(col_width, line_height, f"{kpi_items[2][0]}: {kpi_items[2][1]}", border=1)
    pdf.cell(col_width, line_height, f"{kpi_items[3][0]}: {kpi_items[3][1]}", border=1)
    pdf.ln(line_height)
    pdf.ln(5)
    
    # Auto-generated insights (Single text block)
    top_roas_influencer = df.nlargest(1, 'incremental_roas').iloc[0]
    top_rev_influencer = df.nlargest(1, 'total_revenue').iloc[0]
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, "Key Insights:", 0, 1, 'L')
    pdf.set_font('Arial', '', 11)
    
    insights_text = (
        f"- Highest ROAS performer: {top_roas_influencer['name']} ({top_roas_influencer['incremental_roas']:.2f}x).\n"
        f"- Top revenue generator: {top_rev_influencer['name']} (Rs. {top_rev_influencer['total_revenue']:,.0f})."
    )
    pdf.multi_cell(0, 6, insights_text)
    pdf.ln(10)

    # --- Charts Section ---
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Visual Analysis', 0, 1, 'L')

    chart_files = []
    for chart_name, fig in charts.items():
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            fig.write_image(tmp_file.name, scale=2)
            chart_files.append(tmp_file.name)
    
    pdf.image(chart_files[0], x=10, y=pdf.get_y(), w=90)
    pdf.image(chart_files[1], x=110, y=pdf.get_y(), w=90)
    pdf.ln(65)
    pdf.image(chart_files[2], x=10, y=pdf.get_y(), w=90)
    pdf.image(chart_files[3], x=110, y=pdf.get_y(), w=90)
    pdf.ln(65)

    # --- Detailed Data Table ---
    if not df.empty:
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Top 10 Influencers Data', 0, 1, 'L')
        pdf.set_font('Arial', '', 9)
        top_10_df = df.nlargest(10, 'incremental_roas')[['name', 'category', 'total_revenue', 'total_payout', 'incremental_roas']]
        
        col_widths = {'name': 70, 'category': 25, 'total_revenue': 30, 'total_payout': 30, 'incremental_roas': 30}
        
        pdf.set_fill_color(224, 235, 255)
        for col, width in col_widths.items():
            pdf.cell(width, 8, col.replace('_', ' ').title(), 1, 0, 'C', 1)
        pdf.ln()

        for _, row in top_10_df.iterrows():
            pdf.cell(col_widths['name'], 8, row['name'], 1)
            pdf.cell(col_widths['category'], 8, row['category'], 1)
            pdf.cell(col_widths['total_revenue'], 8, f"Rs.{row['total_revenue']:,.0f}", 1, 0, 'R')
            pdf.cell(col_widths['total_payout'], 8, f"Rs.{row['total_payout']:,.0f}", 1, 0, 'R')
            pdf.cell(col_widths['incremental_roas'], 8, f"{row['incremental_roas']:.2f}x", 1, 0, 'R')
            pdf.ln()

    return pdf.output(dest='S')

# --- Helper Functions (Calculations) ---
def calculate_payouts(payouts_df, posts_df, tracking_df):
    payouts_with_counts = payouts_df.copy()
    post_counts = posts_df.groupby('influencer_id').size().reset_index(name='post_count')
    payouts_with_counts = pd.merge(payouts_with_counts, post_counts, on='influencer_id', how='left').fillna(0)
    order_counts = tracking_df.groupby('influencer_id')['orders'].sum().reset_index(name='total_orders')
    payouts_with_counts = pd.merge(payouts_with_counts, order_counts, on='influencer_id', how='left').fillna(0)
    payouts_with_counts['total_payout'] = np.where(payouts_with_counts['basis'] == 'per_post', payouts_with_counts['rate'] * payouts_with_counts['post_count'], payouts_with_counts['rate'] * payouts_with_counts['total_orders'])
    return payouts_with_counts[['influencer_id', 'total_payout']]

def calculate_roas(df):
    BASELINE_CONVERSION_RATE = 0.15
    df['roas'] = df['total_revenue'] / df['total_payout']
    df['incremental_revenue'] = df['total_revenue'] * (1 - BASELINE_CONVERSION_RATE)
    df['incremental_roas'] = df['incremental_revenue'] / df['total_payout']
    df.replace([np.inf, -np.inf], 0, inplace=True)
    df.fillna(0, inplace=True)
    return df

# --- UI Rendering Functions ---
def display_kpis(df):
    st.subheader("📈 Overall Campaign Performance")
    if df.empty:
        st.warning("No data available for the selected filters.")
        return {}
    with st.container():
        total_revenue, total_payout = df['total_revenue'].sum(), df['total_payout'].sum()
        overall_roas = total_revenue / total_payout if total_payout > 0 else 0
        overall_inc_roas = (total_revenue * 0.85) / total_payout if total_payout > 0 else 0
        kpis = {"Total Revenue": f"Rs. {total_revenue:,.0f}", "Total Payout": f"Rs. {total_payout:,.0f}", "Overall ROAS": f"{overall_roas:.2f}x", "Incremental ROAS": f"{overall_inc_roas:.2f}x"}
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Revenue", kpis["Total Revenue"])
        col2.metric("Total Payout", kpis["Total Payout"])
        col3.metric("Overall ROAS", kpis["Overall ROAS"])
        col4.metric("Incremental ROAS", kpis["Incremental ROAS"], help="Assumes 15% baseline organic sales.")
        return kpis

def display_top_performers(df):
    st.subheader("🏆 Top Performing Influencers")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### By Incremental ROAS")
            top_roas = df.nlargest(10, 'incremental_roas')
            fig_roas = px.bar(top_roas, x='incremental_roas', y='name', orientation='h', labels={'name': ''}, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_roas.update_layout(yaxis_title=None, xaxis_title="ROAS (x)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_roas, use_container_width=True)
        with col2:
            st.markdown("##### By Revenue Generated")
            top_revenue = df.nlargest(10, 'total_revenue')
            fig_revenue = px.bar(top_revenue, x='total_revenue', y='name', orientation='h', labels={'name': ''}, color_discrete_sequence=px.colors.qualitative.Pastel2)
            fig_revenue.update_layout(yaxis_title=None, xaxis_title="Revenue (₹)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_revenue, use_container_width=True)
        return fig_roas, fig_revenue

def display_persona_analysis(df):
    st.subheader("🧑‍🔬 Persona & Platform Analysis")
    with st.container():
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown("##### Follower Count vs. Engagement Rate")
            fig_scatter = px.scatter(df[df['total_revenue'] > 0], x='follower_count', y='engagement_rate', size='total_revenue', color='category', hover_name='name', size_max=40, log_x=True)
            fig_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', legend_title_text='Category')
            st.plotly_chart(fig_scatter, use_container_width=True)
        with col2:
            st.markdown("##### Average ROAS by Platform")
            platform_roas = df.groupby('platform')['roas'].mean().reset_index()
            fig_platform = px.pie(platform_roas, names='platform', values='roas', hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe)
            fig_platform.update_traces(textinfo='percent+label', pull=[0.05, 0])
            fig_platform.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_platform, use_container_width=True)
        return fig_scatter, fig_platform

def display_timeseries(df):
    st.subheader("📅 Temporal Analysis")
    with st.container():
        df['order_date'] = pd.to_datetime(df['order_date'])
        revenue_over_time = df.set_index('order_date').resample('W-Mon')['revenue'].sum().reset_index()
        fig_timeseries = px.line(revenue_over_time, x='order_date', y='revenue', title='Weekly Revenue from Influencer Campaigns', labels={'order_date': 'Week', 'revenue': 'Total Revenue (₹)'})
        fig_timeseries.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_timeseries, use_container_width=True)

# --- Main App ---
load_css()
st.title("Advanced Influencer ROI Dashboard")
st.markdown("Analyze campaign performance with advanced filtering and reporting.")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Controls")
    influencers_file = st.file_uploader("Upload Influencers CSV", type="csv")
    posts_file = st.file_uploader("Upload Posts CSV", type="csv")
    tracking_file = st.file_uploader("Upload Tracking Data CSV", type="csv")
    payouts_file = st.file_uploader("Upload Payouts CSV", type="csv")

if all([influencers_file, posts_file, tracking_file, payouts_file]):
    influencers_df = pd.read_csv(influencers_file)
    posts_df = pd.read_csv(posts_file)
    tracking_df = pd.read_csv(tracking_file)
    payouts_df = pd.read_csv(payouts_file)
    
    with st.sidebar:
        st.markdown("---"); st.header("📊 Filters")
        campaigns = ['All'] + list(tracking_df['campaign'].unique())
        products = ['All'] + list(tracking_df['product_id'].unique())
        selected_campaign = st.selectbox('Campaign', campaigns)
        selected_product = st.selectbox('Product', products)
        min_date, max_date = pd.to_datetime(tracking_df['order_date']).min().date(), pd.to_datetime(tracking_df['order_date']).max().date()
        date_range = st.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

    filtered_tracking_df = tracking_df.copy()
    if selected_campaign != 'All': filtered_tracking_df = filtered_tracking_df[filtered_tracking_df['campaign'] == selected_campaign]
    if selected_product != 'All': filtered_tracking_df = filtered_tracking_df[filtered_tracking_df['product_id'] == selected_product]
    if len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        # Ensure 'order_date' is timezone-naive before comparing with timezone-naive start/end
        filtered_tracking_df['order_date'] = pd.to_datetime(filtered_tracking_df['order_date']).dt.tz_localize(None)
        filtered_tracking_df = filtered_tracking_df[filtered_tracking_df['order_date'].between(start_date, end_date)]

    influencer_revenue = filtered_tracking_df.groupby('influencer_id').agg(total_revenue=('revenue', 'sum'), total_orders=('orders', 'sum')).reset_index()
    posts_df['engagement'] = posts_df['likes'] + posts_df['comments']
    influencer_posts_metrics = posts_df.groupby('influencer_id').agg(total_reach=('reach', 'sum'), total_engagement=('engagement', 'sum'), post_count=('post_id', 'count')).reset_index()
    influencer_posts_metrics['engagement_rate'] = (influencer_posts_metrics['total_engagement'] / influencer_posts_metrics['total_reach']) * 100
    payouts_calculated_df = calculate_payouts(payouts_df, posts_df, filtered_tracking_df)
    
    master_df = pd.merge(influencers_df, influencer_revenue, on='influencer_id', how='left')
    master_df = pd.merge(master_df, influencer_posts_metrics, on='influencer_id', how='left')
    master_df = pd.merge(master_df, payouts_calculated_df, on='influencer_id', how='left')
    master_df = calculate_roas(master_df)
    
    with st.sidebar:
        platforms = master_df['platform'].unique(); categories = master_df['category'].unique()
        selected_platform = st.multiselect('Platform', platforms, default=platforms)
        selected_category = st.multiselect('Category', categories, default=categories)
        max_roas = float(master_df['incremental_roas'].max())
        if max_roas == 0.0: max_roas = 1.0
        roas_range = st.slider('Incremental ROAS', 0.0, max_roas, (0.0, max_roas))
    
    filtered_df = master_df[(master_df['platform'].isin(selected_platform)) & (master_df['category'].isin(selected_category)) & (master_df['incremental_roas'].between(roas_range[0], roas_range[1]))]
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🧑‍💻 Influencer Deep Dive", "📅 Temporal Analysis", "🔬 Data Explorer"])
    with tab1: 
        kpi_data = display_kpis(filtered_df)
        fig_scatter, fig_platform = display_persona_analysis(filtered_df)
    with tab2: 
        fig_roas, fig_revenue = display_top_performers(filtered_df)
        st.write(""); st.subheader("📉 Underperforming Influencers (ROAS < 1.5x)"); 
        st.dataframe(filtered_df[filtered_df['roas'] < 1.5].sort_values('roas'), hide_index=True)
    with tab3:
        display_timeseries(filtered_tracking_df)
    with tab4: 
        st.subheader("📂 Full Filtered Dataset"); 
        st.dataframe(filtered_df.style.format({'total_revenue': '₹{:,.2f}', 'total_payout': '₹{:,.2f}', 'roas': '{:.2f}x', 'incremental_roas': '{:.2f}x', 'engagement_rate': '{:.2f}%'}), hide_index=True)
    
    with st.sidebar:
        st.markdown("---"); st.header("⬇️ Export")
        if st.button("Generate PDF Report"):
            if not filtered_df.empty:
                charts_for_pdf = {"ROAS": fig_roas, "Revenue": fig_revenue, "Scatter": fig_scatter, "Platform": fig_platform}
                pdf_data = generate_pdf_report(kpi_data, charts_for_pdf, filtered_df)
                st.download_button(label="Download Report as PDF", data=bytes(pdf_data), file_name=f"HealthKart_Report_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf")
            else:
                st.warning("Cannot generate report for empty data. Please adjust filters.")
else:
    st.info("👋 Welcome! Please upload all four CSV files using the sidebar to begin.")