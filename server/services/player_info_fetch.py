import random

from ..utils import db_util, league_api_util


def fetch_player_info(summoner, region):
    player = db_util.get_player_info(summoner, region)
    if not player:
        player = league_api_util.LeaguePlayer(summoner, region)
        print("Fetching from API")
    if type(player) == league_api_util.LeaguePlayer:
        player_ranking = player.ranked_positions()
        rankings = {r['queueType']: r for r in player_ranking}
        chmp_id = player.champion_mastery()[0]["championId"]
        skin_name = league_api_util.get_champion_info(champion_id=chmp_id)["data"]
        db_util.save_player(player=player, favourite_champ=list(skin_name.keys())[0])
        skin_name = f"{list(skin_name.keys())[0]}_{random.choice(skin_name[list(skin_name.keys())[0]]['skins'])['num']}"
        assets_and_strings = {
            "currentPatch": player.current_patch,
            "summonerName": player.summoner_name,
            "summonerLevel": player.ids['summonerLevel'],
            "summonerRankAndPosition": player.determine_primary_position().capitalize(),
            "playerSoloPlacement": db_util.get_player_position('RANKED_SOLO_5x5', player.ids['id']),
            "playerFlexPlacement": db_util.get_player_position('RANKED_FLEX_SR', player.ids['id']),
            "assets": {
                "summonerIcon": player.ids['profileIconId'],
                "highestMasteryChampionRandomSkin": skin_name,
                "rankedSoloTier": rankings.get('RANKED_SOLO_5x5')['tier'].capitalize() if rankings.get(
                    'RANKED_SOLO_5x5') else "Unranked",
                "rankedSoloRank": rankings.get('RANKED_SOLO_5x5')['rank'] if rankings.get(
                    'RANKED_SOLO_5x5') else "",
                "rankedFlexTier": rankings.get('RANKED_FLEX_SR')['tier'].capitalize() if rankings.get(
                    'RANKED_FLEX_SR') else "Unranked",
                "rankedFlexRank": rankings.get('RANKED_FLEX_SR')['rank'] if rankings.get(
                    'RANKED_FLEX_SR') else "",
            }
        }
    else:
        chmp_info = league_api_util.get_champion_info(champion_name=player['main_champion'])["data"]
        skin_name = f"{player['main_champion']}_{random.choice(chmp_info[list(chmp_info.keys())[0]]['skins'])['num']}"
        rankings = player['ranking']
        assets_and_strings = {
            "currentPatch": league_api_util.get_current_patch(),
            "summonerName": player['summoner_name'],
            "summonerLevel": player['summoner_level'],
            "summonerRankAndPosition": player['role'],
            "playerSoloPlacement": db_util.get_player_position('RANKED_SOLO_5x5', player['id']),
            "playerFlexPlacement": db_util.get_player_position('RANKED_FLEX_SR', player['id']),
            "assets": {
                "summonerIcon": player['profileIconId'],
                "highestMasteryChampionRandomSkin": skin_name,
                "rankedSoloTier": rankings.get('RANKED_SOLO_5x5')['tier'].capitalize() if rankings.get(
                    'RANKED_SOLO_5x5') else "Unranked",
                "rankedSoloRank": rankings.get('RANKED_SOLO_5x5')['rank'] if rankings.get(
                    'RANKED_SOLO_5x5') else "",
                "rankedFlexTier": rankings.get('RANKED_FLEX_SR')['tier'].capitalize() if rankings.get(
                    'RANKED_FLEX_SR') else "Unranked",
                "rankedFlexRank": rankings.get('RANKED_FLEX_SR')['rank'] if rankings.get(
                    'RANKED_FLEX_SR') else "",
            }
        }
    return assets_and_strings
