import streamlit as st
import yfinance as yf
import datetime

# 預設值：股票監控清單
if "watchlist" not in st.session_state:
    st.session_state.watchlist = {
        "2330.TW": {"upper": 950, "lower": 850},   # 台積電
        "2317.TW": {"upper": 180, "lower": 150},   # 鴻海
    }

st.title("📈 股價監控系統 (Web 版)")

# === 股票監控設定 ===
st.header("📊 股票監控清單")
stock = st.text_input("輸入股票代號 (例如 2330.TW)", key="stock_input")
upper = st.number_input("價格上限", min_value=0.0, value=0.0, key="upper_input")
lower = st.number_input("價格下限", min_value=0.0, value=0.0, key="lower_input")

if st.button("➕ 新增監控"):
    if stock:
        st.session_state.watchlist[stock] = {"upper": upper, "lower": lower}
        st.success(f"已新增 {stock}，上限 {upper}，下限 {lower}")

st.write("目前監控清單：", st.session_state.watchlist)

# === 查詢股價 ===
if st.button("🔍 立即檢查股價"):
    for stock, limits in st.session_state.watchlist.items():
        try:
            ticker = yf.Ticker(stock)

            # 先嘗試抓當日分鐘線
            data = ticker.history(period="1d", interval="1m")

            # 如果沒有資料，抓最近 5 天日線，取最後收盤價
            if data.empty:
                data = ticker.history(period="5d", interval="1d")

            if data.empty:
                st.warning(f"{stock} 沒有數據")
                continue

            last_price = data["Close"].iloc[-1]
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 判斷顏色
            if limits.get("upper") and last_price >= limits["upper"]:
                color = "red"
                condition = f"突破上限 {limits['upper']}"
            elif limits.get("lower") and last_price <= limits["lower"]:
                color = "green"
                condition = f"跌破下限 {limits['lower']}"
            else:
                color = "black"
                condition = "正常"

            st.markdown(
                f"<span style='color:{color}; font-weight:bold'>{now} | {stock} 股價：{last_price:.2f} 元 ({condition})</span>",
                unsafe_allow_html=True,
            )

        except Exception as e:
            st.error(f"⚠️ {stock} 查詢失敗: {e}")



