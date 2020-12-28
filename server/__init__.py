from flask import Flask, make_response, render_template, request, jsonify, redirect
from . import mongo_util
from flask_seasurf import SeaSurf

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gh48hfsjkdh943uro2jf92pafj483la3'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['CSRF_COOKIE_NAME'] = 'csrfmiddlewaretoken'
app.config['CSRF_COOKIE_SAMESITE'] = 'Strict'
app.config['CSRF_COOKIE_HTTPONLY'] = True
app.config['CSRF_COOKIE_SECURE'] = True

csrf = SeaSurf(app)

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
        "Content-Security-Policy"] = "default-src 'none'; script-src 'self' https://hcaptcha.com https://*.hcaptcha.com; object-src 'none'; style-src 'self' https://hcaptcha.com https://*.hcaptcha.com; img-src 'self'; media-src 'self'; frame-src https://hcaptcha.com https://*.hcaptcha.com; font-src 'self'; connect-src 'self' https://hcaptcha.com https://*.hcaptcha.com; frame-ancestors 'none'; form-action 'self';"
    response.headers[
        "X-Content-Security-Policy"] = "default-src 'none'; script-src 'self' https://hcaptcha.com https://*.hcaptcha.com; object-src 'none'; style-src 'self' https://hcaptcha.com https://*.hcaptcha.com; img-src 'self'; media-src 'self'; frame-src https://hcaptcha.com https://*.hcaptcha.com; font-src 'self'; connect-src 'self' https://hcaptcha.com https://*.hcaptcha.com; frame-ancestors 'none'; form-action 'self';"
    response.headers[
        "X-WebKit-CSP"] = "default-src 'none'; script-src 'self' https://hcaptcha.com https://*.hcaptcha.com; object-src 'none'; style-src 'self' https://hcaptcha.com https://*.hcaptcha.com; img-src 'self'; media-src 'self'; frame-src https://hcaptcha.com https://*.hcaptcha.com; font-src 'self'; connect-src 'self' https://hcaptcha.com https://*.hcaptcha.com; frame-ancestors 'none'; form-action 'self';"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Access-Control-Allow-Origin"] = "https://assets.hcaptcha.com"
    # response.headers["Vary"] = "Origin"
    return response


@app.route("/")
def index_page():
    return render_template('index.html', indexPage=indexPage)

def validate_summoner_name(sname: str) -> bool:
    return 3 <= len(sname) <= 16

def validate_region(region: str) -> bool:
    return region in ["eune", "euw"]

@app.route("/get-statistics-report", methods=['POST'])
def stats_renderer():
    code = 200
    summoner = request.form['summoner']
    region = request.form['region']
    if request.method == 'POST' and validate_summoner_name(summoner) and validate_region(region):
        status = {"name": summoner, "region": region}
    else:
        code = 400
        status = {"Error": "Bad Request"}
    return make_response(jsonify(status), code)

@app.errorhandler(404)
def sec_404(error):
    return render_template('404.html'), 404
    
@app.route("/.htaccess")
@app.route("/sitemap.xml")
def sec_redirect():
    return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")