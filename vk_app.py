import streamlit as st
import pandas as pd
import numpy as np
import re
from collections import Counter

st.set_page_config(page_title="VK Анализ", layout="wide")
st.title("🧠 VK Анализ: Определение ботов и сегментов")

uploaded = st.sidebar.file_uploader("Загрузите таблицу VK (CSV или XLSX)", type=["csv","xlsx"])
if uploaded:
    df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
    df['ВИЗИТ В ВК'] = pd.to_datetime(df['ВИЗИТ В ВК'], errors='coerce')
    first_q = df['group_count'].quantile(0.25)
    bot_thr = df['group_count'].mean() + 2 * df['group_count'].std()
    max_date = df['ВИЗИТ В ВК'].max()
    days_since = (max_date - df['ВИЗИТ В ВК']).dt.days
    df['Тип аккаунта'] = 'пользователь'
    df.loc[(df['group_count']<=first_q) | ((df['group_count']>bot_thr)&(days_since>180)) | (days_since>360), 'Тип аккаунта'] = 'бот'

    VK_THEME2SEGMENT = {
        # вставь сюда свой полный словарь VK_THEME2SEGMENT, который у тебя уже есть
    }

    def define_segment(groups):
        if not groups: return np.nan
        mapped = [VK_THEME2SEGMENT.get(str(g.get("theme","")).lower().strip()) for g in groups if g.get("theme")]
        mapped = [m for m in mapped if m]
        return Counter(mapped).most_common(1)[0][0] if mapped else np.nan

    theme_cols = [c for c in df.columns if re.match(r"group_\\d+_activity$", c)]
    df['segment'] = df.apply(lambda row: define_segment([{"theme":row[c]} for c in theme_cols if pd.notna(row[c])]), axis=1)

    st.subheader("Результаты")
    st.dataframe(df.head())
    st.subheader("Распределение сегментов")
    st.bar_chart(df['segment'].value_counts())

    if st.sidebar.button("Скачать результат"):
        st.download_button("Скачать Excel", df.to_excel(index=False), file_name="vk_analysis.xlsx")

else:
    st.info("Загрузите VK таблицу через левую панель.")
