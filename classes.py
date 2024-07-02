"""
For data structures and utitlity functions
"""
from dataclasses import dataclass
from typing import List


@dataclass
class Frame:
    time: float
    x: float
    y: float
    z: float

@dataclass
class PitchFrames:
    ball: List[Frame]
    head: List[Frame]
    handle: List[Frame]

    def has_bat(self):
        return self.head is not None or self.handle is not None

    def has_ball(self):
        return self.ball is not None

    @staticmethod
    def from_dict(samples_ball, samples_bat):
        """
        Convert from format in JSONL files
        :param samples_ball: dict. samples_ball field in .jsonl
        :param samples_bat: dict. samples_bat field in .jsonl
        :return: PitchFrames object with frame data.
        """

        ball_frames = [Frame(s["time"], *s["pos"]) for s in samples_ball]

        if samples_bat is None or samples_bat[0]["event"]=="No":
            head_frames = None
            handle_frames = None
        else:
            head_frames = [Frame(s["time"], *(s["head"]["pos"])) for s in samples_bat]
            handle_frames = [Frame(s["time"], *(s["handle"]["pos"])) for s in samples_bat]

        return PitchFrames(ball_frames, head_frames, handle_frames)

