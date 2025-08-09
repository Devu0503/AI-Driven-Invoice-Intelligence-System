# src/visual_builder.py
# Simple, dependency-light chart builder (uses Plotly Express).

import streamlit as st
import pandas as pd
import plotly.express as px

def builder(df: pd.DataFrame):
    """
    Interactive chart builder for the invoice dataset.
    Lets users pick chart type, fields, and aggregations quickly.
    """
    st.subheader("🔧 Interactive Chart Builder")

    if df.empty:
        st.info("No data yet. Create or upload invoices to build visuals.")
        return

    # Basic clean-up
    df = df.dropna(axis=1, how="all")

    chart_type = st.selectbox(
        "Chart type",
        ["Bar", "Line", "Scatter", "Pie", "Histogram"],
        index=0,
    )

    cols = df.columns.tolist()
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    non_numeric_cols = [c for c in cols if c not in numeric_cols]

    if chart_type == "Pie":
        if not non_numeric_cols or not numeric_cols:
            st.warning("Need at least one text column and one numeric column for a pie chart.")
            return
        label_col = st.selectbox("Label (categorical)", non_numeric_cols)
        value_col = st.selectbox("Values (numeric)", numeric_cols)
        fig = px.pie(df, names=label_col, values=value_col, title=f"{label_col} share")
        st.plotly_chart(fig, use_container_width=True)
        return

    if chart_type == "Histogram":
        if not numeric_cols:
            st.warning("Need at least one numeric column for a histogram.")
            return
        hist_col = st.selectbox("Numeric column", numeric_cols)
        nbins = st.slider("Bins", 5, 60, 20)
        fig = px.histogram(df, x=hist_col, nbins=nbins, title=f"Histogram of {hist_col}")
        st.plotly_chart(fig, use_container_width=True)
        return

    # Bar / Line / Scatter
    x_col = st.selectbox("X-axis", cols)
    # y must be numeric for aggregation and lines/scatter
    if not numeric_cols:
        st.warning("Need at least one numeric column for Y-axis.")
        return
    y_col = st.selectbox("Y-axis (numeric)", numeric_cols)

    color_col = st.selectbox("Color / Group (optional)", ["None"] + cols)
    agg_fn = st.selectbox("Aggregation", ["sum", "mean", "count", "none"], index=0)

    plot_df = df
    if agg_fn != "none":
        if agg_fn == "count":
            plot_df = df.groupby(x_col, dropna=False).size().reset_index(name="count")
            y_col = "count"
        else:
            plot_df = df.groupby(x_col, dropna=False)[y_col].agg(agg_fn).reset_index()

    if chart_type == "Bar":
        fig = px.bar(plot_df, x=x_col, y=y_col,
                     color=None if color_col == "None" else plot_df[color_col],
                     title=f"{agg_fn}({y_col}) by {x_col}" if agg_fn != "none" else f"{y_col} by {x_col}")
    elif chart_type == "Line":
        fig = px.line(plot_df, x=x_col, y=y_col, markers=True,
                      color=None if color_col == "None" else plot_df[color_col],
                      title=f"{agg_fn}({y_col}) by {x_col}" if agg_fn != "none" else f"{y_col} over {x_col}")
    else:  # Scatter
        fig = px.scatter(plot_df, x=x_col, y=y_col,
                         color=None if color_col == "None" else plot_df[color_col],
                         title=f"{y_col} vs {x_col}")

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Show grouped data"):
        st.dataframe(plot_df, use_container_width=True)
