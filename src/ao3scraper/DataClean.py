import re
from difflib import get_close_matches
import pandas as pd


def find_correct_character(
    original: str, options: list, characters_occurences: pd.DataFrame
):
    if (
        ("mr" in original)
        or ("mrs" in original)
        or ("jr." in original)
        or ("sr." in original)
    ):
        return original
    else:
        try:
            return characters_occurences[options].idxmax()
        except:
            return original


def find_correct_fandom(options: list, fandoms_occurences: pd.DataFrame):
    return fandoms_occurences[options].idxmax()


def clean_relationship(
    s: str,
    characters_list: pd.DataFrame,
    characters_occurences: pd.DataFrame,
    replace_w_closest_character: bool = True,
) -> str:
    if s.lower() == "dramione" or s.lower() == "dmhg":
        s = "dracomalfoy/hermionegranger"
    if (
        "drarry" in s.lower()
        or "drarrry" in s.lower()
        or "hp/dm" in s.lower()
        or s == "h/d"
    ):
        s = "dracomalfoy/harrypotter"
    if "wolfstar" in s.lower():
        s = "remuslupin/siriusblack"
    if "ss/rl" in s.lower():
        s = "remuslupin/severussnape"
    if "snarry" in s.lower() or "ss/hp" in s.lower() or "hp/ss" in s.lower():
        s = "harrypotter/severussnape"
    # Remove implied/background and other words
    stopwords = {
        "implied",
        "background",
        "established",
        "minor",
        "past",
        "relationship",
        "sort of",
        "-",
    }
    s = " ".join(
        [word for word in s.split() if word and word.lower() not in stopwords]
    )  # filter out empty words
    # Remove everything in paranthesis like (Background), (Implied)
    if s_new := re.sub(r"\([^()]*\)", "", s):
        s = s_new
    else:  # there is nothing except the text in paranthesis, get the text in paranthesis
        if s:
            s = re.search(r"\((.*?)\)", s).group(1)
        else: # There are instance of "implied" being used as a relationship tag. 
            return ""

    for splitter in {"/", "&"}:
        if splitter in s:
            s = splitter.join(
                sorted(
                    [
                        find_correct_character(
                            character.strip(),
                            get_close_matches(
                                character.strip(),
                                characters_list.name,
                                cutoff=0.1,
                            ),
                            characters_occurences,
                        )
                        if replace_w_closest_character
                        else character.replace(" ","").lower()
                        for character in s.split(splitter)
                    ]
                )
            )
    return s
