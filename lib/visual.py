import plotly.graph_objs as go
import streamlit as st
import zerohertzLib as zz
from plotly.subplots import make_subplots

from lib.layout import _main, _transaction
from lib.util import _color


def candle():
    data, xdata = st.session_state["cache"]["data"], st.session_state["cache"]["xdata"]
    st.session_state["cache"]["candle"] = go.Candlestick(
        x=xdata,
        open=data.Open,
        high=data.High,
        low=data.Low,
        close=data.Close,
        increasing={"line": {"color": "red"}},
        decreasing={"line": {"color": "blue"}},
        name=st.session_state["cache"]["name"],
    )
    st.session_state["logger"].info(
        f"""[Plot] Candle Chart: {st.session_state["cache"]["name"]} ({st.session_state["cache"]["symbol"]})"""
    )


def moving_average():
    xdata = st.session_state["cache"]["xdata"]
    st.session_state["cache"]["ma"] = []
    colors = _color(4, 0.5, "Set1")
    for idx, window in enumerate([5, 20, 60, 120]):
        st.session_state["cache"]["ma"].append(
            go.Scatter(
                x=xdata,
                y=st.session_state["cache"]["data"]
                .iloc[:, :4]
                .mean(1)
                .rolling(window)
                .mean(),
                mode="lines",
                name=f"MA{window}",
                line={"color": colors[idx]},
            )
        )
    st.session_state["logger"].info(
        f"""[Plot] Moving Average: {st.session_state["cache"]["name"]} ({st.session_state["cache"]["symbol"]})"""
    )


def bollinger_bands():
    bands = zz.quant.util._bollinger_bands(st.session_state["cache"]["data"])
    xdata = st.session_state["cache"]["xdata"]
    st.session_state["cache"]["bollinger"] = []
    for col_, name_, color_ in zip(
        ["lower_band", "middle_band", "upper_band"],
        ["Lower", "Middle", "Upper"],
        ["rgba(255, 0, 0, 0.5)", "rgba(0, 255, 0, 0.5)", "rgba(0, 0, 255, 0.5)"],
    ):
        st.session_state["cache"]["bollinger"].append(
            go.Scatter(
                x=xdata,
                y=bands[col_],
                mode="lines",
                name=name_,
                line={"color": color_},
            )
        )
    st.session_state["logger"].info(
        f"""[Plot] Bollinger Bands: {st.session_state["cache"]["name"]} ({st.session_state["cache"]["symbol"]})"""
    )


def _signal(signals):
    st.session_state["cache"]["quant"] = []
    if isinstance(signals, zz.quant.Quant):
        threshold_sell, threshold_buy = signals.threshold_sell, signals.threshold_buy
        signals = signals.signals
    else:
        threshold_sell, threshold_buy = -1, 1
        colors = _color(len(signals.columns))
        for idx, col in enumerate(signals.columns[:-2]):
            signals[col]
            st.session_state["cache"]["quant"].append(
                go.Scatter(
                    x=st.session_state["cache"]["xdata"],
                    y=signals[col],
                    yaxis="y3",
                    mode="lines",
                    name=zz.quant.util._method2str(col),
                    line={"color": colors[idx]},
                )
            )
    st.session_state["cache"]["quant"].append(
        go.Scatter(
            x=st.session_state["cache"]["xdata"],
            y=signals.signals,
            yaxis="y2",
            mode="lines",
            name="Signal",
            line={"color": "rgba(0, 0, 0, 0.5)"},
        )
    )
    st.session_state["cache"]["transaction_vert"] = []
    for day, sig, log in zip(
        st.session_state["cache"]["xdata"],
        signals.signals,
        signals.logic,
    ):
        vert_ = _vert(day, sig, log, (threshold_sell, threshold_buy))
        if vert_ is not None:
            st.session_state["cache"]["transaction_vert"].append(vert_)


def _backtest():
    fig = make_subplots(rows=1, cols=3)
    fig.add_trace(
        go.Histogram(
            x=st.session_state["cache"]["transaction"]["buy"],
            name="Buy",
            marker_color="red",
            nbinsx=20,
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Histogram(
            x=st.session_state["cache"]["transaction"]["sell"],
            name="Sell",
            marker_color="blue",
            nbinsx=20,
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Histogram(
            x=st.session_state["cache"]["transaction"]["profit"],
            name="Profit",
            marker_color="#0a800a",
            nbinsx=20,
        ),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Histogram(
            x=st.session_state["cache"]["transaction"]["period"],
            name="Period",
            marker_color="#0a0a80",
            nbinsx=20,
        ),
        row=1,
        col=3,
    )
    fig.update_xaxes(
        gridcolor="black",
        tickangle=-45,
        tickprefix="₩",
        tickformat=",",
        tickfont={"color": "black"},
        showgrid=True,
        tickmode="auto",
        row=1,
        col=1,
    )
    fig.update_yaxes(
        gridcolor="black",
        tickfont={"color": "black"},
        showgrid=True,
        autorange=True,
        row=1,
        col=1,
    )
    fig.update_xaxes(
        gridcolor="black",
        tickangle=-45,
        tickfont={"color": "black"},
        showgrid=True,
        tickmode="auto",
        ticksuffix="%",
        tickformat=".2f",
        row=1,
        col=2,
    )
    fig.update_yaxes(
        gridcolor="black",
        tickfont={"color": "black"},
        showgrid=True,
        autorange=True,
        row=1,
        col=2,
    )
    fig.update_xaxes(
        gridcolor="black",
        tickangle=-45,
        tickfont={"color": "black"},
        showgrid=True,
        tickmode="auto",
        ticksuffix="days",
        row=1,
        col=3,
    )
    fig.update_yaxes(
        gridcolor="black",
        tickfont={"color": "black"},
        showgrid=True,
        autorange=True,
        row=1,
        col=3,
    )
    return fig


def _vert(xdata, signal, logic, threshold=(-1, 1)):
    threshold_sell, threshold_buy = threshold
    if logic == 1:
        dash = "solid"
        color = "rgba(255, 0, 0, 0.2)"
    elif logic == -1:
        dash = "solid"
        color = "rgba(0, 0, 255, 0.2)"
    elif logic == 2:
        dash = "longdashdot"
        color = "rgba(255, 0, 0, 0.2)"
    elif logic == -2:
        dash = "longdashdot"
        color = "rgba(0, 0, 255, 0.2)"
    elif signal >= threshold_buy:
        dash = "dash"
        color = "rgba(255, 0, 0, 0.2)"
    elif signal <= threshold_sell:
        dash = "dash"
        color = "rgba(0, 0, 255, 0.2)"
    else:
        return None
    return go.layout.Shape(
        type="line",
        x0=xdata,
        y0=0,
        x1=xdata,
        y1=1,
        xref="x",
        yref="paper",
        line={"color": color, "width": 2, "dash": dash},
    )


def main():
    figs = [st.session_state["cache"]["candle"]]
    if st.session_state["cache"]["vis_ma"]:
        figs += st.session_state["cache"]["ma"]
    if st.session_state["cache"]["vis_bollinger"]:
        figs += st.session_state["cache"]["bollinger"]
    if st.session_state["cache"]["vis_signals"]:
        figs += st.session_state["cache"]["quant"]
    st.plotly_chart(
        go.Figure(
            data=figs,
            layout=_main(),
        ),
        use_container_width=True,
    )


def transaction():
    fig = _backtest()
    fig.update_layout(_transaction())
    st.plotly_chart(
        fig,
        use_container_width=True,
    )
