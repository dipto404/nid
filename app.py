import json
import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)


def solve_captcha_automatically():
  captcha_url = (
      "https://infodokan.nagad.us.cc/apilab/svs/backend.php?get_captcha=1"
  )
  headers_get = {
      "Host": "infodokan.nagad.us.cc",
      "sec-ch-ua-platform": '"Android"',
      "user-agent": (
          "Mozilla/5.0 (Linux; Android 11; Redmi Note 8 Build/RKQ1.201004.002)"
          " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.8037.106 Mobile"
          " Safari/537.36"
      ),
      "sec-ch-ua": '"Chromium";v="154", "Android WebView";v="154", "Not A(Brand";v="99"',
      "sec-ch-ua-mobile": "?1",
      "accept": "*/*",
      "x-requested-with": "mark.via.gp",
      "sec-fetch-site": "same-origin",
      "sec-fetch-mode": "cors",
      "sec-fetch-dest": "empty",
      "referer": "https://infodokan.nagad.us.cc/apilab/svs/",
      "accept-language": "en-US,en;q=0.9",
      "priority": "u=1, i",
      "cookie": "PHPSESSID=f0lf5kiku0s91utb9vk71sicip",
  }

  try:
    session = requests.Session()
    res_captcha = session.get(captcha_url, headers=headers_get, timeout=10)
    data = res_captcha.json()
    question = data.get("question", "")
    clean_expr = question.replace("= ?", "").strip()
    solved_value = str(eval(clean_expr))
    return solved_value, session
  except Exception as e:
    print("Captcha Solving Error:", e)
    return "", None


def get_response_for_nid(nid, dob, solved_captcha, session):
  post_url = "https://infodokan.nagad.us.cc/apilab/svs/backend.php"

  headers_post = {
      "Host": "infodokan.nagad.us.cc",
      "sec-ch-ua-platform": '"Android"',
      "user-agent": (
          "Mozilla/5.0 (Linux; Android 11; Redmi Note 8 Build/RKQ1.201004.002)"
          " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.8037.106 Mobile"
          " Safari/537.36"
      ),
      "sec-ch-ua": '"Chromium";v="154", "Android WebView";v="154", "Not A(Brand";v="99"',
      "sec-ch-ua-mobile": "?1",
      "accept": "*/*",
      "x-requested-with": "mark.via.gp",
      "sec-fetch-site": "same-origin",
      "sec-fetch-mode": "cors",
      "sec-fetch-dest": "empty",
      "referer": "https://infodokan.nagad.us.cc/apilab/svs/",
      "accept-language": "en-US,en;q=0.9",
      "priority": "u=1, i",
      "cookie": "PHPSESSID=f0lf5kiku0s91utb9vk71sicip",
      "origin": "https://infodokan.nagad.us.cc",
  }

  form_data = {"nid": nid, "dob": dob, "captcha": solved_captcha}
  res_post = session.post(
      post_url, headers=headers_post, data=form_data, timeout=10
  )
  return res_post.text


@app.route("/", methods=["GET"])
def home():
  return jsonify({
      "status": "Running",
      "usage": "/api?nid=YOUR_NID&dob=YYYY-MM-DD",
      "API_OWNER": "DIPTO",
      "CHANNEL": "https://t.me/Xrror_404",
  })


@app.route("/api", methods=["GET"])
def query_nid():
  # শুধুমাত্র GET মেথডের মাধ্যমে nid ও dob ইনপুট নেওয়া হচ্ছে
  nid = request.args.get("nid")
  dob = request.args.get("dob")

  if not nid or not dob:
    return jsonify({
        "error": (
            "দয়া করে সঠিক নিয়মে nid এবং dob প্রদান করুন। যেমন:"
            " /api?nid=YOUR_NID&dob=YYYY-MM-DD"
        ),
        "API_OWNER": "DIPTO",
        "CHANNEL": "https://t.me/Xrror_404",
    }), 400

  auto_solved_captcha, session = solve_captcha_automatically()

  if auto_solved_captcha and session:
    response_text = get_response_for_nid(nid, dob, auto_solved_captcha, session)
    try:
      json_data = json.loads(response_text)
    except json.JSONDecodeError:
      json_data = {"response": response_text}

    json_data["API_OWNER"] = "DIPTO"
    json_data["CHANNEL"] = "https://t.me/Xrror_404"
    return jsonify(json_data)
  else:
    return jsonify({
        "error": "ক্যাপচা স্বয়ংক্রিয়ভাবে সমাধান করতে ব্যর্থ হয়েছে!",
        "API_OWNER": "DIPTO",
        "CHANNEL": "https://t.me/Xrror_404",
    }), 500


if __name__ == "__main__":
  app.run(debug=True)
