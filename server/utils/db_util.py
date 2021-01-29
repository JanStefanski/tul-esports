"""

db_util.py
===========

Something I can manage a database with.
My wife left me, but my cool did not 😎

"""

import sqlite3
import os
from .league_api_util import LeaguePlayer
from datetime import datetime, timedelta

current_season = 11  # TODO: It's hardcoded and it should be retrieved somehow

db_path = os.path.join(os.getcwd(), 'server/db/tulesports.db')

print(sqlite3.connect(db_path))

tier_list = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]

rank_list = ["IV", "III", "II", "I"]


def init_db():
    with sqlite3.connect(db_path) as conn:
        print("creating db...")
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("""
        create table if not exists players
        (
            account_id      text not null,
            summoner_id     text not null
                constraint players_pk
                    primary key,
            summoner_name   text not null,
            region          text not null,
            profile_icon_id int,
            summoner_level  int,
            puuid,
            role            text,
            refreshed_at    timestamp default current_timestamp,
            main_champion   text
        );
        """)
        c.execute("""
        create unique index if not exists table_name_summoner_id_uindex on players (summoner_id);
        """)
        c.execute("""
        create table if not exists rankings
        (
            type        text not null,
            tier        int  not null,
            rank        int  not null,
            summoner_id int  not null
                constraint rankings_players_summoner_id_fk
                    references players,
            wins        int  not null,
            loses       int  not null,
            season      int,
            lp          int
        );
        """)



def save_player(player: LeaguePlayer, favourite_champ: str):
    with sqlite3.connect(db_path) as conn:
        # summoner_id, account_id, summoner_name, region, profile_icon_id, summoner_level, puuid
        player_data = (
            player.ids['id'], player.ids['accountId'], player.summoner_name, player.region, player.ids['profileIconId'],
            player.ids['summonerLevel'], player.ids['puuid'], player.determine_primary_position(), favourite_champ
        )
        c = conn.cursor()
        c.execute(
            """INSERT INTO players(summoner_id, account_id, summoner_name, region, profile_icon_id, summoner_level, puuid, role, main_champion)
             VALUES (?,?,?,?,?,?,?,?,?)
             ON CONFLICT(summoner_id) 
             DO UPDATE SET summoner_name=excluded.summoner_name, profile_icon_id=excluded.profile_icon_id,
              summoner_level=excluded.summoner_level, role=excluded.role, refreshed_at=current_timestamp, main_champion=excluded.main_champion;
              """,
            player_data
        )
        player_ranked_pos = player.ranked_positions()
        # type, tier, rank, summoner_id, wins, loses, season, lp
        player_rankings = [(rp['queueType'], tier_list.index(rp['tier']), rank_list.index(rp['rank']), rp['summonerId'],
                            rp['wins'], rp['losses'], current_season, rp['leaguePoints']) for rp in player_ranked_pos]
        c.execute('delete from rankings where summoner_id is (?) and season = (?)', [player.ids['id'], current_season])
        c.executemany(
            'INSERT INTO rankings(type, tier, rank, summoner_id, wins, loses, season, lp) VALUES (?,?,?,?,?,?,?,?);',
            player_rankings)


def get_player_position(queue_type, summoner_id):
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        # TODO: Check if usage of """ is secure in this case
        ranking = c.execute("""
    select position from (
        SELECT
               row_number() over (order by tier desc, rank desc, lp desc) as position,
       players.summoner_id,
       r.tier,
       r.rank,
       r.lp
from players
         inner join (select *
                     from rankings where season = (?) and type is (?)) r on players.summoner_id = r.summoner_id) where summoner_id is (?);""",
                            (current_season, queue_type, summoner_id))
        r = (list(ranking) or [[0]])[0][0]
        return r


def get_player_info(summoner_name, summoner_region):
    refresh_delay = timedelta(minutes=5)
    region_mappings = {"eune": "eun1", "euw": "euw1"}
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        refreshed_at = c.execute(
            'select refreshed_at, summoner_id, summoner_name, summoner_level, profile_icon_id, role, main_champion from players where summoner_name = (?) and region = (?);',
            (summoner_name, region_mappings[summoner_region]))
        ref = [a for a in refreshed_at]
        if ref:
            ref = ref
            if datetime.utcnow() > datetime.strptime(ref[0][0], "%Y-%m-%d %H:%M:%S") + refresh_delay:
                print(f'Failed time check for {summoner_name} on {summoner_region}, fetch from API')
                return False
            else:
                player_info = c.execute("""
                select
       r.type,
       r.tier,
       r.rank,
       r.wins,
       r.loses,
       r.lp
from players
    inner join rankings r on players.summoner_id = r.summoner_id
where
      players.summoner_id = (?)
  and
      season = (?);
                """, (ref[0][1], current_season))
                lpi = [a for a in player_info]
                info = {
                    "id": ref[0][1],
                    "summoner_name": ref[0][2],
                    "summoner_level": ref[0][3],
                    "profileIconId": ref[0][4],
                    "role": ref[0][5],
                    'main_champion': ref[0][6],
                    "ranking": {
                        rank[0]: {
                            'tier': tier_list[rank[1]],
                            'rank': rank_list[rank[2]],
                            'wins': rank[3],
                            'loses': rank[4],
                            'lp': rank[5]
                        }
                        for rank in lpi
                    }
                }
                return info
        else:
            print(f'New summoner {summoner_name} from {summoner_region}, fetching from API')
            return False


def get_ranking(limit: int = 5, page: int = 0, season=current_season) -> list:
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        # TODO: Check if usage of """ is secure in this case
        ranking = c.execute("""
        SELECT
               row_number() over (order by tier desc, rank desc, lp desc) as position,
       players.summoner_name,
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
                     from (select * from rankings where season = (?) order by tier desc, rank desc, lp desc)
                     group by summoner_id ) r on players.summoner_id = r.summoner_id
limit (?) offset (?);""", (season, limit, page * limit))
        r = [{"name": player[1], "rank": f"{tier_list[player[4]]} {rank_list[player[5]]}",
              "role": player[3].capitalize()} for player in ranking]
        return r
