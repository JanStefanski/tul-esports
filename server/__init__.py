import secrets
from math import ceil

from .services.player_info_fetch import fetch_player_info
from flask import Flask, make_response, render_template, request, redirect, escape, cli
from .utils import i18n_util, db_util
from flask_seasurf import SeaSurf
from .utils.config_loader import ConfigLoader

app = Flask(__name__)

cli.load_dotenv()

ConfigLoader(app)

csrf = SeaSurf(app)

@app.before_request
def generate_nonce():
    nonce = secrets.token_urlsafe()
    app.jinja_env.globals['styleNonce']= nonce

@app.after_request
def apply_sec_headers(response):
    # Setting CSP (more info: https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
    response.headers[
        "Content-Security-Policy"] = f"default-src 'none'; script-src 'self' https://umami-stefanski-tech.herokuapp.com/; object-src 'none'; style-src 'self' 'nonce-{app.jinja_env.globals['styleNonce']}'; img-src 'self' https://ddragon.leagueoflegends.com/ data: 'unsafe-eval'; media-src 'self'; frame-src; font-src 'self'; connect-src 'self' https://umami-stefanski-tech.herokuapp.com/api/collect; frame-ancestors 'none'; form-action 'self';"
    response.headers[
        "X-Content-Security-Policy"] = f"default-src 'none'; script-src 'self' https://umami-stefanski-tech.herokuapp.com/; object-src 'none'; style-src 'self' 'nonce-{app.jinja_env.globals['styleNonce']}'; img-src 'self' https://ddragon.leagueoflegends.com/ data: 'unsafe-eval'; media-src 'self'; frame-src; font-src 'self'; connect-src 'self' https://umami-stefanski-tech.herokuapp.com/api/collect; frame-ancestors 'none'; form-action 'self';"
    response.headers[
        "X-WebKit-CSP"] = f"default-src 'none'; script-src 'self' https://umami-stefanski-tech.herokuapp.com/; object-src 'none'; style-src 'self' 'nonce-{app.jinja_env.globals['styleNonce']}'; img-src 'self' https://ddragon.leagueoflegends.com/ data: 'unsafe-eval'; media-src 'self'; frame-src; font-src 'self'; connect-src 'self' https://umami-stefanski-tech.herokuapp.com/api/collect; frame-ancestors 'none'; form-action 'self';"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


def load_lang(req: request):
    # print(req.headers.get('Accept-Language'))
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
    ranked_players = db_util.get_ranking()[1]
    resp = make_response(
        render_template('index.html', rankedPlayers=ranked_players, indexPage=idx_page, navBar=navbar))
    if request.args.get('lang'):
        resp.set_cookie('lang', request.args.get('lang'), secure=True, httponly=True, samesite='Strict')
    return resp


@app.route("/leaderboards")
def rankings_page():
    param_parser = lambda param_key, param_val: "?" + "&".join(([f"{param_value}={request.args.get(param_value)}" for param_value in request.args] + [f"{param_key}={str(param_val)}"]) if not request.args.get(param_key) else [f"{param_value}={request.args.get(param_value)}".replace(param_key+'='+request.args.get(param_value), param_key+'='+str(param_val)) for param_value in request.args])
    allowed_limits = (5, 10, 25, 50)
    limit = int(request.args.get('limit') or allowed_limits[0]) if int(request.args.get('limit') or allowed_limits[0]) in allowed_limits else allowed_limits[0]
    page = int(request.args.get('page') or 0)
    season = int(request.args.get('season') or 11)
    l_page = i18n_util.I18n('leaderboardsPage').load_translation(load_lang(request))
    navbar = i18n_util.I18n('navBar').load_translation(load_lang(request))
    ranking = db_util.get_ranking(limit=limit, season=season, page=page)
    all_ranking_records = ranking[0]
    pages = range(ceil(all_ranking_records / limit))
    ranked_players = ranking[1]
    resp = make_response(
        render_template('leaderboards.html', rankedPlayers=ranked_players, leaderboardsPage=l_page,
                        navBar=navbar, limit=limit, pages=pages, currentPage=page, allowedLimits=allowed_limits, paramParser=param_parser))
    if request.args.get('lang'):
        resp.set_cookie('lang', request.args.get('lang'), secure=True, httponly=True, samesite='Strict')
    return resp


def validate_summoner_name(sname: str) -> bool:
    return 3 <= len(sname) <= 16


def validate_region(region: str) -> bool:
    return region in ["eune", "euw"]


@app.route("/get-statistics-report", methods=['POST'])
def stats_renderer():
    summoner = request.form['summoner']
    region = escape(request.form['region'])
    navbar = i18n_util.I18n('navBar').load_translation(load_lang(request))
    stats_page = i18n_util.I18n('statsPage').load_translation(load_lang(request))
    if request.method == 'POST' and validate_summoner_name(summoner) and validate_region(region):
        summoner = escape(summoner)
        try:
            assets_and_strings = fetch_player_info(summoner, region)
            stats_page_texts = dict(stats_page, **assets_and_strings)
            resp = make_response(render_template('stats.html', indexPage={}, navBar=navbar, statsPage=stats_page_texts))
            if request.args.get('lang'):
                resp.set_cookie('lang', request.args.get('lang'), secure=True, httponly=True, samesite='Strict')
        except Exception as e:
            print(e)
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
