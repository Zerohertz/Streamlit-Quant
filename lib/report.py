import streamlit as st
import zerohertzLib as zz


def main():
    try:
        script = ""
        if st.session_state["cache"]["qnt"] is not None:
            st.markdown("### :technologist: Today Info")
            today = st.session_state["cache"]["qnt"]()
            title = {
                "Buy": "chart_with_upwards_trend",
                "Sell": "chart_with_upwards_trend",
            }
            logic = {-2: "손절", -1: "매도", 0: "중립", 1: "매수", 2: "추가 매수"}
            script += f"""+ :{title.get(today["position"], "egg")}: Signal Info: {today["total"][1]:.2f}% ({int(today["total"][0])}/{int(st.session_state["cache"]["qnt"].total_cnt)}) → {logic[today["logic"]]}"""

            for key in st.session_state["cache"]["qnt"].methods:
                script += f"""\n\t+ :hammer: {zz.quant.util._method2str(key)}: {today[key][1]:.2f}% ({int(today[key][0])}/{int(st.session_state["cache"]["qnt"].methods_cnt[key])})"""
            script += f"""\n+ :memo: Threshold\n\t+ :arrow_double_up: Buy: {st.session_state["cache"]["qnt"].threshold_buy}\n\t+ :arrow_double_down: Sell: {st.session_state["cache"]["qnt"].threshold_sell}\n"""
        if st.session_state["cache"]["transaction"] is not None:
            script += "### :computer: Backtest Results"
            script += f"""\n+ :money_with_wings: Total Profit: {(st.session_state["cache"]["sell"] - st.session_state["cache"]["buy"]) / st.session_state["cache"]["buy"] * 100:.2f}%"""
            script += f"""\n+ :chart_with_upwards_trend: Total Buy: {zz.quant.util._cash2str(st.session_state["cache"]["buy"], True)}"""
            script += f"""\n+ :chart_with_downwards_trend: Total Sell: {zz.quant.util._cash2str(st.session_state["cache"]["sell"], True)}"""
        if st.session_state["cache"]["qnt"] is not None:
            script += "\n### :information_desk_person: Parameter Info"
            for key in st.session_state["cache"]["qnt"].methods:
                script += f"""\n+ :hammer: {zz.quant.util._method2str(key)}: `{'`, `'.join(st.session_state["cache"]["qnt"].exps_str[key])}`"""
    except ZeroDivisionError:
        script = "### :sob: No Transactions"
    st.markdown(script)
