import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib

# --- 診断ルール (IEEE Table 6) ---
def duval1_zone(c1, c2, c3):
    if c1 >= 98: return "PD"
    if c3 < 4:
        if c2 < 20: return "T1"
        if 20 <= c2 < 50: return "T2"
        if c2 >= 50: return "T3"
    if c2 >= 50 and c3 < 15: return "T3"
    if c2 >= 23 and (c3 >= 29 or (13 <= c3 < 29 and c2 < 40)): return "D2"
    if c2 < 23 and c3 >= 13: return "D1"
    if (c2 < 50 and 4 <= c3 < 13) or (40 <= c2 < 50 and 13 <= c3 < 29) or (c2 >= 50 and 15 <= c3 < 29):
        return "DT"
    return "ND"

# --- バリセン変換 ---
def pct_to_xy(c2, c3):
    c1 = 100 - c2 - c3
    return c2/100 + c1/200, (c1/100)*np.sqrt(3)/2

# --- Streamlit UI設定 ---
st.title("Duval Triangle 1 診断ツール")

st.sidebar.header("ガス濃度入力 (ppm)")
ch4 = st.sidebar.number_input("CH₄ (メタン)", min_value=0.0, value=100.0)
c2h4 = st.sidebar.number_input("C₂H₄ (エチレン)", min_value=0.0, value=50.0)
c2h2 = st.sidebar.number_input("C₂H₂ (アセチレン)", min_value=0.0, value=10.0)

if st.button("診断実行"):
    total = ch4 + c2h4 + c2h2
    if total <= 0:
        st.error("ガス濃度を入力してください")
    else:
        C1, C2, C3 = [g/total*100 for g in (ch4, c2h4, c2h2)]
        
        # プロット作成
        fig, ax = plt.subplots(figsize=(7,7))
        # (ここにプロットの描画ロジックを継続...)
        # ※以前のコードをベースに簡略化して表示
        xp, yp = pct_to_xy(C2, C3)
        diag = duval1_zone(C1, C2, C3)
        
        ax.plot(xp, yp, 'ro', ms=10, mec='k')
        apex = (0.5, np.sqrt(3)/2)
        ax.plot([0,1,apex[0],0],[0,0,apex[1],0],'k',lw=2)
        ax.set_aspect('equal')
        ax.axis('off')
        
        st.pyplot(fig)
        st.success(f"診断結果: {diag}")
