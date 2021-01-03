from flask import Flask, make_response, render_template, request, jsonify, redirect
from .utils import league_api_util, i18n_util
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

@app.after_request
def apply_sec_headers(response):
    # Setting CSP (more info: https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
    response.headers[
        "Content-Security-Policy"] = "default-src 'none'; script-src 'self'; object-src 'none'; style-src 'self'; img-src 'self' data: 'unsafe-eval'; media-src 'self'; frame-src; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; form-action 'self';"
    response.headers[
        "X-Content-Security-Policy"] = "default-src 'none'; script-src 'self'; object-src 'none'; style-src 'self'; img-src 'self' data: 'unsafe-eval'; media-src 'self'; frame-src; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; form-action 'self';"
    response.headers[
        "X-WebKit-CSP"] = "default-src 'none'; script-src 'self'; object-src 'none'; style-src 'self'; img-src 'self' data: 'unsafe-eval'; media-src 'self'; frame-src; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; form-action 'self';"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Access-Control-Allow-Origin"] = "https://assets.hcaptcha.com"
    return response


@app.route("/")
def index_page():
    idx_page = i18n_util.I18n('indexPage').load_translation(request.args.get('lang') if request.args.get('lang') else 'en-GB')
    ranked_players = [
        { "name": "Player I", "rank": "Platinum IV", "role": "Mid"},
        { "name": "Player II", "rank": "Gold II", "role": "Jungle"},
        { "name": "Player III", "rank": "Gold II", "role": "ADC"},
        { "name": "Player IV", "rank": "Gold IV", "role": "Support"},
        { "name": "Player V", "rank": "Silver I", "role": "Top"}
    ]
    return render_template('index.html', rankedPlayers=enumerate(ranked_players), indexPage=idx_page)

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
        player = league_api_util.LeaguePlayer(summoner, region)
        status["ranking"] = player.ranked_positions()
        status["position"] = player.position
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