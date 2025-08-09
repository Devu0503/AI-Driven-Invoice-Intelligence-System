# src/visual_explorer.py
import streamlit as st
import pandas as pd
import plotly.express as px

AGGS = {"sum":"sum","mean":"mean","count":"count","max":"max","min":"min"}

def explore(df: pd.DataFrame):
    st.markdown("### 🧲 Drag‑&‑Drop Style Visual Builder")
    cols = df.columns.tolist()
    x = st.selectbox("X axis", options=cols, index=min(0,len(cols)-1))
    y = st.selectbox("Y axis (numeric recommended)", options=cols, index=min(1,len(cols)-1))
    agg = st.selectbox("Aggregation", options=list(AGGS.keys()), index=0)
    chart = st.selectbox("Chart type", ["bar","line","scatter","pie"], index=0)

    if x and y:
        g = df.groupby(x)[y].agg(AGGS[agg]).reset_index().rename(columns={y:f"{agg}_{y}"})
        y_new = f"{agg}_{y}"

        if chart == "bar":
            fig = px.bar(g, x=x, y=y_new)
        elif chart == "line":
            fig = px.line(g, x=x, y=y_new)
        elif chart == "scatter":
            fig = px.scatter(g, x=x, y=y_new)
        else:  # pie
            fig = px.pie(g, names=x, values=y_new)
        st.plotly_chart(fig, use_container_width=True)
