import json
import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)


def create_new_session_and_solve_captcha():
  session = requests.Session()
  home_url = "https://infodokan.nagad.us.cc/apilab/svs/"

  base_headers = {
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
  }

  try:
    # ১. প্রথমে হোম পেজে ভিজিট করে ফ্রেশ কুকি (PHPSESSID) জেনারেট করা হচ্ছে
    session.get(home_url, headers=base_headers, timeout=10)

    # ২. এরপর ক্যাপচা ফেচ করা হচ্ছে নতুন সেশন ও কুকি দিয়ে
    captcha_url = (
        "https://infodokan.nagad.us.cc/apilab/svs/backend.php?get_captcha=1"
    )
    res_captcha = session.get(captcha_url, headers=base_headers, timeout=10)
    data = res_captcha.json()

    question = data.get("question", "")
    clean_expr = question.replace("= ?", "").strip()
    solved_value = str(eval(clean_expr))

    return solved_value, session
  except Exception as e:
    print("Session & Captcha Error:", str(e))
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
      "origin": "https://infodokan.nagad.us.cc",
  }

  form_data = {"nid": nid, "dob": dob, "captcha": solved_captcha}
  try:
    res_post = session.post(
        post_url, headers=headers_post, data=form_data, timeout=10
    )
    return res_post.text
  except Exception as e:
    print("NID Request Error:", str(e))
    return None


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
  nid = request.args.get("nid")
  dob = request.args.get("dob")

  if not nid or not dob:
    return jsonify({
        "status": "error",
        "message": "Please provide both 'nid' and 'dob' parameters.",
        "API_OWNER": "DIPTO",
        "CHANNEL": "https://t.me/Xrror_404",
    }), 400

  try:
    # প্রতিবার রিকোয়েস্টে নতুন কুকি ও সেশন তৈরি হবে
    auto_solved_captcha, session = create_new_session_and_solve_captcha()

    if not auto_solved_captcha or not session:
      return jsonify({
          "status": "error",
          "message": (
              "Failed to generate new session or solve captcha automatically!"
          ),
          "API_OWNER": "DIPTO",
          "CHANNEL": "https://t.me/Xrror_404",
      }), 500

    response_text = get_response_for_nid(nid, dob, auto_solved_captcha, session)

    if not response_text:
      return jsonify({
          "status": "error",
          "message": "No response received from target server.",
          "API_OWNER": "DIPTO",
          "CHANNEL": "https://t.me/Xrror_404",
      }), 500

    try:
      raw_json = json.loads(response_text)
    except json.JSONDecodeError:
      return jsonify({
          "status": "error",
          "message": "Invalid JSON response from target server.",
          "raw_response": response_text,
          "API_OWNER": "DIPTO",
          "CHANNEL": "https://t.me/Xrror_404",
      }), 500

    inner_data = raw_json.get("data", {})
    ordered_inner_data = {
        "name": inner_data.get("name", ""),
        "nameEn": inner_data.get("nameEn", ""),
        "nationalId": inner_data.get("nationalId", ""),
        "dateOfBirth": inner_data.get("dateOfBirth", ""),
        "pin": inner_data.get("pin", ""),
        "old_nid": inner_data.get("old_nid", ""),
        "voter_area": inner_data.get("voter_area", ""),
        "birth_place": inner_data.get("birth_place", ""),
        "fatherName": inner_data.get("fatherName", ""),
        "motherName": inner_data.get("motherName", ""),
        "gender": inner_data.get("gender", ""),
        "genderEn": inner_data.get("genderEn", ""),
        "religion": inner_data.get("religion", ""),
        "religionEn": inner_data.get("religionEn", ""),
    }

    formatted_response = {
        "status": "success",
        "data": {
            "code": raw_json.get("code", 200),
            "success": raw_json.get("success", True),
            "message": raw_json.get("message", "NID fetched successfully!"),
            "data": ordered_inner_data,
        },
        "API_OWNER": "DIPTO",
        "CHANNEL": "https://t.me/Xrror_404",
    }

    return jsonify(formatted_response)

  except Exception as e:
    return jsonify({
        "status": "error",
        "message": f"Internal Server Error: {str(e)}",
        "API_OWNER": "DIPTO",
        "CHANNEL": "https://t.me/Xrror_404",
    }), 500


if __name__ == "__main__":
  app.run(debug=True)
