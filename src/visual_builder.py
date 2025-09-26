
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
    if not numeric_cols:
        st.warning("Need at least one numeric column for Y-axis.")
        return
    y_col = st.selectbox("Y-axis (numeric)", numeric_cols)

    agg_fn = st.selectbox("Aggregation", ["sum", "mean", "count", "none"], index=0)

    plot_df = df
    if agg_fn != "none":
        if agg_fn == "count":
            plot_df = df.groupby(x_col, dropna=False).size().reset_index(name="count")
            y_col = "count"
        else:
            plot_df = df.groupby(x_col, dropna=False)[y_col].agg(agg_fn).reset_index()

    title_core = f"{agg_fn}({y_col})" if agg_fn != "none" else y_col
    title = f"{title_core} by {x_col}" if chart_type != "Line" else f"{title_core} over {x_col}"

    if chart_type == "Bar":
        fig = px.bar(plot_df, x=x_col, y=y_col, title=title)
    elif chart_type == "Line":
        fig = px.line(plot_df, x=x_col, y=y_col, markers=True, title=title)
    else:  # Scatter
        fig = px.scatter(plot_df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Show grouped data"):
        st.dataframe(plot_df, use_container_width=True)



# # src/visual_builder.py                        # Module path (for your repo structure).
# # Simple, dependency-light chart builder       # High-level description.
# # (uses Plotly Express).                       # Tech note.

# import streamlit as st                         # Streamlit: UI layer for the web app.
# import pandas as pd                            # Pandas: DataFrame manipulation.
# import plotly.express as px                    # Plotly Express: quick charting API.

# def builder(df: pd.DataFrame):                 # Entry point: builds the chart UI for a given DataFrame.
#     """
#     Interactive chart builder for the invoice dataset.
#     Lets users pick chart type, fields, and aggregations quickly.
#     """
#     st.subheader("🔧 Interactive Chart Builder")  # Section heading in the Streamlit page.

#     if df.empty:                                   # Guard: handle the no-data case early.
#         st.info("No data yet. Create or upload invoices to build visuals.")  # Friendly info message.
#         return                                     # Exit early if no rows.

#     # Basic clean-up
#     df = df.dropna(axis=1, how="all")              # Remove columns that are entirely NaN to declutter selectors.

#     chart_type = st.selectbox(                     # UI control: choose which chart to render.
#         "Chart type",                              # Label shown to the user.
#         ["Bar", "Line", "Scatter", "Pie", "Histogram"],  # Supported chart types.
#         index=0,                                   # Default selection = "Bar".
#     )

#     cols = df.columns.tolist()                     # Cache all column names once.
#     numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()  # Columns with numeric dtype.
#     non_numeric_cols = [c for c in cols if c not in numeric_cols]         # Everything else (often categorical).

#     if chart_type == "Pie":                        # Branch: configure and render a Pie chart.
#         if not non_numeric_cols or not numeric_cols:  # Need one categorical + one numeric field.
#             st.warning("Need at least one text column and one numeric column for a pie chart.")  # UX hint.
#             return                                 # Cannot proceed without required fields.
#         label_col = st.selectbox("Label (categorical)", non_numeric_cols)  # Choose category labels.
#         value_col = st.selectbox("Values (numeric)", numeric_cols)         # Choose numeric values.
#         fig = px.pie(                               # Build a pie chart with Plotly Express.
#             df, names=label_col, values=value_col, title=f"{label_col} share"
#         )
#         st.plotly_chart(fig, use_container_width=True)  # Render full-width in the container.
#         return                                    # Done for pie; skip the rest.

#     if chart_type == "Histogram":                  # Branch: configure and render a Histogram.
#         if not numeric_cols:                       # Need at least one numeric column to bin.
#             st.warning("Need at least one numeric column for a histogram.")  # UX hint.
#             return
#         hist_col = st.selectbox("Numeric column", numeric_cols)  # Pick the numeric field to bin.
#         nbins = st.slider("Bins", 5, 60, 20)       # Slider to choose number of bins (range 5–60, default 20).
#         fig = px.histogram(                        # Build histogram for selected column.
#             df, x=hist_col, nbins=nbins, title=f"Histogram of {hist_col}"
#         )
#         st.plotly_chart(fig, use_container_width=True)  # Render chart.
#         return                                    # Done for histogram.

#     # Bar / Line / Scatter                         # Shared config for the other three chart types.
#     x_col = st.selectbox("X-axis", cols)           # Choose X-axis; can be any dtype (categorical, date, etc.).
#     if not numeric_cols:                            # Ensure we have a numeric Y candidate.
#         st.warning("Need at least one numeric column for Y-axis.")  # UX hint.
#         return
#     y_col = st.selectbox("Y-axis (numeric)", numeric_cols)  # Choose Y-axis (numeric only).

#     agg_fn = st.selectbox(                         # Optional aggregation to roll up data by X.
#         "Aggregation", ["sum", "mean", "count", "none"], index=0  # Default to "sum".
#     )

#     plot_df = df                                   # Start with the raw DataFrame; may replace with grouped data.
#     if agg_fn != "none":                           # If an aggregation is requested:
#         if agg_fn == "count":                      # Special case: count rows per X category.
#             plot_df = df.groupby(x_col, dropna=False).size().reset_index(name="count")  # Compute counts.
#             y_col = "count"                        # Update Y to point at the computed "count" column.
#         else:                                      # For sum/mean: aggregate Y by X.
#             plot_df = (
#                 df.groupby(x_col, dropna=False)[y_col].agg(agg_fn).reset_index()
#             )

#     title_core = f"{agg_fn}({y_col})" if agg_fn != "none" else y_col  # Core of the chart title.
#     title = (                                  # Friendly title depending on chart type.
#         f"{title_core} by {x_col}" if chart_type != "Line" else f"{title_core} over {x_col}"
#     )

#     if chart_type == "Bar":                        # Render a Bar chart.
#         fig = px.bar(plot_df, x=x_col, y=y_col, title=title)  # Build bar chart from (possibly) aggregated data.
#     elif chart_type == "Line":                     # Render a Line chart.
#         fig = px.line(plot_df, x=x_col, y=y_col, markers=True, title=title)  # Markers=True to show data points.
#     else:                                          # Render a Scatter chart.
#         fig = px.scatter(plot_df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")  # Basic XY scatter.

#     st.plotly_chart(fig, use_container_width=True)  # Draw the chosen figure full width.

#     with st.expander("Show grouped data"):          # Collapsible panel to inspect the data used for plotting.
#         st.dataframe(plot_df, use_container_width=True)  # Show the (possibly aggregated) DataFrame.
