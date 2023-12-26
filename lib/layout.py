import plotly.graph_objs as go
import streamlit as st


def _default():
    layout = go.Layout()
    layout.autosize = True
    layout.legend.font.color = "black"
    layout.paper_bgcolor = "white"
    layout.plot_bgcolor = "white"
    layout.showlegend = True
    layout.margin = {"l": 50, "r": 50, "t": 20, "b": 50}
    return layout


def _main():
    layout = _default()
    layout.height = 500 * st.session_state["scale"]
    layout.width = 1000
    layout.xaxis = {
        "type": "category",
        "gridcolor": "black",
        "tickangle": -45,
        "tickfont": {"color": "black"},
        "showgrid": True,
        "tickmode": "auto",
        "nticks": 20,
        "rangeslider": {"visible": False},
    }
    layout.yaxis = {
        "gridcolor": "black",
        "tickprefix": "₩",
        "tickformat": ",",
        "tickfont": {"color": "black"},
        "showgrid": True,
        "autorange": True,
    }
    if not st.session_state["cache"]["vis_signals"]:
        return layout
    layout.yaxis2 = {
        "overlaying": "y",
        "side": "right",
        "tickfont": {"color": "white"},
        "showgrid": False,
    }
    layout.shapes = st.session_state["cache"]["transaction_vert"]
    if st.session_state["cache"]["method"] != "Quant":
        layout.yaxis3 = {
            "overlaying": "y",
            "side": "right",
            "tickfont": {"color": "white"},
            "showgrid": False,
        }
    return layout


def _transaction():
    layout = _default()
    layout.height = 400 * st.session_state["scale"]
    layout.width = 1000
    return layout
