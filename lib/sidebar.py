import streamlit as st
import zerohertzLib as zz

from .visual import _signal


def upside():
    st.session_state["scale"] = st.slider("Height Scale", 0.2, 1.5, 1.0)
    krx = st.session_state["data"]
    name = st.selectbox("Name", krx.data.keys())
    symbol = krx[name]
    year = st.slider("Period [yrs]", 2012, 2023, 2019)
    method = st.selectbox(
        "Method",
        ["Moving Average", "RSI", "Bollinger Bands", "Momentum", "MACD", "Quant"],
        index=5,
    )
    return name, symbol, year, method


def downside():
    name, symbol, method = (
        st.session_state["cache"]["name"],
        st.session_state["cache"]["symbol"],
        st.session_state["cache"]["method"],
    )
    ohlc = st.selectbox("OHLC", ["All", "Open", "High", "Low", "Close"], index=4)
    vis_ma = st.checkbox("Moving Averages", False)
    vis_bollinger = st.checkbox("Bollinger Bands", False)
    vis_signals_holder = st.empty()
    if ohlc == "All":
        ohlc = ""
    if method == "Quant":
        top = st.slider("Top", 1, 10, 3)
        if st.button("Analyze"):
            st.session_state["logger"].info(
                f"[Quant] Button Clicked: {name} ({symbol})"
            )
            st.session_state["logger"].info(f"[Quant] ohlc: {ohlc}")
            with st.spinner("Calculating..."):
                qnt = zz.quant.Quant(
                    name, st.session_state["cache"]["data"], ohlc=ohlc, top=top
                )
                _signal(qnt)
                st.session_state["cache"]["qnt"] = qnt
                st.session_state["cache"]["transaction"] = qnt.transaction
                st.session_state["cache"]["buy"] = qnt.buy
                st.session_state["cache"]["sell"] = qnt.sell
            st.session_state["logger"].info(f"[Quant] Done: {name} ({symbol})")
    else:
        st.session_state["logger"].info(f"[{method}] Calculating: {name} ({symbol})")
        st.session_state["logger"].info(f"[{method}] ohlc: {ohlc}")
        signals = getattr(MethodUI, method.replace(" ", "_").lower())(
            st.session_state["cache"]["data"], ohlc
        )
        results = zz.quant.backtest(st.session_state["cache"]["data"], signals, ohlc)
        _signal(signals)
        st.session_state["cache"]["transaction"] = results["transaction"]
        st.session_state["cache"]["buy"] = results["buy"]
        st.session_state["cache"]["sell"] = results["sell"]
        st.session_state["logger"].info(f"[{method}] Done: {name} ({symbol})")
    vis_signals = False
    if st.session_state["cache"]["transaction"] is not None:
        vis_signals = vis_signals_holder.checkbox("Quant Signals", True)
    st.session_state["cache"]["vis_ma"] = vis_ma
    st.session_state["cache"]["vis_bollinger"] = vis_bollinger
    st.session_state["cache"]["vis_signals"] = vis_signals


class MethodUI:
    def moving_average(data, ohlc):
        arg1 = st.slider("Short Window", 10, 50, 40)
        arg2 = st.slider("Long Window", 50, 90, 80)
        arg3 = st.slider("Threshold", 0.0, 1.0, 0.0)
        return zz.quant.moving_average(data, arg1, arg2, arg3, ohlc)

    def rsi(data, ohlc):
        arg1 = st.slider("Lower Band", 5, 40, 20)
        arg2 = st.slider("Upper Band", 60, 95, 80)
        arg3 = st.slider("Window", 1, 90, 30)
        return zz.quant.rsi(data, arg1, arg2, arg3, ohlc)

    def bollinger_bands(data, ohlc):
        arg1 = st.slider("Window", 1, 90, 30)
        arg2 = st.slider("Std. Dev.", 1.5, 3.0, 2.5)
        return zz.quant.bollinger_bands(data, arg1, arg2, ohlc)

    def momentum(data, ohlc):
        arg1 = st.slider("Window", 5, 90, 5)
        return zz.quant.momentum(data, arg1, ohlc)

    def macd(data, ohlc):
        arg1 = st.slider("Fast", 6, 36, 12)
        arg2 = st.slider("Signal", 5, 18, 9)
        return zz.quant.macd(data, arg1, arg2, ohlc)
