import streamlit as st
import pandas as pd
import altair as alt

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
    bmi_colors = ["blue", "green", "orange", "red", "purple", "black"]
    idx, evaluation = get_threshold_index(bmi, bmi_thresholds)
    color = bmi_colors[idx] if idx is not None else "black"
    return evaluation, color, idx, bmi_thresholds

def get_ffmi_evaluation(ffmi, gender):
    if gender == "男性":
        thresholds = [
            {"range": (None, 18.0), "判定": "平均以下の筋肉量"},
            {"range": (18.0, 19.5), "判定": "平均的な筋肉量"},
            {"range": (19.5, 21.0), "判定": "やや筋肉質な体型"},
            {"range": (21.0, 23.0), "判定": "かなり筋肉質な体型"},
            {"range": (23.0, 24.0), "判定": "アスリートレベル"},
            {"range": (24.0, 25.0), "判定": "普通の限界体型"},
            {"range": (25.0, 26.0), "判定": "恵まれている体型"},
            {"range": (26.0, 27.0), "判定": "ゴリマッチョ体型"},
            {"range": (27.0, None), "判定": "人類の限界超え"}
        ]
        colors = ["blue", "green", "teal", "olive", "orange", "red", "purple", "brown", "black"]
    else:
        thresholds = [
            {"range": (None, 14.0), "判定": "平均以下の筋肉量"},
            {"range": (14.0, 16.0), "判定": "平均的な筋肉量"},
            {"range": (16.0, 17.0), "判定": "筋肉質な体型"},
            {"range": (17.0, 18.0), "判定": "かなり筋肉質な体型"},
            {"range": (18.0, 19.0), "判定": "アスリートレベル"},
            {"range": (19.0, 20.0), "判定": "普通の限界体型"},
            {"range": (20.0, None),  "判定": "ステロイドの可能性"}
        ]
        colors = ["blue", "green", "teal", "olive", "orange", "red", "black"]
    idx, evaluation = get_threshold_index(ffmi, thresholds)
    color = colors[idx] if idx is not None else "black"
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

# --- メイン処理 ---

st.title("BMIとFFMIの計算・評価アプリ")

# サイドバー入力
st.sidebar.header("入力データ")
gender = st.sidebar.radio("性別を選択してください:", ("男性", "女性"))
height = st.sidebar.number_input("身長 (cm)", min_value=100.0, max_value=250.0, value=170.0, step=1.0, format="%.1f")
weight = st.sidebar.number_input("体重 (kg)", min_value=30.0, max_value=200.0, value=60.0, step=1.0, format="%.1f")
body_fat = st.sidebar.number_input("体脂肪率 (%)", min_value=0.0, max_value=100.0, value=15.0, step=1.0, format="%.1f")

# 計算
bmi = weight / ((height / 100) ** 2)
lean_mass = weight * (1 - body_fat / 100)
ffmi = lean_mass / ((height / 100) ** 2)

# 評価取得
bmi_eval, bmi_color, bmi_idx, bmi_thresholds = get_bmi_evaluation(bmi)
ffmi_eval, ffmi_color, ffmi_idx, ffmi_thresholds = get_ffmi_evaluation(ffmi, gender)

st.write(f"**性別:** {gender}")
st.write(f"**計算されたBMI:** {round(bmi, 2)} （評価：{bmi_eval}）")
st.write(f"**計算されたFFMI:** {round(ffmi, 2)} （評価：{ffmi_eval}）")

# グラフ表示（2カラム）
col1, col2 = st.columns(2)
with col1:
    data_bmi = pd.DataFrame({"項目": ["BMI"], "値": [bmi]})
    bmi_chart = alt.Chart(data_bmi).mark_bar(color=bmi_color).encode(
        # X軸のタイトルを「BMI値」に変更し、tickラベルは非表示
        x=alt.X("項目", axis=alt.Axis(title="BMI値", labels=False)),
        # Y軸のタイトルは非表示、tickラベルは表示（labels=True）
        y=alt.Y("値", axis=alt.Axis(title=None, labels=True), scale=alt.Scale(domain=[0, max(bmi, 40)]))
    ).properties(width=300)
    st.altair_chart(bmi_chart, use_container_width=False)

with col2:
    data_ffmi = pd.DataFrame({"項目": ["FFMI"], "値": [ffmi]})
    ffmi_chart = alt.Chart(data_ffmi).mark_bar(color=ffmi_color).encode(
        # X軸のタイトルを「FFMI値」に変更し、tickラベルは非表示
        x=alt.X("項目", axis=alt.Axis(title="FFMI値", labels=False)),
        # Y軸のタイトルは非表示、tickラベルは表示（labels=True）
        y=alt.Y("値", axis=alt.Axis(title=None, labels=True), scale=alt.Scale(domain=[0, max(ffmi, 30)]))
    ).properties(width=300)
    st.altair_chart(ffmi_chart, use_container_width=False)

# BMIの判定基準テーブル
bmi_table_data = create_threshold_table(bmi_thresholds, bmi, "BMI値")
st.markdown("### BMIの判定基準")
st.table(pd.DataFrame(bmi_table_data))

# FFMIの判定基準テーブル
ffmi_table_data = create_threshold_table(ffmi_thresholds, ffmi, "FFMI値")
st.markdown("### FFMIの判定基準")
st.table(pd.DataFrame(ffmi_table_data))

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

*例: 体重60kg、体脂肪率15%、身長170cmの場合*  
1. 除脂肪体重 = 60 × (1 - 0.15) = 60 × 0.85 = 51kg  
2. FFMI = 51 ÷ (1.70)^2 ≒ 17.66
""")


