# from base64 import b64encode
# from os import urandom
import random
from .services.player_info_fetch import fetch_player_info
from flask import Flask, make_response, render_template, request, jsonify, redirect, escape
from .utils import league_api_util, i18n_util, db_util
from flask_seasurf import SeaSurf

app = Flask(__name__)

# TODO: Actual environment vars instead of hardcoded keys, secrets & vars
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
    # TODO: Change unsafe-inline to unsafe inline with nonce in styles later.
    #  generating nonce: nonce = lambda length: filter(lambda s: s.isalpha(), b64encode(urandom(length * 2)))[:length]
    response.headers[
        "Content-Security-Policy"] = "default-src 'none'; script-src 'self' http://localhost:3000/; object-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'self' https://ddragon.leagueoflegends.com/ data: 'unsafe-eval'; media-src 'self'; frame-src; font-src 'self'; connect-src 'self' http://localhost:3000/api/collect; frame-ancestors 'none'; form-action 'self';"
    response.headers[
        "X-Content-Security-Policy"] = "default-src 'none'; script-src 'self' http://localhost:3000/; object-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'self' https://ddragon.leagueoflegends.com/ data: 'unsafe-eval'; media-src 'self'; frame-src; font-src 'self'; connect-src 'self' http://localhost:3000/api/collect; frame-ancestors 'none'; form-action 'self';"
    response.headers[
        "X-WebKit-CSP"] = "default-src 'none'; script-src 'self' http://localhost:3000/; object-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'self' https://ddragon.leagueoflegends.com/ data: 'unsafe-eval'; media-src 'self'; frame-src; font-src 'self'; connect-src 'self' http://localhost:3000/api/collect; frame-ancestors 'none'; form-action 'self';"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


def load_lang(req: request):
    print(req.headers.get('Accept-Language'))
    if req.args.get('lang'):
        pref_lang = request.args.get('lang')
    elif req.cookies.get('lang'):
        pref_lang = request.cookies.get('lang')
    else:
        pref_lang = 'en-GB'
    return pref_lang


@app.route("/")
def index_page():
    idx_page = i18n_util.I18n('indexPage').load_translation(load_lang(request))
    navbar = i18n_util.I18n('navBar').load_translation(load_lang(request))
    ranked_players = db_util.get_ranking()
    resp = make_response(
        render_template('index.html', rankedPlayers=enumerate(ranked_players), indexPage=idx_page, navBar=navbar))
    if request.args.get('lang'):
        resp.set_cookie('lang', request.args.get('lang'))
    return resp


@app.route("/leaderboards")
def rankings_page():
    print(request.full_path)
    allowed_limits = (10, 25, 50)
    limit = int(request.args.get('limit') or 10) if int(request.args.get('limit') or 10) in allowed_limits else 10
    page = request.args.get('page') or 1
    season = int(request.args.get('season') or 10)
    idx_page = i18n_util.I18n('indexPage').load_translation(load_lang(request))
    navbar = i18n_util.I18n('navBar').load_translation(load_lang(request))
    ranked_players = db_util.get_ranking(limit=limit, season=season)
    resp = make_response(
        render_template('leaderboards.html', rankedPlayers=enumerate(ranked_players), indexPage=idx_page,
                        navBar=navbar))
    if request.args.get('lang'):
        resp.set_cookie('lang', request.args.get('lang'))
    return resp


def validate_summoner_name(sname: str) -> bool:
    return 3 <= len(sname) <= 16


def validate_region(region: str) -> bool:
    return region in ["eune", "euw"]


@app.route("/get-statistics-report", methods=['POST'])
def stats_renderer():
    summoner = escape(request.form['summoner'])
    region = escape(request.form['region'])
    navbar = i18n_util.I18n('navBar').load_translation(load_lang(request))
    stats_page = i18n_util.I18n('statsPage').load_translation(load_lang(request))
    if request.method == 'POST' and validate_summoner_name(summoner) and validate_region(region):
        try:
            assets_and_strings = fetch_player_info(summoner, region)
            stats_page_texts = dict(stats_page, **assets_and_strings)
            resp = make_response(render_template('stats.html', indexPage={}, navBar=navbar, statsPage=stats_page_texts))
            if request.args.get('lang'):
                resp.set_cookie('lang', request.args.get('lang'))
        except Exception:
            resp = make_response(render_template('error.html', errorPage={"errorHeader": "Error",
                                                                          "errorMessage": f"There is a problem with your request, check if summoner {summoner} exists for {region} region"}, navBar=navbar),
                                 400)
    else:
        resp = (render_template('error.html', errorPage={"errorHeader": "Error",
                                                         "errorMessage": "Bad Request"}, navBar=navbar),
                400)
    return resp


# 404 page copied from apache
@app.errorhandler(404)
def sec_404(error):
    return render_template('404.html'), 404


# Dir traversal easter egg
@app.route("/.htaccess")
@app.route("/sitemap.xml")
def sec_redirect():
    return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
