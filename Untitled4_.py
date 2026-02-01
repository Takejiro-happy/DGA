import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib

# --- 1. 診断ルール (IEEE Table 6) ---
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

# --- 2. バリセン変換 ---
def pct_to_xy(c2, c3):
    c1 = 100 - c2 - c3
    return c2/100 + c1/200, (c1/100)*np.sqrt(3)/2

# --- Streamlit UI ---
st.title("Duval Triangle 1 診断ツール")

st.sidebar.header("ガス濃度入力 (ppm)")
ch4 = st.sidebar.number_input("CH4 (メタン)", min_value=0.0, value=100.0)
c2h4 = st.sidebar.number_input("C2H4 (エチレン)", min_value=0.0, value=50.0)
c2h2 = st.sidebar.number_input("C2H2 (アセチレン)", min_value=0.0, value=10.0)

if st.button("診断実行"):
    total = ch4 + c2h4 + c2h2
    if total <= 0:
        st.error("ガス濃度を入力してください")
    else:
        C1, C2, C3 = [g/total*100 for g in (ch4, c2h4, c2h2)]
        
        fig, ax = plt.subplots(figsize=(8,8))
        
        step = 0.5 
        xs, ys, ids = [], [], []
        zones = ["PD","T1","T2","T3","D1","D2","DT","ND"]
        colors = {"PD":"#E5CCFF","T1":"#E5E5E5","T2":"#BFE6FF","T3":"#5063B0",
                  "D1":"#FFD6A5","D2":"#FF6F61","DT":"#FF9F9F","ND":"#D3D3D3"}
        z2id = {z:i for i,z in enumerate(zones)}

        for c2_g in np.arange(0, 101, step):
            for c3_g in np.arange(0, 101 - c2_g, step):
                x, y = pct_to_xy(c2_g, c3_g)
                xs.append(x); ys.append(y)
                ids.append(z2id[duval1_zone(100-c2_g-c3_g, c2_g, c3_g)])

        cmap = plt.matplotlib.colors.ListedColormap([colors[z] for z in zones])
        ax.scatter(xs, ys, c=ids, cmap=cmap, s=1, marker='s', alpha=0.4)

        # 三角形の枠
        apex = (0.5, np.sqrt(3)/2)
        ax.plot([0, 1, apex[0], 0], [0, 0, apex[1], 0], 'k', lw=2)

        # --- 修正ポイント1：頂点ラベルの位置をさらに高く設定 ---
        ax.text(0.5, apex[1] + 0.08, "CH4 (100%)", ha="center", fontsize=12, fontweight='bold')
        ax.text(-0.05, -0.05, "C2H2 (100%)", ha="right", va="top", fontsize=12, fontweight='bold')
        ax.text(1.05, -0.05, "C2H4 (100%)", ha="left", va="top", fontsize=12, fontweight='bold')

        # 各ゾーンのラベル
        for z in zones:
            mask = np.array(ids) == z2id[z]
            if np.any(mask):
                xm, ym = np.mean(np.array(xs)[mask]), np.mean(np.array(ys)[mask])
                # --- 修正ポイント2：頂点のPDラベルだけ少し下にずらす ---
                if z == "PD":
                    ym -= 0.03
                ax.text(xm, ym, z, ha="center", va="center", fontsize=10, alpha=0.8, fontweight='bold')

        # 入力データのプロット
        xp, yp = pct_to_xy(C2, C3)
        diag = duval1_zone(C1, C2, C3)
        ax.plot(xp, yp, marker='o', color='red', markersize=15, markeredgecolor='black', markeredgewidth=2)
        
        ax.set_aspect('equal')
        ax.axis('off')
        
        st.pyplot(fig)
        st.success(f"### 診断結果: {diag}")
        st.info(f"計算成分比: CH4={C1:.1f}%, C2H4={C2:.1f}%, C2H2={C3:.1f}%")
