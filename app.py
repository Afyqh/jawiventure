
from flask import Flask, render_template, request, jsonify
import csv
import os
import re

app = Flask(__name__)

# Load the Rumi-Jawi dictionary once when the app starts.
DICTIONARY_FILE = os.path.join(
    os.path.dirname(__file__), "rumi-jawi.tsv"
)

jawi_dictionary = {}

try:
    with open(
        DICTIONARY_FILE, "r", encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file, delimiter="\t")

        for row in reader:
            rumi = row["rumi"].strip().lower()
            jawi = row["jawi"].strip()

            if rumi and jawi:
                # Keep the first spelling if a word has
                # more than one entry.
                if rumi not in jawi_dictionary:
                    jawi_dictionary[rumi] = jawi

except FileNotFoundError:
    print("Warning: rumi-jawi.tsv was not found.")


def convert_to_jawi(text):
    # Match Malay words, including hyphenated words.
    pattern = r"[^\W\d_]+(?:[-'’][^\W\d_]+)*"

    def replace_word(match):
        word = match.group(0)
        result = jawi_dictionary.get(word.lower())

        # Keep unknown words unchanged.
        if result is None:
            return word

        # Preserve basic uppercase formatting.
        if word.isupper():
            return result.upper()

        if word.istitle():
            return result

        return result

    return re.sub(pattern, replace_word, text)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/convert", methods=["POST"])
def convert():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")

    if not isinstance(text, str):
        return jsonify({"error": "Input mesti berupa teks."}), 400

    if not text.strip():
        return jsonify({"error": "Sila masukkan teks Rumi dahulu."}), 400

    if len(text) > 10000:
        return jsonify({"error": "Teks terlalu panjang."}), 400

    result = convert_to_jawi(text)

    return jsonify({"jawi": result})


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
