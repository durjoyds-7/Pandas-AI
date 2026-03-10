from flask import Flask, render_template, request,redirect, url_for

from humanizer.pipeline import preprocess_text
from humanizer.rules import word_count, sentence_count

from ai_engine.llm_rewrite import llm_rewrite
from ai_engine.grammar import check_grammar, tool_status
from ai_engine.readability import readability_scores

#NEW: quality modules
from ai_engine.quality import tighten_text, redundancy_suggestions, clarity_report

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    wc = 0
    sc = 0

    grammar_issue_count = 0
    grammar_issues = []
    grammar_status = tool_status()

    readability_flesch = 0.0
    readability_grade = 0.0

    #NEW: quality dashboard vars
    clarity_score = 0
    avg_sentence_length = 0.0
    clarity_tips = []
    tighten_suggestions_ui = []
    redundancy_suggestions_ui = []

    #default thesis-friendly mode
    mode = request.form.get("mode", "thesis")
    strength = request.form.get("strength", "medium")

    if request.method == "POST":
        user_text = request.form.get("text", "")

        if user_text.strip():
            try:
                clean = preprocess_text(user_text)
                if len(clean) > 2000:
                    clean = clean[:2000]

                #LLM rewrite (local)
                #You have llama3:latest installed, so default to that.
                output = llm_rewrite(clean, mode=mode, strength=strength, model="llama3:latest")

                #Quality pipeline on output (tighten + redundancy + clarity)
                tightened, tighten_sugs = tighten_text(output)
                redund_sugs = redundancy_suggestions(tightened)
                clarity = clarity_report(tightened)

                output = tightened  # final output after tightening

                tighten_suggestions_ui = [
                    {"message": s.message, "before": s.before, "after": s.after}
                    for s in tighten_sugs[:8]
                ]
                redundancy_suggestions_ui = [
                    {"message": s.message, "before": s.before, "after": s.after}
                    for s in redund_sugs[:8]
                ]
                clarity_score = clarity.get("score", 0)
                avg_sentence_length = clarity.get("avg_sentence_length", 0.0)
                clarity_tips = clarity.get("tips", [])

                #Insights from final output
                wc = word_count(output)
                sc = sentence_count(output)

                #Grammar suggestions
                issues = check_grammar(output)
                grammar_issue_count = len(issues)
                grammar_issues = [{"message": i.message} for i in issues[:8]]

                #Readability
                rs = readability_scores(output)
                readability_flesch = round(rs.get("flesch_reading_ease", 0.0), 1)
                readability_grade = round(rs.get("flesch_kincaid_grade", 0.0), 1)

            except Exception as e:
                output = f"ERROR: {e}"
        else:
            output = "Input text is empty, please provide a valid text."

    return render_template(
        "index.html",
        output=output,

        # old insights
        word_count=wc,
        sentence_count=sc,
        grammar_issue_count=grammar_issue_count,
        grammar_issues=grammar_issues,
        grammar_status=grammar_status,
        readability_flesch=readability_flesch,
        readability_grade=readability_grade,

        #NEW: quality dashboard
        clarity_score=clarity_score,
        avg_sentence_length=avg_sentence_length,
        clarity_tips=clarity_tips,
        tighten_suggestions=tighten_suggestions_ui,
        redundancy_suggestions=redundancy_suggestions_ui,

        # controls
        mode=mode,
        strength=strength
    )

if __name__ == "__main__":
    app.run(debug=True)
