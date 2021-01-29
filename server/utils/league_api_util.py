"""
    league_api_util.py
    ----------------

    Scuffed implementation of Riot API.
    If it's terrible, please refrain from yelling at me ;; ~ Janek
"""
import requests
import json
from typing import Iterable
from os import environ

def get_current_patch() -> str:
    """
    Helper function that fetches current league patch to be used with Data Dragon
    :return: String with current patch version
    """
    req = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
    return json.loads(req.text)[0]


def get_champion_id(champion_name: str, current_patch:str=None) -> int:
    """
    Helper function that fetches ID of a given champion to be used with Riot API & Data Dragon
    Opposite of :func:`get_champion_name()`
    :param current_patch: (optional) String with Current Patch
    :param champion_name: Name of the champion
    :return: Int with Champion ID
    """
    req = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{current_patch or get_current_patch()}/data/en_US/champion.json")
    champion_id = json.loads(req.text)["data"][champion_name]["key"]
    return int(champion_id)

def get_champion_name(champion_id: int, current_patch:str=None) -> str:
    """
    Helper function that fetches name of a given champion  to be used with Riot API & Data Dragon
    Opposite of :func:`get_champion_id()`
    :param current_patch: (optional) String with Current Patch
    :param champion_id: Int with Champion ID
    :return: Name of the champion
    """
    req = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{current_patch or get_current_patch()}/data/en_US/champion.json")
    champion_name = list(filter(lambda champ: champ['key'] == str(champion_id), json.loads(req.text)["data"].values()))[0]['id']
    return str(champion_name)


def get_champion_info(champion_name:str=None, champion_id:int=None, current_patch=None) -> dict:
    if champion_name and champion_id:
        raise SyntaxError("You cannot define both champion name and champion id. Use one of them")
    else:
        if champion_id:
            if type(champion_id) != int:
                raise TypeError(f"Champion id ought to be a int type. Current type: {type(champion_id)}")
            else:
                champion_name = get_champion_name(champion_id, current_patch=current_patch)
        req = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{current_patch or get_current_patch()}/data/en_US/champion/{champion_name}.json")
        return json.loads(req.text)


class SummonerNotFoundError(Exception):
    """Raised when given summoner does not exist"""
    def __init__(self, summoner_name, region):
        err = f"Summoner {summoner_name} does not exist in {region} region"
        super().__init__(err)


class LeaguePlayer:

    def __init__(self, summoner_name: str, region: str):
        """
        Defines the :class:`LeaguePlayer` to use with API
        :param summoner_name: Name of the summoner
        :param region: A region where the summoner has been registered. Available options: "eune", "euw"
        """
        region_mappings = {"eune": "eun1", "euw": "euw1"}
        self.key = environ.get('LEAGUE_API_KEY')
        self.summoner_name = summoner_name
        self.region = region_mappings[region]
        self.current_patch = get_current_patch()
        # TODO: Make better exceptions and exception handling.
        #  It should be different exceptions if key is invalid and different if player is not found
        try:
            self.ids = self.__get_summoner_ids()
        except KeyError:
            raise SummonerNotFoundError(summoner_name, region)

    def __get_summoner_ids(self) -> dict:
        req = requests.get(
            "https://{0}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{1}".format(self.region,
                                                                                         self.summoner_name),
            headers={"X-Riot-Token": self.key})
        return json.loads(req.text)

    def ranked_positions(self, queues:Iterable[str] = ("flex", "solo")) -> list:
        """
        Tries to retrieve ranked positions of the player. If player has no ranked positions, it returns empty list.
        :param queues: :class:`Iterable` with one or more queue names.
        :return: :class:`List` with response
        """
        queue_types = {"flex": "RANKED_FLEX_SR", "solo": "RANKED_SOLO_5x5"}
        req = requests.get(
            "https://{0}.api.riotgames.com/lol/league/v4/entries/by-summoner/{1}".format(self.region, self.ids['id']),
            headers={"X-Riot-Token": self.key})
        result = filter(lambda ranking: ranking["queueType"] in [queue_types[qt] for qt in queues],
                        json.loads(req.text))
        return list(result)

    def champion_mastery(self) -> list:
        # TODO: Implement champion mastery from League API
        #  ALL Masteries: https://developer.riotgames.com/apis#champion-mastery-v4/GET_getAllChampionMasteries
        #  Specific Mastery: https://developer.riotgames.com/apis#champion-mastery-v4/GET_getChampionMastery
        # raise NotImplementedError
        req = requests.get(
            "https://{0}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{1}".format(self.region, self.ids['id']),
            headers={"X-Riot-Token": self.key})
        return json.loads(req.text)

    def matches(self, champion=None, queue=None, season=None) -> list:
        """
        Returns matches of the summoner

        :param champion: (optional) Name of the champion (or champions, then list of names) to retrieve matches with
        :param queue: (optional) Queue type of the matches
        :param season: (optional) Season matches has been played in
        :return: :class:`Dictionary` with matches
        """
        params = {
            "champion": (get_champion_id(champion, current_patch=self.current_patch) if type(champion) is str else [get_champion_id(ch, current_patch=self.current_patch) for ch in champion]) if champion else None, # I am sincerely sorry for this line
            "queue": queue,
            "season": season
        }
        # TODO: Now only retrieves 100 last matches with specific params THIS IS VERY WRONG AND SHOULDN'T BE A CASE!
        #  I'll need to make use of the beginIndex and endIndex as described in Riot API (https://developer.riotgames.com/apis#match-v4/GET_getMatchlist)
        #  and possibly make this function a generator of matches with usage of yield
        params = {key: value for key, value in params.items() if value is not None}
        req = requests.get(
            "https://{0}.api.riotgames.com/lol/match/v4/matchlists/by-account/{1}".format(self.region,
                                                                                          self.ids['accountId']),
            headers={"X-Riot-Token": self.key}, params=params)
        matches = json.loads(req.text)
        matches = matches["matches"] if "matches" in matches else []  # Kind of cursed line if you ask me
        return matches

    def determine_primary_position(self, min_games: int = 20) -> str:
        """
        Attempts to determine primary position of the player.
        If not enough games in queue type are found to determine, it looks in the next queue.

        Queue priority order:
          0. Ranked solo (420)
          1. Ranked Flex (440)
          2. Normal Draft (400)
        :param min_games: Minimum games in specific queue to determine the players' role
        :return: One of five possible values: `top` `jungle` `mid` `adc` `support`
        """

        # TODO: This method is really damn slow right now. Optimize this heresy BEFORE it goes to prod!
        relevant_queue_types = [420, 440, 400]
        lanes = ["BOTTOM", "JUNGLE", "MID", "TOP"]
        relevant_matches = []
        grouped_matches = {}  # I use this because I'm special

        for qt in relevant_queue_types:
            relevant_matches = self.matches(queue=qt)
            if len(relevant_matches) >= min_games:
                break

        # All of this looks like this, so we need to group it accordingly.
        # LANES -|_ MID
        #        |_ JUNGLE
        #        |_ TOP
        #        |_ BOTTOM -|_ ADC
        #                   |_ SUPPORT
        # Probably a stupid solution..
        for lane in lanes:
            grouped_matches[lane] = list(filter(lambda match: match["lane"] == lane, relevant_matches))
        grouped_matches["ADC"] = list(filter(lambda match: match["role"] == "DUO_CARRY", grouped_matches["BOTTOM"]))
        grouped_matches["SUPPORT"] = list(
            filter(lambda match: match["role"] == "DUO_SUPPORT", grouped_matches["BOTTOM"]))
        del grouped_matches["BOTTOM"]
        return max([(len(matches), role) for role, matches in grouped_matches.items()])[1].lower()