# 기술 트렌드 분석 대시보드
import json
import pandas as pd
import streamlit as st
import plotly.express as px
import os

st.set_page_config(page_title="기술 트렌드 대시보드", layout="wide")

try:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, "data", "dashboard_data.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    st.error("dashboard_data.json 파일 없음")
    st.stop()

st.title("기술 트렌드 분석 대시보드")
st.caption("dev.to 글 태그 분석 + Word2Vec 임베딩 + K-means 군집화")

tab1, tab2, tab3 = st.tabs(["트렌드", "카테고리", "함께 공부할 기술"])

# 트렌드: 많이 언급된 태그
with tab1:
    st.subheader("가장 많이 언급된 기술 (상위 30)")
    trend = pd.DataFrame(data["trend"])
    fig = px.bar(
        trend.sort_values("count"),
        x="count", y="tag", orientation="h",
        labels={"count": "글 수", "tag": "기술"},
        height=750,
    )
    st.plotly_chart(fig, use_container_width=True)

# 카테고리: K-means 클러스터
with tab2:
    st.subheader("자동으로 묶인 기술 카테고리")
    st.caption("비슷한 맥락에서 함께 쓰인 태그끼리 묶었습니다.")
    clusters = pd.DataFrame(data["clusters"])
    cols = st.columns(2)
    for i, cid in enumerate(sorted(clusters["cluster"].unique())):
        tags = clusters[clusters["cluster"] == cid]["tag"].tolist()
        with cols[i % 2]:
            st.markdown("**카테고리 %d** — %d개" % (cid+1, len(tags)))
            st.write(", ".join(tags))

# 추천: 같이 공부하면 좋은 기술
with tab3:
    st.subheader("이 기술이랑 같이 공부하면 좋은 것")
    techs = sorted(data["recommend"].keys())
    pick = st.selectbox("기술을 고르세요", techs)
    recs = data["recommend"].get(pick, [])
    if recs:
        rdf = pd.DataFrame(recs, columns=["기술", "유사도"])
        fig2 = px.bar(
            rdf.sort_values("유사도"),
            x="유사도", y="기술", orientation="h",
            range_x=[0, 1], height=350,
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.dataframe(rdf, use_container_width=True)
    else:
        st.info("이 기술은 추천 데이터가 없습니다")