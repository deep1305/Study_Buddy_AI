from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from src.generator.question_generator import QuestionGenerator
from src.utils.helpers import QuizManager


def _init_session_state() -> None:
    """
    Streamlit reruns the script on every interaction.

    Initialize session state keys once so the app flow is stable.
    """
    if "quiz_manager" not in st.session_state:
        st.session_state["quiz_manager"] = QuizManager()

    if "quiz_generated" not in st.session_state:
        st.session_state["quiz_generated"] = False

    if "quiz_submitted" not in st.session_state:
        st.session_state["quiz_submitted"] = False

    if "saved_results_file" not in st.session_state:
        st.session_state["saved_results_file"] = None


def _reset_quiz() -> None:
    qm: QuizManager = st.session_state["quiz_manager"]
    qm.questions = []
    qm.user_answers = []
    qm.results = []
    st.session_state["quiz_generated"] = False
    st.session_state["quiz_submitted"] = False
    st.session_state["saved_results_file"] = None


def _build_sidebar() -> tuple[str, str, str, int]:
    st.sidebar.header("⚙️ Quiz settings")

    question_type = st.sidebar.selectbox(
        "❓ Question type",
        ["Multiple Choice Question", "Fill in the Blank"],
        index=0,
    )

    topic = st.sidebar.text_input(
        "📚 Topic",
        value=st.session_state.get("topic", ""),
        placeholder="Indian history, Python programming, etc.",
    )

    difficulty = st.sidebar.selectbox("🎯 Difficulty", ["Easy", "Medium", "Hard"], index=1)

    num_questions = st.sidebar.slider(
        "🔢 Number of questions",
        min_value=1,
        max_value=10,
        value=5,
        step=1,
    )

    st.session_state["topic"] = topic
    return question_type, topic, difficulty, num_questions


def main() -> None:
    st.set_page_config(page_title="Study Buddy AI", page_icon="📚", layout="wide")
    load_dotenv()
    _init_session_state()

    st.title("📚 Study Buddy AI")

    question_type, topic, difficulty, num_questions = _build_sidebar()
    qm: QuizManager = st.session_state["quiz_manager"]

    col1, col2 = st.columns([1, 1])
    with col1:
        generate_clicked = st.button("🧠 Generate quiz", type="primary", use_container_width=True)
    with col2:
        clear_clicked = st.button("🧹 Clear", use_container_width=True)

    if clear_clicked:
        _reset_quiz()
        st.rerun()

    if generate_clicked:
        if not topic.strip():
            st.warning("⚠️ Please enter a topic before generating the quiz.")
            st.stop()

        # New quiz => clear old results
        st.session_state["quiz_submitted"] = False

        # Creating the generator can fail if env vars are missing.
        try:
            generator = QuestionGenerator()
        except Exception as e:
            st.error(f"❌ {e}")
            st.stop()

        with st.spinner("⏳ Generating questions..."):
            success = qm.generate_questions(
                generator=generator,
                topic=topic,
                question_type=question_type,
                difficulty=difficulty,
                num_questions=num_questions,
            )

        st.session_state["quiz_generated"] = bool(success)
        st.session_state["quiz_submitted"] = False
        st.rerun()

    if st.session_state["quiz_generated"] and qm.questions:
        st.header("📝 Quiz")
        qm.attempt_quiz()

        if st.button("✅ Submit quiz", type="secondary"):
            qm.evaluate_quiz()
            st.session_state["quiz_submitted"] = True
            st.rerun()

    if not st.session_state["quiz_submitted"]:
        return

    st.header("📊 Results")
    results_df = qm.generate_result_dataframe()
    if results_df.empty:
        st.warning("⚠️ No results to show.")
        return

    correct_count = int(results_df["is_correct"].sum())
    total_questions = int(len(results_df))
    score_percentage = (correct_count / total_questions) * 100 if total_questions else 0.0
    st.metric("🏆 Score", f"{correct_count}/{total_questions}", f"{score_percentage:.1f}%")

    for _, result in results_df.iterrows():
        qn = result["question_number"]
        if bool(result["is_correct"]):
            st.success(f"Question {qn}: {result['question']}")
        else:
            st.error(f"Question {qn}: {result['question']}")
            st.write(f"Your answer: {result['user_answer']}")
            st.write(f"Correct answer: {result['correct_answer']}")

        st.markdown("---")

    # Prefer in-memory download (no container filesystem dependency).
    csv_bytes = results_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download results (CSV)",
        data=csv_bytes,
        file_name="quiz_results.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # Optional: keep the existing save-to-disk behavior too.
    with st.expander("🗂️ Optional: save results to container filesystem"):
        if st.button("💾 Save results to CSV (server)"):
            saved_file = qm.save_to_csv()
            if saved_file:
                st.session_state["saved_results_file"] = saved_file
                st.success(f"✅ Saved to: {saved_file}")

        saved_path = st.session_state.get("saved_results_file")
        if saved_path:
            try:
                with open(saved_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download saved file",
                        data=f.read(),
                        file_name=os.path.basename(saved_path),
                        mime="text/csv",
                        use_container_width=True,
                    )
            except OSError as e:
                st.warning(f"⚠️ Saved file is not accessible: {e}")


if __name__ == "__main__":
    main()


