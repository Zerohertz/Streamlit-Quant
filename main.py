from collections import defaultdict

import streamlit as st
import zerohertzLib as zz

import lib

st.set_page_config(
    page_title="Zerohertz's Quant Space", page_icon="./etc/favicon.ico", layout="wide"
)
lib.util.title()
col1, col2 = st.columns([0.8, 0.2])

lib.init.status()

if not st.session_state["status"]["init"]:
    lib.init.vars()

with st.sidebar:
    name, symbol, year, method = lib.sidebar.upside()

if (
    name != st.session_state["cache"]["name"]
    or year != st.session_state["cache"]["year"]
    or method != st.session_state["cache"]["method"]
):
    if name != st.session_state["cache"]["name"]:
        st.session_state["logger"].info(
            f"""[Cache] Name: {st.session_state["cache"]["name"]} ({st.session_state["cache"]["symbol"]}) -> {name} ({symbol})"""
        )
    if year != st.session_state["cache"]["year"]:
        st.session_state["logger"].info(
            f"""[Cache] Year: {st.session_state["cache"]["year"]} -> {year}"""
        )
    if method != st.session_state["cache"]["method"]:
        st.session_state["logger"].info(
            f"""[Cache] Method: {st.session_state["cache"]["method"]} -> {method}"""
        )
    st.session_state["cache"] = defaultdict(lambda: None)
    st.session_state["logger"].info("[Cache] Clear")
    lib.util.get_data(name, symbol, year, method)
    lib.visual.candle()
    lib.visual.moving_average()
    lib.visual.bollinger_bands()

with st.sidebar:
    lib.sidebar.downside()

with col1:
    lib.visual.main()
    if st.session_state["cache"]["transaction"] is not None:
        lib.visual.transaction()

with col2:
    lib.report.main()

lib.util.warning()
