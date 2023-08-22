from abc import ABC, abstractmethod
from typing import Any
import numpy as np
from joblib import Parallel, delayed
from dataclasses import dataclass
import pandas as pd

@dataclass
class LevelSummary:
    level_index: int
    win_rate: float
    boosters: dict[str, int]
    churn: bool
    loses: int


class LevelStringParser:

    _start = 'start'
    _win = 'win'
    _lose = 'lose'
    _churn = 'churn'

    boosters_counts = {"amuletBomb": 0,
                       "amuletMoves": 0,
                       "horn": 0,
                       "boostHammer": 0,
                       "boostCross": 0,
                       "boostSwapElements": 0,
                       'preingame_bomb': 0,
                       "preingame_multicolor": 0,
                       'preingame_firework': 0,
                       'preingame_steps': 0,
                       "additionalMoves": 0,
                       "inGameBomb": 0,
                       "inGameTnt": 0,
                       "inGameBigTnt": 0}

    @staticmethod
    def _to_trajectories(words: list[str]) -> list[list[str]]:
        words_np = np.array(words)
        end_lvl_poses = np.append(np.argwhere(words_np == 'win'), np.argwhere(words_np == 'churn')).reshape((-1,))

        trajectories = []
        start_idx = 0

        for idx in end_lvl_poses:
            trajectory = words[start_idx:idx + 1]
            trajectories.append(trajectory)
            start_idx = idx + 1

        return trajectories

    @staticmethod
    def parse(text_string: str) -> list[LevelSummary]:

        text_words = text_string.split(' ')
        start = text_words[0]

        if start != LevelStringParser._start:
            raise Exception(f"Wrong start token,{LevelStringParser._start} token expected, got {start}")

        levels_trajectories = LevelStringParser._to_trajectories(words=text_words)

        levels_summaries = []
        for level_index, level_trajectory in enumerate(levels_trajectories):

            churn = LevelStringParser._churn in level_trajectory
            loses_count = 0

            boosters_summary = LevelStringParser.boosters_counts.copy()

            for word in level_trajectory:
                if word == LevelStringParser._lose:
                    loses_count += 1

                elif word in boosters_summary.keys():
                    boosters_summary[word] += 1

                elif word not in (LevelStringParser._win,LevelStringParser._start,LevelStringParser._churn):
                    raise Exception(f'Unknown token: {word}')

            win_rate = (LevelStringParser._win in level_trajectory) / (loses_count + 1)

            lvl_summary = LevelSummary(level_index=level_index,
                                       win_rate=win_rate,
                                       boosters=boosters_summary,
                                       churn=churn,
                                       loses=loses_count)

            levels_summaries.append(lvl_summary)

        return levels_summaries


class Sample:
    def __init__(self, text_string: str):
        self.text_string = text_string
        self.levels = self._parsed_levels

    @property
    def _parsed_levels(self) -> list[LevelSummary]:
        return LevelStringParser.parse(text_string=self.text_string)


class LevelsSampler:

    def __init__(self, texts: list[str]):
        self._texts = texts

    @property
    def to_levels(self) -> list[list[Sample]]:
        out = Parallel(n_jobs=-1)(delayed(LevelStringParser.parse)(text_str) for text_str in self._texts)
        return out


class SamplersSummarizer:
    def __init__(self, samples: list[list[Sample]]):
        self._samples_list = samples

    @staticmethod
    def _to_df(samples: list[Sample]) -> pd.DataFrame:
        df = pd.DataFrame()
        for idx,level_summary in enumerate(samples):

            data_dict = {
                "level_index": level_summary.level_index,
                "win_rate": level_summary.win_rate,
                "loses": level_summary.loses,
                "churn": level_summary.churn
            }
            data_dict.update(level_summary.boosters)

            data = pd.DataFrame(data_dict, index=[idx])
            df = pd.concat([df, data])
        return df

    @property
    def summary(self) -> pd.DataFrame:
        out = Parallel(n_jobs=-1)(delayed(self._to_df)(samples) for samples in self._samples_list)
        summary = pd.concat(out)
        return summary


class TextStringsMetrics:
    def __init__(self, texts: list[str]):
        self.texts = texts

    @property
    def metrics(self) -> pd.DataFrame:
        samples_with_levels = LevelsSampler(texts=self.texts).to_levels
        df = SamplersSummarizer(samples=samples_with_levels).summary
        return df








