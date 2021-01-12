"""

db_util.py
===========

Something I can manage a database with.
Currently used exclusively for leaderboards and rankings.

"""

import sqlite3
import os
from .league_api_util import LeaguePlayer

current_season = 11

db_path = os.path.join(os.getcwd(), 'server/db/tulesports.db')

tier_list = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]

rank_list = ["IV", "III", "II", "I"]


def save_player(player: LeaguePlayer):
    with sqlite3.connect(db_path) as conn:
        # summoner_id, account_id, summoner_name, region, profile_icon_id, summoner_level, puuid
        player_data = (
            player.ids['id'], player.ids['accountId'], player.summoner_name, player.region, player.ids['profileIconId'],
            player.ids['summonerLevel'], player.ids['puuid'], player.position
        )
        c = conn.cursor()
        c.execute(
            """INSERT INTO players(summoner_id, account_id, summoner_name, region, profile_icon_id, summoner_level, puuid, role)
             VALUES (?,?,?,?,?,?,?,?)
             ON CONFLICT(summoner_id) 
             DO UPDATE SET summoner_name=excluded.summoner_name, profile_icon_id=excluded.profile_icon_id,
              summoner_level=excluded.summoner_level, role=excluded.role;
              """,
            player_data
        )
        player_ranked_pos = player.ranked_positions()
        # type, tier, rank, summoner_id, wins, loses, season, lp
        player_rankings = [(rp['queueType'], tier_list.index(rp['tier']), rank_list.index(rp['rank']), rp['summonerId'],
                            rp['wins'], rp['losses'], current_season, rp['leaguePoints']) for rp in player_ranked_pos]
        # TODO: Update cause for almost whole queue, it actually would be easier to drop the value and insert a new one
        # c.executemany(
        #     'INSERT INTO rankings(type, tier, rank, summoner_id, wins, loses, season, lp) VALUES (?,?,?,?,?,?,?,?)',
        #     player_rankings)


def get_ranking(limit: int = 5, page: int = 0) -> list:
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        # TODO: Check if usage of """ is secure in this case
        ranking = c.execute("""
        SELECT players.summoner_name,
       players.profile_icon_id,
       players.role,
       r.tier,
       r.rank,
       r.lp,
       r.type,
       r.wins,
       r.loses
from players
         inner join (select *
                     from (select * from rankings order by tier desc, rank desc, lp desc)
                     group by summoner_id) r on players.summoner_id = r.summoner_id
order by tier desc, rank desc, lp desc
limit (?) offset (?);""", (limit, page * limit))
        r = [{"name": player[0], "rank": f"{tier_list[player[3]]} {rank_list[player[4]]}", "role": player[2].capitalize()} for player in ranking]
        return r
