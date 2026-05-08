import pandas as pd
import polars as pl
import numpy as np
import nflreadpy as nfl
import gc

# ------------------nfl play by play columns-------------------------
pbp_cols = [
    # pk
    "game_id", "play_id", "drive", # these three together form a pk of a play
    
    # game descriptors
    "home_team", "away_team" , "season_type", "week", "season",

    # drive/play descriptors
    "posteam", "defteam", "side_of_field", "yardline_100", "yrdln",
    "half_seconds_remaining", "game_seconds_remaining", "game_half", "sp", 
    "qtr", "down", "goal_to_go", "ydstogo", 
    "desc", "penalty", "play", "special_teams_play",
    "play_type_nfl", "aborted_play",

    # offensive attributes
    "play_type", "rush_attempt", "pass_attempt","yards_gained", 
    "shotgun", "qb_dropback", "qb_scramble", "pass_length", 
    "pass_location", "run_location", "run_gap", "pass",
    "rush", "special", "play_deleted", "qb_spike", "qb_kneel",

    # yardage
    "passing_yards", "receiving_yards", "rushing_yards",

    # game descriptors
    "score_differential",

    # advanced metric descriptors
    "epa", "wp", "wpa",

    # 4th down descriptors
    "fourth_down_converted", "fourth_down_failed",

    # player identifiers
    "passer_player_id", "passer_player_name", "receiver_player_id", "receiver_player_name",
    "rusher_player_id", "rusher_player_name",

    # coach identifiers
    "home_coach", "away_coach"

]

# ------------------nfl participation columns-------------------------
participation_cols = [
    # PK
    "nflverse_game_id", "play_id", 

    # offensive descriptors
    "offense_formation", "route", 

    # defensive descriptors 
    "defenders_in_box", "number_of_pass_rushers", "defense_man_zone_type", "defense_coverage_type" 
]

# ------------------nfl participation columns-------------------------
def fourth_down_data(seasons: int | list[int] | bool | None = None, ) -> pd.DataFrame:

    """Load NFL 4th down data for selected seasons.

    Keyword arguments:
    seasons (int): year(s) of desired 4th down nfl data
    """

      # when bool load all seasons
    if seasons is True:
        pass

    # When seasons is None, we return just the most recent year
    elif seasons is None:
        seasons = [2025]
    
    # When seasons is an integer or list of ints, seasons of data is those given years in list 
    elif isinstance(seasons, int):
        seasons = [seasons]

    # Load raw pbp and participation data
    pbp_data = nfl.load_pbp(seasons = seasons).lazy().filter((pl.col("down") == 4) & (pl.col("season") >= 2016)).select(pbp_cols).collect()
    participation_data = nfl.load_participation(seasons = seasons).lazy().select(participation_cols).collect()
    
    # join data on pks
    nfl_4th = pbp_data.join(participation_data, how = "left", left_on= ["game_id", "play_id"] ,right_on= ["nflverse_game_id", "play_id"])

    # clear memory
    del pbp_data, participation_data
    gc.collect()

    # convert to pandas
    output = nfl_4th.to_pandas()
    del nfl_4th
    gc.collect()

    return(output)

# Write to CSV
#data = fourth_down_data(seasons = True)
#data.to_csv("fourth.csv")