from datetime import datetime

import pandas as pd
import streamlit as st


def load_css(file_name):
    with open(file_name, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


st.set_page_config(page_title="試打評価シート", layout="wide")
load_css("style.css")
st.title("試打評価シート")

# ----------------------------
# 1. マスターデータ
# ----------------------------
RACKETS = [
    "PP Tour",
    "PP 100",
    "PP Team",
    "PP Lite",
    "PA 100",
    "PD 100",
    "PS 16/19",
    "SPEED",
    "GRAVITY",
]

# 総合点を除く、手入力する11項目
INPUT_ITEMS = [
    "第一印象（デザイン）",
    "打球感",
    "振動吸収性",
    "振り抜き",
    "ボールの乗り感",
    "面の安定性",
    "パワー性能",
    "スピン性能",
    "コントロール性能",
    "スイートエリアの広さ",
    "打球音",
]

# ----------------------------
# 2. 参加者名入力
# ----------------------------
participant_name = st.text_input("名前")

if participant_name:
    st.write(f"入力者: {participant_name}")

# ----------------------------
# 3. session_stateの初期化
# ----------------------------
if "form_data" not in st.session_state:
    st.session_state.form_data = {}

if "generated_csv_text" not in st.session_state:
    st.session_state.generated_csv_text = None

if "generated_csv_filename" not in st.session_state:
    st.session_state.generated_csv_filename = None

if "score_one_fields" not in st.session_state:
    st.session_state.score_one_fields = []

if participant_name and participant_name not in st.session_state.form_data:
    st.session_state.form_data[participant_name] = {}
    for racket in RACKETS:
        st.session_state.form_data[participant_name][racket] = {
            "第一印象（デザイン）": None,
            "打球感": None,
            "振動吸収性": None,
            "振り抜き": None,
            "ボールの乗り感": None,
            "面の安定性": None,
            "パワー性能": None,
            "スピン性能": None,
            "コントロール性能": None,
            "スイートエリアの広さ": None,
            "打球音": None,
            "コメント": "",
        }

# 参加者名が変わったときに、前のCSV生成結果をクリア
if "last_participant_name" not in st.session_state:
    st.session_state.last_participant_name = None

if participant_name != st.session_state.last_participant_name:
    st.session_state.generated_csv_text = None
    st.session_state.generated_csv_filename = None
    st.session_state.score_one_fields = []
    st.session_state.last_participant_name = participant_name


# ----------------------------
# 4. 関数
# ----------------------------
def get_score_one_fields(name):
    """1点が入っている項目一覧を返す。"""
    score_one_items = []

    for racket in RACKETS:
        data = st.session_state.form_data[name][racket]
        for item in INPUT_ITEMS:
            if data[item] == 1:
                score_one_items.append((racket, item))

    return score_one_items


def calculate_total_score(name, racket):
    """
    総合点を自動計算する。
    今回は11項目の平均点を、小数1桁で返す。
    """
    data = st.session_state.form_data[name][racket]
    values = [data[item] for item in INPUT_ITEMS if data[item] is not None]

    if len(values) != len(INPUT_ITEMS):
        return None

    return round(sum(values) / len(values), 1)


def build_export_dataframe(name):
    """CSV出力用のDataFrameを作る。"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = []

    for racket in RACKETS:
        data = st.session_state.form_data[name][racket]
        total_score = calculate_total_score(name, racket)

        row = {
            "timestamp": now,
            "participant_name": name,
            "racket": racket,
            "第一印象（デザイン）": data["第一印象（デザイン）"],
            "打球感": data["打球感"],
            "振動吸収性": data["振動吸収性"],
            "振り抜き": data["振り抜き"],
            "ボールの乗り感": data["ボールの乗り感"],
            "面の安定性": data["面の安定性"],
            "パワー性能": data["パワー性能"],
            "スピン性能": data["スピン性能"],
            "コントロール性能": data["コントロール性能"],
            "スイートエリアの広さ": data["スイートエリアの広さ"],
            "打球音": data["打球音"],
            "総合点": total_score,
            "コメント": data["コメント"],
        }
        rows.append(row)

    return pd.DataFrame(rows)


# ----------------------------
# 5. 入力画面
# ----------------------------
if participant_name:
    st.write("それぞれのラケットタブで入力してください。")
    st.write("※ 総合点は11項目の平均点として自動計算されます。")
    st.write("※ 1〜10をスライダーで選択してください。")

    tabs = st.tabs(RACKETS)

    for i, racket in enumerate(RACKETS):
        with tabs[i]:
            st.markdown(
                f"""
                <div class="sticky-racket-name">
                    {racket} を評価中
                </div>
                """,
                unsafe_allow_html=True
            )

            data = st.session_state.form_data[participant_name][racket]

            # 11項目の入力欄
            for item in INPUT_ITEMS:
                current_value = data[item]
                key_name = f"{participant_name}_{racket}_{item}"

                if current_value is None:
                    slider_value = 1
                else:
                    slider_value = current_value

                selected_value = st.select_slider(
                    item,
                    options=list(range(1, 11)),
                    value=slider_value,
                    key=key_name,
                )

                st.session_state.form_data[participant_name][racket][item] = selected_value

            # 総合点の自動表示
            total_score = calculate_total_score(participant_name, racket)

            st.markdown("### 総合点（自動計算）")
            if total_score is None:
                st.info("11項目がすべて入力されると、自動で総合点が表示されます。")
            else:
                st.success(f"総合点: {total_score}")

            # コメント欄（任意）
            comment_key = f"{participant_name}_{racket}_comment"
            current_comment = data["コメント"]

            comment = st.text_area(
                "コメント（任意・200文字まで）",
                value=current_comment,
                max_chars=200,
                height=120,
                key=comment_key,
            )

            st.session_state.form_data[participant_name][racket]["コメント"] = comment

    # ----------------------------
    # 6. 確認表示
    # ----------------------------
    st.write("## 入力内容の確認")

    # 点数確認用の表を作る
    score_table_data = {}

    for racket in RACKETS:
        data = st.session_state.form_data[participant_name][racket]

        racket_scores = {}
        for item in INPUT_ITEMS:
            racket_scores[item] = data[item] if data[item] is not None else ""

        total_score = calculate_total_score(participant_name, racket)
        racket_scores["総合点"] = total_score if total_score is not None else ""

        score_table_data[racket] = racket_scores

    score_df = pd.DataFrame(score_table_data)

    st.write("### 点数一覧")
    st.dataframe(score_df, use_container_width=True)

    # コメント確認用の表を作る
    comment_rows = []
    for racket in RACKETS:
        data = st.session_state.form_data[participant_name][racket]
        comment_rows.append(
            {
                "ラケット": racket,
                "コメント": data["コメント"] if data["コメント"].strip() != "" else "",
            }
        )

    comment_df = pd.DataFrame(comment_rows)

    st.write("### コメント一覧")
    st.dataframe(comment_df, use_container_width=True)

    # ----------------------------
    # 7. CSV作成・ダウンロード
    # ----------------------------
    if st.button("CSVを作成する"):
        export_df = build_export_dataframe(participant_name)

        st.session_state.generated_csv_text = export_df.to_csv(index=False, encoding="utf-8-sig")
        st.session_state.generated_csv_filename = f"{participant_name}_racket_evaluation.csv"
        st.session_state.score_one_fields = get_score_one_fields(participant_name)

    if st.session_state.generated_csv_text is not None:
        if st.session_state.score_one_fields:
            st.warning("1点が入っている項目があります。意図した評価か確認してください。", icon="⚠️")

            st.write("### 1点の項目一覧")
            for racket, item in st.session_state.score_one_fields:
                st.write(f"- {racket} / {item} → 評価しましたか？")
        else:
            st.success("CSVを作成しました。")

        st.write("### 次のステップ")
        st.write("CSVをダウンロードして、管理者へメールで送信してください。")

        st.download_button(
            label="CSVをダウンロード",
            data=st.session_state.generated_csv_text,
            file_name=st.session_state.generated_csv_filename,
            mime="text/csv",
        )

else:
    st.info("名前を入力すると進みます。")