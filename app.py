import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="รายงานการตายต่อประชากรแสนคน",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 แดชบอร์ดวิเคราะห์สถิติการตายต่อประชากรแสนคน (ปี 2566 - 2568)")
st.write("เว็บแอปพลิเคชันวิเคราะห์สาเหตุการตายและอัตราการตายต่อประชากรแสนคนในประเทศไทย")

# 2. โหลดและทำความสะอาดข้อมูลจาก cod.csv
@st.cache_data
def load_data():
    df = pd.read_csv("cod.csv")
    # ทำความสะอาดคอลัมน์ 'จำนวน' (ลบเครื่องหมาย Comma และแปลงเป็นตัวเลข)
    df["จำนวน_ตัวเลข"] = df["จำนวน"].astype(str).str.replace(",", "").astype(float)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"ไม่สามารถโหลดไฟล์ cod.csv ได้: {e}")
    st.stop()

# 3. Interactive Widgets (Sidebar Filters)
st.sidebar.header("🔍 ตัวกรองข้อมูล (Filters)")

# Widget 1: เลือกปี พ.ศ.
year_list = sorted(df["ปี"].unique())
selected_year = st.sidebar.selectbox("เลือกปี พ.ศ.:", options=year_list, index=len(year_list)-1)

# Widget 2: Slider เลือกจำนวนสาเหตุการตายอันดับแรก (Top N)
top_n = st.sidebar.slider("เลือกจำนวนอันดับสาเหตุการตาย (Top N):", min_value=3, max_value=18, value=10)

# Widget 3: Multiselect เลือกเปรียบเทียบสาเหตุการตายเฉพาะกลุ่ม
all_causes = list(df["สาเหตุการตาย"].unique())
selected_causes = st.sidebar.multiselect(
    "เลือกสาเหตุการตายเพื่อดูแนวโน้มรายปี:",
    options=all_causes,
    default=all_causes[:5]
)

# กรองข้อมูลตามปีที่เลือก
df_year = df[df["ปี"] == selected_year].sort_values(by="อัตราต่อแสนประชากร", ascending=False)
df_top_n = df_year.head(top_n)

# 4. แสดง Key Metrics
col1, col2, col3 = st.columns(3)
col1.metric("อัตราการตายรวม (ต่อแสนประชากร)", f"{df_year['อัตราต่อแสนประชากร'].sum():,.2f}")
col2.metric("จำนวนผู้เสียชีวิตรวม (คน)", f"{int(df_year['จำนวน_ตัวเลข'].sum()):,}")
top_cause_name = df_year.iloc[0]["สาเหตุการตาย"] if not df_year.empty else "-"
col3.metric("สาเหตุอันดับ 1", top_cause_name)

st.markdown("---")

# 5. แสดงกราฟ 2 กราฟ
col_chart1, col_chart2 = st.columns(2)

# กราฟที่ 1: Bar Chart แสดงสถิติอันดับสาเหตุการตายในปีที่เลือก
with col_chart1:
    st.subheader(f"📊 กราฟที่ 1: {top_n} อันดับสาเหตุการตาย (ปี {selected_year})")
    fig1 = px.bar(
        df_top_n,
        x="อัตราต่อแสนประชากร",
        y="สาเหตุการตาย",
        orientation="h",
        color="อัตราต่อแสนประชากร",
        color_continuous_scale="Reds",
        text_auto=".2f",
        labels={"อัตราต่อแสนประชากร": "อัตราต่อแสนประชากร", "สาเหตุการตาย": "สาเหตุการตาย"},
        title=f"อัตราการตายต่อประชากรแสนคน ปี {selected_year}"
    )
    fig1.update_layout(yaxis={"categoryorder": "total ascending"}, height=500)
    st.plotly_chart(fig1, use_container_width=True)

# กราฟที่ 2: Line Chart แสดงแนวโน้มการตายรายปี (2566 - 2568)
with col_chart2:
    st.subheader("📈 กราฟที่ 2: แนวโน้มอัตราการตายรายปี (2566 - 2568)")
    df_filtered_causes = df[df["สาเหตุการตาย"].isin(selected_causes)]
    fig2 = px.line(
        df_filtered_causes,
        x="ปี",
        y="อัตราต่อแสนประชากร",
        color="สาเหตุการตาย",
        markers=True,
        labels={"ปี": "ปี พ.ศ.", "อัตราต่อแสนประชากร": "อัตราต่อแสนประชากร"},
        title="แนวโน้มอัตราการตายต่อแสนประชากรแยกตามสาเหตุ"
    )
    fig2.update_layout(xaxis=dict(tickmode='linear', tick0=2566, dtick=1), height=500)
    st.plotly_chart(fig2, use_container_width=True)

# 6. แสดงตารางข้อมูล
st.markdown("---")
st.subheader(f"📋 ตารางข้อมูลสถิติปี {selected_year}")
display_cols = ["ปี", "รหัสโรค", "สาเหตุการตาย", "จำนวน", "อัตราต่อแสนประชากร", "แหล่งที่มา"]
st.dataframe(df_year[display_cols], use_container_width=True)