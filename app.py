import streamlit as st
import pandas as pd
import altair as alt
from PIL import Image

# サムネイル（favicon）を設定
im = Image.open("favicon.ico")
st.set_page_config(
    page_title="BMIとFFMIの計算・評価アプリ",  # タイトルを設定
    page_icon=im,  # アイコン画像を指定
)

# --- 関数定義 ---

def get_threshold_index(value, thresholds):
    """
    thresholds: 各要素は {"range": (low, high), "判定": 判定文字列} の辞書
    low または high が None の場合は無制限を意味する
    """
    for i, threshold in enumerate(thresholds):
        low, high = threshold["range"]
        if low is None and value < high:
            return i, threshold["判定"]
        elif high is None and value >= low:
            return i, threshold["判定"]
        elif low is not None and high is not None and low <= value < high:
            return i, threshold["判定"]
    return None, None

def get_bmi_evaluation(bmi):
    bmi_thresholds = [
        {"range": (None, 18.5), "判定": "低体重(痩せ型)"},
        {"range": (18.5, 25),   "判定": "普通体重"},
        {"range": (25, 30),     "判定": "肥満(1度)"},
        {"range": (30, 35),     "判定": "肥満(2度)"},
        {"range": (35, 40),     "判定": "肥満(3度)"},
        {"range": (40, None),   "判定": "肥満(4度)"}
    ]
    bmi_colors = ["blue", "green", "teal", "olive", "orange", "red"]
    idx, evaluation = get_threshold_index(bmi, bmi_thresholds)
    color = bmi_colors[idx] if idx is not None else "black"
    return evaluation, color, idx, bmi_thresholds

def shift_threshold_ranges(thresholds, shift):
    """
    指定された thresholds の各 range 値に対して一律で shift を加算/減算する。
    None はそのまま（上限 or 下限なし）として扱う。
    """
    new_thresholds = []
    for t in thresholds:
        low, high = t["range"]
        
        new_low = None if low is None else low + shift
        new_high = None if high is None else high + shift
        
        new_thresholds.append({
            "range": (new_low, new_high),
            "判定": t["判定"]
        })
    return new_thresholds

def get_ffmi_evaluation(ffmi, gender):
    # 男性の基準値を定義
    male_thresholds = [
        {"range": (None, 18.0),  "判定": "平均以下の筋肉量"},
        {"range": (18.0, 19.5),  "判定": "平均的な筋肉量"},
        {"range": (19.5, 20.5),  "判定": "やや筋肉質な体型"},
        {"range": (20.5, 21.5),  "判定": "筋肉質な体型"},
        {"range": (21.5, 22.5),  "判定": "かなり筋肉質な体型"},
        {"range": (22.5, 23.5),  "判定": "ボディビルなどの競技者レベル"},
        {"range": (23.5, 25.0),  "判定": "ナチュラルの限界付近"},
        {"range": (25.0, None),  "判定": "恵まれている人が到達できる体型、ナチュラルが疑われる"}
    ]

    if gender == "男性":
        thresholds = male_thresholds
    else:
        # 女性の場合は男性の閾値から4ポイント引いたものを採用
        thresholds = shift_threshold_ranges(male_thresholds, -4.0)

    # 色のリスト（ユーザビリティを考慮）
    colors = ["blue", "green", "teal", "yellowgreen", "gold", "darkorange", "orangered", "red"]
    idx, evaluation = get_threshold_index(ffmi, thresholds)
    color = colors[idx]
    return evaluation, color, idx, thresholds

def format_range_str(low, high):
    if low is None:
        return f"{high}未満"
    elif high is None:
        return f"{low}以上"
    else:
        return f"{low}～{high}未満"

def create_threshold_table(thresholds, value, value_label):
    table_data = []
    for i, threshold in enumerate(thresholds):
        low, high = threshold["range"]
        range_str = format_range_str(low, high)
        table_data.append({
            value_label: range_str,
            "判定": threshold["判定"],
            f"あなたの{value_label}": ""
        })
    idx, _ = get_threshold_index(value, thresholds)
    table_data[idx][f"あなたの{value_label}"] = str(round(value, 2))
    return table_data

def calc_bmi(height, weight):
    return weight / ((height / 100) ** 2)

def calc_ffmi(height, weight, body_fat):
    lean_mass = weight * (1 - body_fat / 100)
    return lean_mass / ((height / 100) ** 2)

# --- メイン処理 ---

st.title("BMIとFFMIの計算・評価アプリ")

# サイドバー入力
gender = st.radio("性別:", ("男性", "女性"), index=0, horizontal=True)

# 横並びのレイアウトを作成
col1, col2, col3 = st.columns(3)
with col1:
    height = st.number_input("身長 (cm)", min_value=100.0, max_value=250.0, value=170.0, step=1.0, format="%.1f")
with col2:
    weight = st.number_input("体重 (kg)", min_value=30.0, max_value=200.0, value=60.0, step=1.0, format="%.1f")
with col3:
    body_fat = st.number_input("体脂肪率 (%)", min_value=0.0, max_value=100.0, value=15.0, step=1.0, format="%.1f")

# 計算
bmi  = calc_bmi(height, weight)
ffmi = calc_ffmi(height, weight, body_fat)

# 評価取得
bmi_eval, bmi_color, bmi_idx, bmi_thresholds = get_bmi_evaluation(bmi)
ffmi_eval, ffmi_color, ffmi_idx, ffmi_thresholds = get_ffmi_evaluation(ffmi, gender)

st.markdown("### 計算結果")
st.write(f"**性別:** {gender}")
col1, col2 = st.columns(2)

with col1:
    st.metric(label="BMI", value=f"{round(bmi, 2)}", delta=f"{bmi_eval}", delta_color='off')

with col2:
    st.metric(label="FFMI", value=f"{round(ffmi, 2)}", delta=f"{ffmi_eval}", delta_color='off')

# 最大値を統一
max_value = max(bmi, ffmi, 40)  # 最低40を保証
graph_width = 400

# 1つのデータフレームにまとめる
data = pd.DataFrame({
    "指標": ["BMI", "FFMI"],
    "値": [bmi, ffmi]
})

# Altairで2バーをまとめて描画
chart = (
    alt.Chart(data)
    .mark_bar()
    .encode(
        # X軸に「BMI」「FFMI」を、Y軸に値を対応づけ
        x=alt.X("指標:N", axis=alt.Axis(title=None)),
        y=alt.Y("値:Q", axis=alt.Axis(title=None), scale=alt.Scale(domain=[0, max_value])),
        # 指標ごとに色を分けたい場合: カラーに「指標」を指定し、scaleでカラーを指定
        color=alt.Color(
            "指標:N", 
            scale=alt.Scale(domain=["BMI", "FFMI"], range=[bmi_color, ffmi_color])
        )
    )
    .properties(width=graph_width, height=300)
)

st.altair_chart(chart, use_container_width=True)

st.markdown("---")

# BMIの判定基準テーブル
bmi_table_data = create_threshold_table(bmi_thresholds, bmi, "BMI値")
st.markdown("### BMIの判定基準")
st.table(pd.DataFrame(bmi_table_data))

# FFMIの判定基準テーブル
ffmi_table_data = create_threshold_table(ffmi_thresholds, ffmi, "FFMI値")
st.markdown("### FFMIの判定基準")
st.table(pd.DataFrame(ffmi_table_data))

if gender == "女性":
    st.markdown("※女性のFFMIは男性から4ポイント引いたものを基準にしています")

# 計算式の説明
st.markdown("""
---
### BMI（Body Mass Index）計算式
BMI = 体重 (kg) ÷ (身長 (m))^2

*例: 身長170cm、体重60kgの場合*  
1. 身長をメートルに変換: 170cm = 1.70m  
2. BMI = 60 ÷ (1.70)^2 ≒ 20.76

### FFMI（Fat Free Mass Index）計算式
除脂肪体重 = 体重 × (1 - 体脂肪率 / 100)  
FFMI = 除脂肪体重 (kg) ÷ (身長 (m))^2

*例: 身長170cm、体重60kg、体脂肪率15%の場合*  
1. 除脂肪体重 = 60 × (1 - 0.15) = 60 × 0.85 = 51kg  
2. FFMI = 51 ÷ (1.70)^2 ≒ 17.66
---
<small>
【免責事項】
本ツールは、BMIおよびFFMIの概算値を計算し、一般的な指標に基づいて評価を提供するものです。
表示される情報はあくまで参考であり、医学的な診断やアドバイスを提供するものではありません。
ご自身の健康状態に関するご相談は、必ず医師や専門家にご相談ください。
</small>

""", unsafe_allow_html=True)

