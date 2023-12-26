import FinanceDataReader as fdr
import streamlit as st
import zerohertzLib as zz


def _color(cnt, alpha=0.99, palette="husl"):
    colors = []
    colors_ = zz.plot.color(cnt, uint8=True, palette=palette)
    if cnt == 1:
        colors_ = [colors_]
    for color_ in colors_:
        colors.append("rgba(" + ",".join(list(map(str, color_))) + f",{alpha})")
    return colors


def get_data(name, symbol, year, method):
    st.session_state["cache"]["name"] = name
    st.session_state["cache"]["symbol"] = symbol
    st.session_state["cache"]["year"] = year
    data = fdr.DataReader(symbol, f"{year}0101")
    st.session_state["cache"]["data"] = data
    xdata = [data_.strftime("%Y/%m/%d") for data_ in data.index]
    st.session_state["cache"]["xdata"] = xdata
    st.session_state["cache"]["method"] = method


def title():
    st.markdown(
        """
        <style>
        .title {
            text-align: center;
        }
        </style>
        <div class="title">
            <h1>⚡️ Zerohertz's Quant Space ⚡️</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )


def warning():
    with st.sidebar:
        st.markdown(
            """
            <style>
            .warning {
                text-align: center;
                bottom: 0;
                color: #800a0a;
            }
            </style>
            <div class="warning">
                <strong>모든 투자의 책임은 본인에게 있습니다.</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
