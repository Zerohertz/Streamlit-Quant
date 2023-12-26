import uuid
from collections import defaultdict

import streamlit as st
import zerohertzLib as zz


def status():
    if "status" not in st.session_state:
        st.session_state["status"] = defaultdict(bool)


def vars():
    st.session_state["cache"] = defaultdict(lambda: None)
    st.session_state["logger"] = zz.logging.Logger(str(uuid.uuid4()), logger_level=20)
    st.session_state["data"] = zz.util.Json("./etc/data.json")
    st.session_state["status"]["init"] = True
    st.session_state["logger"].info("[Init] Streamlit")
