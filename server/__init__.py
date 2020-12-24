from flask import Flask, make_response, render_template, request, jsonify, session
from flask.sessions import SecureCookieSessionInterface
from flask_wtf.csrf import CSRFProtect
from . import mongo_util

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gh48hfsjkdh943uro2jf92pafj483la3'
csrf = CSRFProtect(app)
indexPage = {
    "title": "TUL Esports - LoL",
    "summonerNameFormLabel": "Summoner Name",
    "regionFormLabel": "Region",
    "getStatsFormButton": "Get Stats",
}

@app.after_request
def apply_sec_headers(response):
    # Setting CSP (more info: https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
    response.headers[
        "Content-Security-Policy"] = "default-src 'none'; script-src 'self' https://hcaptcha.com https://*.hcaptcha.com; object-src 'none'; style-src 'self' https://hcaptcha.com https://*.hcaptcha.com; img-src 'self'; media-src 'self'; frame-src https://hcaptcha.com https://*.hcaptcha.com; font-src 'self'; connect-src 'self' https://hcaptcha.com https://*.hcaptcha.com; frame-ancestors 'none'"
    response.headers[
        "X-Content-Security-Policy"] = "default-src 'none'; script-src 'self' https://hcaptcha.com https://*.hcaptcha.com; object-src 'none'; style-src 'self' https://hcaptcha.com https://*.hcaptcha.com; img-src 'self'; media-src 'self'; frame-src https://hcaptcha.com https://*.hcaptcha.com; font-src 'self'; connect-src 'self' https://hcaptcha.com https://*.hcaptcha.com; frame-ancestors 'none'"
    response.headers[
        "X-WebKit-CSP"] = "default-src 'none'; script-src 'self' https://hcaptcha.com https://*.hcaptcha.com; object-src 'none'; style-src 'self' https://hcaptcha.com https://*.hcaptcha.com; img-src 'self'; media-src 'self'; frame-src https://hcaptcha.com https://*.hcaptcha.com; font-src 'self'; connect-src 'self' https://hcaptcha.com https://*.hcaptcha.com; frame-ancestors 'none'"
    # Kind of obsolete because of 'frame-ancestors' in CSP, but still worth it to support older browsers (more info: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    return response


@app.route("/")
def index_page():
    return render_template('index.html', indexPage=indexPage)


@app.route("/stats", methods=['POST'])
def stats_renderer():
    # if request.method == 'POST':
    status = {"name": request.form['summoner'], "region": request.form['region']}
    # else:
    #     status = {"error": "wrong method"}
    return jsonify(status)
