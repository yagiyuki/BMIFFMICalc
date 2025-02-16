import streamlit as st
import pandas as pd

# --- 補助関数 ---
def format_diff(value):
    """適正値との差分を +○○kg / -○○kg の形式で返す。"""
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f} kg"

# --- BMIテーブル作成 ---
def make_bmi_table(bmi, height, weight):
    """
    BMIの値に応じた分類表をDataFrameで返す関数  
    ※ BMI = 体重(kg) ÷ (身長(m))²  
    ※ 適正体重 = 22 × (身長(m))²  
    """
    ideal_weight = 22 * (height ** 2)
    diff = weight - ideal_weight
    diff_str = format_diff(diff)
    categories = [
        {"range": "18.5未満",     "label": "低体重",      "min": None,  "max": 18.5},
        {"range": "18.5〜25未満", "label": "普通体重",    "min": 18.5,  "max": 25},
        {"range": "25〜30未満",   "label": "肥満（１度）", "min": 25,    "max": 30},
        {"range": "30〜35未満",   "label": "肥満（２度）", "min": 30,    "max": 35},
        {"range": "35〜40未満",   "label": "肥満（３度）", "min": 35,    "max": 40},
        {"range": "40以上",       "label": "肥満（４度）", "min": 40,    "max": None}
    ]
    rows = []
    for cat in categories:
        row = {"範囲": cat["range"], "肥満度": cat["label"], "適正体重": "", "適正体重と比較": "", "BMI": ""}
        in_range = False
        if cat["min"] is None:
            if bmi < cat["max"]:
                in_range = True
        elif cat["max"] is None:
            if bmi >= cat["min"]:
                in_range = True
        else:
            if cat["min"] <= bmi < cat["max"]:
                in_range = True
        if in_range:
            row["適正体重"] = f"{ideal_weight:.2f} kg"
            row["適正体重と比較"] = diff_str
            row["BMI"] = f"{bmi:.2f}"
        rows.append(row)
    return pd.DataFrame(rows)

# --- FFMIテーブル作成 ---
def make_ffmi_table(ffmi, height, fat_free_mass, gender):
    """
    FFMIの値に応じた分類表をDataFrameで返す関数  
    ※ FFMI = 除脂肪体重(kg) ÷ (身長(m))²  
    ※ 除脂肪体重 = 体重 - (体重×体脂肪率/100)  
    ※ 男性: 適正除脂肪体重 = 20×(身長)², 分類範囲: 17,20,23,26  
      女性: 適正除脂肪体重 = 18×(身長)², 分類範囲: 15,18,21,24  
    """
    if gender == "男性":
        ideal_ffm = 20 * (height ** 2)
        categories = [
            {"range": "17未満",     "label": "低FFMI",      "min": None, "max": 17},
            {"range": "17〜20未満", "label": "普通FFMI",    "min": 17,   "max": 20},
            {"range": "20〜23未満", "label": "やや高FFMI",  "min": 20,   "max": 23},
            {"range": "23〜26未満", "label": "高FFMI",      "min": 23,   "max": 26},
            {"range": "26以上",     "label": "非常に高FFMI", "min": 26,   "max": None}
        ]
    else:
        ideal_ffm = 18 * (height ** 2)
        categories = [
            {"range": "15未満",     "label": "低FFMI",      "min": None, "max": 15},
            {"range": "15〜18未満", "label": "普通FFMI",    "min": 15,   "max": 18},
            {"range": "18〜21未満", "label": "やや高FFMI",  "min": 18,   "max": 21},
            {"range": "21〜24未満", "label": "高FFMI",      "min": 21,   "max": 24},
            {"range": "24以上",     "label": "非常に高FFMI", "min": 24,   "max": None}
        ]
    diff = fat_free_mass - ideal_ffm
    diff_str = format_diff(diff)
    rows = []
    for cat in categories:
        row = {"範囲": cat["range"], "分類": cat["label"], "適正除脂肪体重": "", "適正除脂肪体重と比較": "", "FFMI": ""}
        in_range = False
        if cat["min"] is None:
            if ffmi < cat["max"]:
                in_range = True
        elif cat["max"] is None:
            if ffmi >= cat["min"]:
                in_range = True
        else:
            if cat["min"] <= ffmi < cat["max"]:
                in_range = True
        if in_range:
            row["適正除脂肪体重"] = f"{ideal_ffm:.2f} kg (理想FFMI: {ideal_ffm/(height**2):.2f})"
            row["適正除脂肪体重と比較"] = diff_str
            row["FFMI"] = f"{ffmi:.2f}"
        rows.append(row)
    return pd.DataFrame(rows)

# --- FMIテーブル作成 ---
def make_fmi_table(fmi, height, fat_mass, gender):
    """
    FMIの値に応じた分類表をDataFrameで返す関数  
    ※ FMI = 体脂肪量(kg) ÷ (身長(m))²  
    ※ 体脂肪量 = 体重×(体脂肪率/100)  
    ※ 男性: 適正脂肪量 = 6×(身長)², 分類範囲: 3,6,9,12  
      女性: 適正脂肪量 = 10×(身長)², 分類範囲: 8,11,14,17  
    """
    if gender == "男性":
        ideal_fat_mass = 6 * (height ** 2)
        categories = [
            {"range": "3未満",     "label": "低FMI",     "min": None, "max": 3},
            {"range": "3〜6未満",  "label": "普通FMI",   "min": 3,    "max": 6},
            {"range": "6〜9未満",  "label": "やや高FMI", "min": 6,    "max": 9},
            {"range": "9〜12未満", "label": "肥満FMI",   "min": 9,    "max": 12},
            {"range": "12以上",    "label": "高度肥満FMI", "min": 12,   "max": None}
        ]
    else:
        ideal_fat_mass = 10 * (height ** 2)
        categories = [
            {"range": "8未満",     "label": "低FMI",     "min": None, "max": 8},
            {"range": "8〜11未満",  "label": "普通FMI",   "min": 8,    "max": 11},
            {"range": "11〜14未満", "label": "やや高FMI", "min": 11,   "max": 14},
            {"range": "14〜17未満", "label": "肥満FMI",   "min": 14,   "max": 17},
            {"range": "17以上",    "label": "高度肥満FMI", "min": 17,   "max": None}
        ]
    diff = fat_mass - ideal_fat_mass
    diff_str = format_diff(diff)
    rows = []
    for cat in categories:
        row = {"範囲": cat["range"], "分類": cat["label"], "適正脂肪量": "", "適正脂肪量と比較": "", "FMI": ""}
        in_range = False
        if cat["min"] is None:
            if fmi < cat["max"]:
                in_range = True
        elif cat["max"] is None:
            if fmi >= cat["min"]:
                in_range = True
        else:
            if cat["min"] <= fmi < cat["max"]:
                in_range = True
        if in_range:
            row["適正脂肪量"] = f"{ideal_fat_mass:.2f} kg (理想FMI: {ideal_fat_mass/(height**2):.2f})"
            row["適正脂肪量と比較"] = diff_str
            row["FMI"] = f"{fmi:.2f}"
        rows.append(row)
    return pd.DataFrame(rows)

def get_overall_evaluation(bmi, ffmi, fmi, gender):
    """
    BMI, FFMI, FMIの値から体型を総評する一文を返す関数  
    ※ BMIによる基本評価に加え、  
      男性の場合はFFMIが23以上なら「筋肉質」、FMIが9以上なら「体脂肪多め」を付加  
      女性の場合はFFMIが19以上なら「筋肉質」、FMIが14以上なら「体脂肪多め」を付加
    """
    if bmi < 18.5:
        eval_str = "痩せ型"
    elif bmi < 25:
        eval_str = "標準体型"
    elif bmi < 30:
        eval_str = "やや肥満"
    elif bmi < 35:
        eval_str = "肥満"
    elif bmi < 40:
        eval_str = "高度肥満"
    else:
        eval_str = "極度の肥満"
        
    if gender == "男性":
        if ffmi >= 23:
            eval_str += "（筋肉質）"
        if fmi >= 9:
            eval_str += "（体脂肪多め）"
    else:
        if ffmi >= 19:
            eval_str += "（筋肉質）"
        if fmi >= 14:
            eval_str += "（体脂肪多め）"
    return eval_str

# --- Streamlit UI ---
st.title("体脂肪・筋肉評価指標の計算アプリ")

# 性別の選択（ラジオボタンにより、男性か女性のどちらかのみ選択）
gender = st.radio("評価対象の性別を選択してください", ("男性", "女性"), key="gender")

st.header("必要なデータの入力")
# 各入力ウィジェットにキーを指定して前回の入力値を保持
height_cm = st.number_input("身長 (cm)", min_value=0.0, value=170.0, step=0.1, format="%.1f", key="height")
height = height_cm / 100
weight = st.number_input("体重 (kg)", min_value=0.0, value=70.0, step=0.1, format="%.1f", key="weight")
body_fat_percentage = st.number_input("体脂肪率 (%)", min_value=0.0, max_value=100.0, value=20.0, step=0.1, format="%.1f", key="body_fat_percentage")

# 実行ボタン
if st.button("実行"):
    st.header("計算結果")
    if height <= 0:
        st.error("身長は0より大きい値を入力してください。")
    else:
        bmi = weight / (height ** 2)
        fat_mass = weight * (body_fat_percentage / 100)
        fat_free_mass = weight - fat_mass
        ffmi = fat_free_mass / (height ** 2)
        fmi = fat_mass / (height ** 2)
        
        # BMIは共通で表示
        df_bmi = make_bmi_table(bmi, height, weight)
        overall = get_overall_evaluation(bmi, ffmi, fmi, gender)
        
        st.markdown(f"**総評: あなたの体型は {overall} です。**")
        st.markdown("#### BMI (体格指数)")
        st.markdown("**計算式:** BMI = 体重(kg) ÷ (身長(m))²  \n**概要:** 体重と身長から算出され、肥満度の大まかな評価に用いられます。")
        st.table(df_bmi)
        
        if gender == "男性":
            st.markdown("#### FFMI (除脂肪体重指数)【男性基準】")
            st.markdown("**計算式:** FFMI = 除脂肪体重(kg) ÷ (身長(m))²  \n**概要:** 体重から体脂肪量を除いた除脂肪体重を用い、筋肉量の評価に利用されます。\n※ 除脂肪体重 = 体重 - (体重×体脂肪率/100)")
            df_ffmi = make_ffmi_table(ffmi, height, fat_free_mass, "男性")
            st.table(df_ffmi)
            st.markdown("#### FMI (体脂肪量指数)【男性基準】")
            st.markdown("**計算式:** FMI = 体脂肪量(kg) ÷ (身長(m))²  \n**概要:** 体重に占める体脂肪量の割合を評価する指標です。\n※ 体脂肪量 = 体重×(体脂肪率/100)")
            df_fmi = make_fmi_table(fmi, height, fat_mass, "男性")
            st.table(df_fmi)
        else:
            st.markdown("#### FFMI (除脂肪体重指数)【女性基準】")
            st.markdown("**計算式:** FFMI = 除脂肪体重(kg) ÷ (身長(m))²  \n**概要:** 体重から体脂肪量を除いた除脂肪体重を用い、筋肉量の評価に利用されます。\n※ 除脂肪体重 = 体重 - (体重×体脂肪率/100)")
            df_ffmi = make_ffmi_table(ffmi, height, fat_free_mass, "女性")
            st.table(df_ffmi)
            st.markdown("#### FMI (体脂肪量指数)【女性基準】")
            st.markdown("**計算式:** FMI = 体脂肪量(kg) ÷ (身長(m))²  \n**概要:** 体重に占める体脂肪量の割合を評価する指標です。\n※ 体脂肪量 = 体重×(体脂肪率/100)")
            df_fmi = make_fmi_table(fmi, height, fat_mass, "女性")
            st.table(df_fmi)

