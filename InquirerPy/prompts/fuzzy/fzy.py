# type: ignore
"""Module contains the fuzzy matching processing functions.

All fuzzy logic are copied from sweep.py.
source: https://github.com/aslpavel/sweep.py/blob/master/sweep.py

All fuzzy logic credit goes to sweep.py.

LICENSE:

MIT License

Copyright (c) 2018 Pavel Aslanov

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import asyncio
import heapq
from functools import partial
from typing import Any, Dict, List

SCORE_MIN = float("-inf")
SCORE_MAX = float("inf")
SCORE_GAP_LEADING = -0.005
SCORE_GAP_TRAILING = -0.005
SCORE_GAP_INNER = -0.01
SCORE_MATCH_CONSECUTIVE = 1.0


def char_range_with(c_start, c_stop, v, d):
    d = d.copy()
    d.update((chr(c), v) for c in range(ord(c_start), ord(c_stop) + 1))
    return d


lower_with = partial(char_range_with, "a", "z")
upper_with = partial(char_range_with, "A", "Z")
digit_with = partial(char_range_with, "0", "9")

SCORE_MATCH_SLASH = 0.9
SCORE_MATCH_WORD = 0.8
SCORE_MATCH_CAPITAL = 0.7
SCORE_MATCH_DOT = 0.6
BONUS_MAP = {
    "/": SCORE_MATCH_SLASH,
    "-": SCORE_MATCH_WORD,
    "_": SCORE_MATCH_WORD,
    " ": SCORE_MATCH_WORD,
    ".": SCORE_MATCH_DOT,
}
BONUS_STATES = [{}, BONUS_MAP, lower_with(SCORE_MATCH_CAPITAL, BONUS_MAP)]
BONUS_INDEX = digit_with(1, lower_with(1, upper_with(2, {})))


def bonus(haystack):
    """
    Additional bonus based on previous char in haystack
    """
    c_prev = "/"
    bonus = []
    for c in haystack:
        bonus.append(BONUS_STATES[BONUS_INDEX.get(c, 0)].get(c_prev, 0))
        c_prev = c
    return bonus


def subsequence(niddle, haystack):
    """
    Check if niddle is subsequence of haystack
    """
    niddle, haystack = niddle.lower(), haystack.lower()
    if not niddle:
        return True
    offset = 0
    for char in niddle:
        offset = haystack.find(char, offset) + 1
        if offset <= 0:
            return False
    return True


def compute(niddle, haystack):
    """
    Calculate score, and positions of haystack
    """
    n, m = len(niddle), len(haystack)
    bonus_score = bonus(haystack)

    if niddle.islower():
        haystack = haystack.lower()

    if n == 0 or n == m:
        return SCORE_MAX, list(range(n))

    D = [[0] * m for _ in range(n)]  # best score ending with `niddle[:i]`
    M = [[0] * m for _ in range(n)]  # best score for `niddle[:i]`

    for i in range(n):
        prev_score = SCORE_MIN
        gap_score = SCORE_GAP_TRAILING if i == n - 1 else SCORE_GAP_INNER

        for j in range(m):
            if niddle[i] == haystack[j]:
                score = SCORE_MIN
                if i == 0:
                    score = j * SCORE_GAP_LEADING + bonus_score[j]
                elif j != 0:
                    score = max(
                        M[i - 1][j - 1] + bonus_score[j],
                        D[i - 1][j - 1] + SCORE_MATCH_CONSECUTIVE,
                    )
                D[i][j] = score
                M[i][j] = prev_score = max(score, prev_score + gap_score)
            else:
                D[i][j] = SCORE_MIN
                M[i][j] = prev_score = prev_score + gap_score

    return D, M


def positions(niddle, haystack):
    n, m = len(niddle), len(haystack)

    positions = [0] * n

    if n == 0 or m == 0:
        return positions

    if n == m:
        return positions

    if m > 1024:
        return positions

    match_required = False

    D, M = compute(niddle, haystack)

    i, j = n - 1, m - 1

    while i >= 0:
        while j >= 0:
            if (match_required or D[i][j] == M[i][j]) and D[i][j] != SCORE_MIN:
                match_required = (
                    i > 0
                    and j > 0
                    and M[i][j] == D[i - 1][j - 1] + SCORE_MATCH_CONSECUTIVE
                )
                positions[i] = j
                j -= 1
                break
            else:
                j -= 1
        i -= 1

    return M[n - 1][m - 1], positions


def score(niddle, haystack):
    """
    Calculate score, and positions of haystack
    """
    n, m = len(niddle), len(haystack)
    bonus_score = bonus(haystack)

    if niddle.islower():
        haystack = haystack.lower()

    if n == 0 or n == m:
        return SCORE_MAX, list(range(n))
    D = [[0] * m for _ in range(n)]  # best score ending with `niddle[:i]`
    M = [[0] * m for _ in range(n)]  # best score for `niddle[:i]`
    for i in range(n):
        prev_score = SCORE_MIN
        gap_score = SCORE_GAP_TRAILING if i == n - 1 else SCORE_GAP_INNER

        for j in range(m):
            if niddle[i] == haystack[j]:
                score = SCORE_MIN
                if i == 0:
                    score = j * SCORE_GAP_LEADING + bonus_score[j]
                elif j != 0:
                    score = max(
                        M[i - 1][j - 1] + bonus_score[j],
                        D[i - 1][j - 1] + SCORE_MATCH_CONSECUTIVE,
                    )
                D[i][j] = score
                M[i][j] = prev_score = max(score, prev_score + gap_score)
            else:
                D[i][j] = SCORE_MIN
                M[i][j] = prev_score = prev_score + gap_score

    match_required = False
    positions = [0] * n
    i, j = n - 1, m - 1
    while i >= 0:
        while j >= 0:
            if (match_required or D[i][j] == M[i][j]) and D[i][j] != SCORE_MIN:
                match_required = (
                    i > 0
                    and j > 0
                    and M[i][j] == D[i - 1][j - 1] + SCORE_MATCH_CONSECUTIVE
                )
                positions[i] = j
                j -= 1
                break
            else:
                j -= 1
        i -= 1

    return M[n - 1][m - 1], positions


def fzy_scorer(niddle, haystack):
    if subsequence(niddle, haystack):
        return score(niddle, haystack)
    else:
        return SCORE_MIN, None


def substr_scorer(niddle, haystack):
    positions, offset = [], 0
    niddle, haystack = niddle.lower(), haystack.lower()
    for niddle in niddle.split(" "):
        if not niddle:
            continue
        offset = haystack.find(niddle, offset)
        if offset < 0:
            return float("-inf"), None
        niddle_len = len(niddle)
        positions.extend(range(offset, offset + niddle_len))
        offset += niddle_len
    if not positions:
        return 0, positions
    match_len = positions[-1] + 1 - positions[0]
    return -match_len + 2 / (positions[0] + 1) + 1 / (positions[-1] + 1), positions


async def _rank_task(scorer, niddle, haystack, offset):
    """Run the fzy match against the given haystack."""
    result = []
    for index, item in enumerate(haystack):
        score, positions = scorer(niddle, item["name"])
        if positions is None:
            continue
        result.append(
            {
                "score": score,
                "index": index + offset,
                "choice": item,
                "indices": positions,
            }
        )
    result.sort(key=lambda x: x["score"], reverse=True)
    return result


async def fuzzy_match_py_async(
    niddle: str, haystack: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Run filter of niddle against haystack.

    Run the tasks in 4096 batchs in parallel using
    `asyncio.gather`.
    """
    if " " in niddle:
        scorer = substr_scorer
    else:
        scorer = fzy_scorer

    batch_size = 4096
    batches = await asyncio.gather(
        *(
            _rank_task(scorer, niddle, haystack[offset : offset + batch_size], offset)
            for offset in range(0, len(haystack), batch_size)
        ),
    )
    results = heapq.merge(*batches, key=lambda x: x["score"], reverse=True)
    choices = []
    for candidate in results:
        choices.append({**candidate["choice"], "indices": candidate["indices"]})
    return choices
