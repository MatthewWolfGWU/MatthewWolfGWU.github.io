import pandas as pd
import polars as pl
import numpy as np
import nflreadpy as nfl
import gc

def go_column(df: pd.DataFrame) -> pd.DataFrame:
    """ add a "go for it" column to a data frame of fourth down data

    args:
        df: dataframe containing raw 4th down nfl pbp data

    returns:
        A  pandas dataframe which has removed plays which were penalties, deleted, or [insert], 
        and contains plays that are either dropbacks, runs, punts, or field goals.
    """

    # -------------- select just fourth downs --------------

    data = df[df["down"] == 4]

    # -------------- Filter for just pass plays and rush plays, and filter out field goals and punts --------------

    data["go"] = np.where((data["rush"] == 1) | 
                          (data["pass"] == 1) &
                          ~data["play_type_nfl"].isin(["PUNT", "FIELD_GOAL"]), 
                          1,0) 

    # -------------- assign punts that were aborted plays to be 0 in go column  --------------

    data["go"] = np.where((data["aborted_play"] == 1) &                                                             
                           (data["desc"].str.contains("Punt formation", na = False) | data["desc"].str.contains("punts") ), # add a second data desc filter here for if the play fpesnt have punt formation (possible error) and instead search for "punts"
                           0, data["go"])

    # ------------- Create a mask for dead ball plays ---------------

    dead_ball_mask = (
        data["desc"].str.contains(r"(Run formation) | (Pass formation) | (Shotgun)", na =False) &
        data["desc"].str.contains(r"(False Start) | (Neutral Zone Infraction)", na = False)
    )

    # -------------- apply dead ball mask to go col-------------- 

    data.loc[dead_ball_mask, "go"] = np.nan


    # --------------- now filter out plays that were penalties --------

    

    return data


def clean_fourth(df: pd.DataFrame) -> pd.DataFrame:
    """ Clean a data frame of fourth down data from no_play downs and qb_kneel downs

    no_play represents either a penalty or a timeout, so these are 4th down plays that did not count.

    args:
        df: dataframe containing raw 4th down nfl pbp data with "go" column created from go_column function

    returns:
        A filtered pandas dataframe which has removed plays which were penalties, deleted, or timeouts, 
        and contains only plays that are either pass attempts, runs, punts, or field goals.
    """

    # -------------- select just fourth downs --------------

    data = df

    # -------------- filter out no_play and qb_kneels --------------
    
    data = data[(data["play_type"] != "no_play") & (data["play_type"] != "qb_kneel")]

    return data


