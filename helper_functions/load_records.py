import pandas as pd
import polars as pl
import numpy as np
import nflreadpy as nfl
import gc


def team_records(seasons: int | None = None, team: str | None = None ) -> pd.DataFrame:

    """Load team records for a given season.

    Keyword arguments:
    seasons (int): year of desired team records
    """

    if seasons is None:
        seasons = 2025
    else:
        seasons = seasons

    # ---------------------- load schedule ----------------------------------

    sched = nfl.load_schedules(seasons= seasons).lazy().collect().to_pandas()
    sched = sched[(sched["game_type"] == "REG")]
    
    # ---------------------- Calc Wins ----------------------------------
    
    sched = sched.assign( home_win = np.where(sched["home_score"] > sched["away_score"], 1, 0))
    sched = sched.assign( away_win = np.where(sched["away_score"] > sched["home_score"], 1, 0))

    # ---------------------- Calc Losses ----------------------------------

    sched = sched.assign( home_loss = np.where(sched["home_score"] < sched["away_score"], 1, 0))
    sched = sched.assign( away_loss = np.where(sched["away_score"] < sched["home_score"], 1, 0))
        
    # ---------------------- Calc Ties ----------------------------------

    sched = sched.assign(tie = np.where(sched["away_score"] == sched["home_score"], 1, 0))

    # ---------------------- Aggregate home and away Wins and Losses By Team ----------------------------------

    # away wins and losses
    away = sched.groupby(['away_team', 'season']).agg(
        away_wins = ("away_win", "sum"),
        away_losses = ("away_loss", "sum")
    ).reset_index().rename(columns= {
        "away_team": "team"
    })

    # Home wins and losses
    home = sched.groupby(['home_team', 'season']).agg(
        home_wins = ("home_win", "sum"),
        home_losses = ("home_loss", "sum")
    ).reset_index().rename(columns= {
        "home_team": "team"
    })

    # ties
    home_ties = (sched.groupby(['home_team', 'season'])).agg(
        home_ties = ("tie", "sum")
    ).reset_index().rename(columns= {
        "home_team": "team"
    })

    away_ties = (sched.groupby(['away_team', 'season'])).agg(
        away_ties = ("tie", "sum")
    ).reset_index().rename(columns= {
        "away_team": "team"
    })

    # merge both tie dfs together
    ties = home_ties.merge(away_ties, how = 'left', on = "team")

    # ---------------------- Join Wins + Losses + Ties ----------------------------------

    merged = home.merge(away, how= "left", on = "team").merge(ties, how = "left", on="team")
    
    # ---------------------- Calculate Wins, Losses, and Win %  ----------------------------------

    # Create columns for total wins, losses and ties
    records = merged.assign(
        wins = merged["home_wins"] + merged["away_wins"],
        losses = merged["home_losses"] + merged["away_losses"],

        ties = merged["home_ties"] + merged["away_ties"],
        )
    
    # Account for tie component of winning percentage
    records = records.assign( tie_win_component = records["ties"] * 0.5,
        tie_loss_component = records["ties"] * 0.5,
    )

    # Create column for win percentage
    records["win_pct"] = (records["wins"] + records["tie_win_component"]) / ( records["wins"] + records["tie_win_component"] + records["losses"] + records['tie_loss_component'])
    
    # select relevant columns
    records =  records[["season_x_x","team","wins", "losses", "ties", "win_pct"]].sort_values(by = "win_pct", ascending=False).reset_index().rename(columns= {"season_x_x": "season"})

    if team is None:
        return(records)
    else:
        return(records[records["team"] == team])
    
    


