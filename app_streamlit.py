import streamlit as st
import yfinance as yf
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 預設值：股票監控清單
if "watchlist" not in st.session_state:
    st.session_state.watchlist = {
        "2330.TW": {"upper": 950, "lower": 850},   # 台積電
        "2317.TW": {"upper": 180, "lower": 150},   # 鴻海
    }

st.title("📈 股價監控系統 (Web 版)")

# === Email 設定（讀取 Streamlit Secrets） ===
try:
    EMAIL_SENDER = st.secrets["EMAIL_SENDER"]
    EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
    EMAIL_RECEIVER = st.secrets["EMAIL_RECEIVER"]
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
except Exception:
    st.sidebar.warning("⚠️ 尚未設定 Secrets，請到 Streamlit Cloud > Settings > Secrets 新增 EMAIL_SENDER / EMAIL_PASSWORD / EMAIL_RECEIVER")
    EMAIL_SENDER = EMAIL_PASSWORD = EMAIL_RECEIVER = ""

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

# === 發送 Email ===
def send_email_alert(stock, price, condition):
    if not EMAIL_SENDER or not EMAIL_RECEIVER or not EMAIL_PASSWORD:
        st.warning("⚠️ 尚未設定 Email，無法發送通知")
        return

    subject = f"⚡ 股價提醒：{stock} {condition} {price} 元"
    body = f"""
時間：{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
股票：{stock}
當前股價：{price:.2f} 元
觸發條件：{condition}
    """
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        st.info(f"📧 已發送 Email 提醒: {subject}")
    except Exception as e:
        st.error(f"⚠️ Email 發送失敗: {e}")

# === 查詢股價 ===
if st.button("🔍 立即檢查股價"):
    for stock, limits in st.session_state.watchlist.items():
        try:
            ticker = yf.Ticker(stock)
            data = ticker.history(period="1d", interval="1m")
            if data.empty:
                st.warning(f"{stock} 沒有數據")
                continue
            last_price = data["Close"].iloc[-1]
            st.write(f"{datetime.datetime.now()} | {stock} 股價：{last_price:.2f} 元")

            if limits.get("upper") and last_price >= limits["upper"]:
                send_email_alert(stock, last_price, f"突破上限 {limits['upper']}")
            if limits.get("lower") and last_price <= limits["lower"]:
                send_email_alert(stock, last_price, f"跌破下限 {limits['lower']}")
        except Exception as e:
            st.error(f"⚠️ {stock} 查詢失敗: {e}")
