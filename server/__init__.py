# from base64 import b64encode
# from os import urandom
import random
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
        "Content-Security-Policy"] = "default-src 'none'; script-src 'self'; object-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'self' https://ddragon.leagueoflegends.com/ data: 'unsafe-eval'; media-src 'self'; frame-src; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; form-action 'self';"
    response.headers[
        "X-Content-Security-Policy"] = "default-src 'none'; script-src 'self'; object-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'self' https://ddragon.leagueoflegends.com/ data: 'unsafe-eval'; media-src 'self'; frame-src; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; form-action 'self';"
    response.headers[
        "X-WebKit-CSP"] = "default-src 'none'; script-src 'self'; object-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'self' https://ddragon.leagueoflegends.com/ data: 'unsafe-eval'; media-src 'self'; frame-src; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; form-action 'self';"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


@app.route("/")
def index_page():
    language = request.args.get('lang') or 'en-GB'
    idx_page = i18n_util.I18n('indexPage').load_translation(language)
    navbar = i18n_util.I18n('navBar').load_translation(language)
    # TODO: Whole DB util, must decide if it will be MongoDB (probably more work, but more versatile) or SQLite
    ranked_players = db_util.get_ranking()
    return render_template('index.html', rankedPlayers=enumerate(ranked_players), indexPage=idx_page, navBar=navbar)


def validate_summoner_name(sname: str) -> bool:
    return 3 <= len(sname) <= 16


def validate_region(region: str) -> bool:
    return region in ["eune", "euw"]


@app.route("/get-statistics-report", methods=['POST'])
def stats_renderer():
    language = 'en-GB'
    # code = 200
    summoner = escape(request.form['summoner'])
    region = escape(request.form['region'])
    navbar = i18n_util.I18n('navBar').load_translation(language)
    if request.method == 'POST' and validate_summoner_name(summoner) and validate_region(region):
        try:
            # status = {"name": summoner, "region": region}
            player = league_api_util.LeaguePlayer(summoner, region)
            # status["ranking"] = player.ranked_positions()
            # status["position"] = player.position
            # status["mastery"] = player.champion_mastery()
            chmp_id = player.champion_mastery()[0]["championId"]
            skin_name = league_api_util.get_champion_info(champion_id=chmp_id)["data"]
            skin_name = f"{list(skin_name.keys())[0]}_{random.choice(skin_name[list(skin_name.keys())[0]]['skins'])['num']}"
            stats_page_texts = {
                "currentPatch": player.current_patch,
                "summonerName": player.summoner_name,
                "summonerLevel": player.ids['summonerLevel'],
                "summonerRankAndPosition": player.position.capitalize(),
                "assets": {
                    "summonerIcon": player.ids['profileIconId'],
                    "highestMasteryChampionRandomSkin": skin_name
                }
            }
            # if request.args.get('save'):
            #     db_util.save_player(player=player)
            return render_template('stats.html', indexPage={}, navBar=navbar, statsPage=stats_page_texts)
        except league_api_util.SummonerNotFoundError:
            code = 400
            status = {"Error": f"Summoner {summoner} not found in {region} region"}
    else:
        code = 400
        status = {"Error": "Bad Request"}
    return make_response(jsonify(status), code)


# 404 page copied from apache
@app.errorhandler(404)
def sec_404(error):
    return render_template('404.html'), 404


# Dir traversal easter egg
@app.route("/.htaccess")
@app.route("/sitemap.xml")
def sec_redirect():
    return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
