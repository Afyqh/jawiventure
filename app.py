
from flask import Flask, render_template, request, jsonify
import csv
import os
import re

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DICTIONARY_FILE = os.path.join(BASE_DIR, "rumi-jawi.tsv")

# Kamus kecil untuk ujian awal.
# Ejaan ini ialah contoh awal dan perlu disemak.
jawi_dictionary = {
    "saya": "ساي",
    "awak": "اوق",
    "makan": "ماکن",
    "minum": "مينوم",
    "buku": "بوکو",
    "rumah": "رومه",
    "sekolah": "سکوله",
    "bahasa": "بهاس",
    "melayu": "ملايو",
    "jawi": "جاوي",
    "suka": "سوک",
    "dan": "دان",
    "ini": "ايني",
    "itu": "ايتو",
    "air": "اءير",
    "ayam": "ايم",
    "bola": "بولا",
    "membaca": "ممباچ",
}


def load_dictionary():
    """Muat pasangan Rumi-Jawi daripada fail TSV jika tersedia."""
    if not os.path.isfile(DICTIONARY_FILE):
        print("Fail kamus tiada; menggunakan kamus contoh.")
        return

    try:
        with open(
            DICTIONARY_FILE,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:
            reader = csv.reader(file, delimiter="\t")
            rows = list(reader)

        if not rows:
            print("Fail kamus kosong.")
            return

        # Cari lajur bernama rumi dan jawi jika tersedia.
        header = [cell.strip().lower() for cell in rows[0]]

        if "rumi" in header and "jawi" in header:
            rumi_index = header.index("rumi")
            jawi_index = header.index("jawi")
            data_rows = rows[1:]
        else:
            # Jika tiada header, anggap dua lajur pertama
            # ialah Rumi dan Jawi.
            rumi_index = 0
            jawi_index = 1
            data_rows = rows

        loaded = 0

        for row in data_rows:
            if len(row) <= max(rumi_index, jawi_index):
                continue

            rumi = row[rumi_index].strip().lower()
            jawi = row[jawi_index].strip()

            if rumi and jawi:
                jawi_dictionary[rumi] = jawi
                loaded += 1

        print(f"Entri kamus dimuatkan: {loaded}")

    except (OSError, csv.Error) as error:
        print(f"Ralat membaca kamus: {error}")


load_dictionary()


def convert_to_jawi(text):
    # Cari perkataan dan kekalkan tanda baca serta jarak.
    pattern = r"[^\W\d_]+(?:[-'’][^\W\d_]+)*"

    def replace_word(match):
        word = match.group(0)
        return jawi_dictionary.get(word.lower(), word)

    return re.sub(pattern, replace_word, text)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/convert", methods=["POST"])
def convert():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")

    if not isinstance(text, str):
        return jsonify({"error": "Input mestilah teks."}), 400

    if not text.strip():
        return jsonify({
            "error": "Sila masukkan teks Rumi dahulu."
        }), 400

    if len(text) > 10000:
        return jsonify({
            "error": "Teks terlalu panjang. Had maksimum ialah 10000 aksara."
        }), 400

    result = convert_to_jawi(text)

    return jsonify({"jawi": result})


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
