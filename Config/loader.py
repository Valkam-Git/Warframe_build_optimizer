import json
import pandas as pd
import warnings
from pandas.errors import SettingWithCopyWarning
warnings.filterwarnings("ignore")
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)


ONLYMAX=True

stat_keys = ["Range", "Duration", "Efficiency", "Strength", "Health", "Shield", "Armor", "Energy", "Sprint Speed", "Mobility"]

import json

def load_mods():
    """
    Load the warframe mods from Mods.json and return them on a dictionary.
    
    This function reads the Mods.json file and filters the mods that are compatible with the WARFRAME or Aura categories.
    It also filters the mods that have levelStats. Then, it removes duplicates based on the mod name and returns the filtered mods.
    
    Returns:
    list: A list of dictionaries containing the filtered mods.
    """
    with open("Mods.json", "r") as mods_file:
        mods = json.load(mods_file)
    
    # Filter mods by compatibility and levelStats
    mods = [mod for mod in mods if "compatName" in mod and mod["compatName"] in ["WARFRAME", "AURA"]]
    mods = [mod for mod in mods if "levelStats" in mod]
    
    # Remove duplicates based on mod name
    unique_names = []
    new_mods = []
    for mod in mods:
        if mod["name"] not in unique_names:
            unique_names.append(mod["name"])
            new_mods.append(mod)
            
    return new_mods

import pandas as pd

def process_mods(mods):
    """
    Process a list of Warframe mods and returns a pandas DataFrame with relevant information.

    Args:
    mods (list): A list of Warframe mods.

    Returns:
    pandas.DataFrame: A DataFrame with relevant information about the mods.
    """
    global stat_keys
    useful_keys = ["category", "compatName", "fusionLimit", "name", "polarity", "rarity", "tradable", "type", "uniqueName", "drain", "isUtility", "modSet", "isExilus", "description", "modSetValues"]
    useful_keys.extend(stat_keys)
    mods = [convert_levels(mod) for mod in mods]
    mods = pd.DataFrame([mod for sublist in mods for mod in sublist])
    mods = mods[useful_keys]
    mods = mods.fillna(0.0)
    mods = mods.replace({"isExilus": {0.0: False}})

    
    # Some hacks
    mods = mods[mods["name"] != "Primed Streamline"]
    mods = mods[mods["name"] != "Preparation"]
    mods = mods[mods["name"] != "Shepherd"]
    mods = mods[mods["name"] != "Power Donation"]
    mods = mods[mods["name"] != "Adrenaline Boost"]
    mods = mods[mods["name"] != "Follow Through"]
    mods["actualDrain"] = mods.apply(lambda row: row["drain"] + row["fusionLimit"] if row["drain"] >= 0 else row["drain"] - row["fusionLimit"], axis=1)
    umbral_intensify = mods[mods["name"] == "Umbral Intensify"]
    umbral_intensify["Strength"] = 0.44
    # Add a new type column to the mods DataFrame called type, if it's of compatName WARFRAME, type is 0, compatName AURA, type is 1, isExilus, type is 2
    mods["type"] = mods.apply(lambda row: 2 if row["isExilus"] else 1 if row["compatName"] == "AURA" else 0 if row["compatName"] == "WARFRAME" else 3, axis=1)
    # drop the column compatName, isExilus, fusionLimit, drain
    mods = mods.drop(columns=["compatName", "isExilus", "fusionLimit", "drain"])
    # convert to dict
    mods = mods.to_dict(orient="records")
    

    return mods

def convert_levels(mod):
    """
    Given a mod dictionary, creates a list of dictionaries where each dictionary represents a mod at a different level.
    Each mod in the list has the same stats as the original mod, but with different drain and rank values.

    Args:
        mod (dict): A dictionary representing a mod. It must have a "levelStats" key, which is a list of dictionaries
        representing the stats of the mod at different levels.

    Returns:
        list: A list of dictionaries representing the mod at different levels. Each dictionary has the same keys as the
        original mod, but with different values for "drain" and "rank".
    """
    levels = mod["levelStats"]
    new_mods = []
    i = 0
    if ONLYMAX:
        levels = levels[-1:]
    for level in levels:
        # Create a copy of the original mod
        new_mod = mod.copy()
        # Remove the "levelStats" key from the copy
        new_mod.pop("levelStats")
        # Calculate the drain of the mod based on the rank
        new_mod["drain"] = new_mod["baseDrain"] + i
        # Remove the "baseDrain" key from the copy
        new_mod.pop("baseDrain")
        # Extract the stats of the mod at the current level
        stats = extract_stats(level["stats"])
        # Add the stats to the copy of the mod
        for key, value in stats.items():
            new_mod[key] = value
        # Add the copy of the mod to the list of new mods
        new_mods.append(new_mod)
        i += 1
    return new_mods
    

def extract_stats(text):
    """
    Extracts stats from a given text and returns them as a dictionary.

    Args:
        text (str): The text to extract stats from.

    Returns:
        dict: A dictionary containing the extracted stats.
    """
    global stat_keys  # Access the global variable stat_keys
    stats = {}  # Initialize an empty dictionary to store the extracted stats
    for stat in text:  # Iterate over each stat in the text
        if any(x in stat for x in ["Jump", "Wall", "Aim"]): 
            continue
        for key in stat_keys:  # Iterate over each key in the global variable stat_keys
            if key in stat:  # Check if the key is in the stat
                try:
                    # Extract the value from the stat and convert it to a float
                    value = float(stat.split(key)[0].split(" ")[0].strip().replace("+", "").replace("%", ""))*0.01
                    stats[key] = value  # Add the key-value pair to the stats dictionary
                except:
                    continue  # If there's an error, skip to the next iteration
    return stats  # Return the extracted stats dictionary

def get_mods():
    return process_mods(load_mods())

    
if __name__ == "__main__":
    process_mods(load_mods())