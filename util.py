"""
For data structures and useful functions
"""

from dataclasses import dataclass
from typing import List, Optional
import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial import Polynomial


@dataclass
class Frame:
    time: float
    x: float
    y: float
    z: float
    speed: Optional[float] = None
    vx: Optional[float] = None
    vy: Optional[float] = None
    vz: Optional[float] = None

def visualize_swing(ax, frames, bat_buffer=0.07, ball_buffer=0.3):
    """ Visualize moments before/after the bat and ball make contact (or closest approach).
    :param fig: MatplotLib figure to render on
    :param frames: PitchFrames w/ data for bat and ball
    :param bat_buffer: how many seconds before/after contact to display. default=0.07
    :param ball_buffer: how many seconds before/after contact to display. default=0.3
    :return:
    """

    # calculate time of contact
    t_contact = frames.hit_time

    # get frames near time of contact
    ball_x, ball_y, ball_z, ball_time = extract_coords_from_frames(frames.ball, start=t_contact - ball_buffer,
                                                                   end=t_contact + ball_buffer)
    head_x, head_y, head_z, head_time = extract_coords_from_frames(frames.head, start=t_contact - bat_buffer,
                                                                   end=t_contact + bat_buffer)
    handle_x, handle_y, handle_z, _ = extract_coords_from_frames(frames.handle, start=t_contact - bat_buffer,
                                                                 end=t_contact + bat_buffer)

    # draw ball
    ax.scatter(ball_x, ball_y, ball_z, c=ball_time, cmap=plt.colormaps['inferno'])

    # draw bat
    cmap = plt.colormaps['inferno'].resampled(len(head_time))
    for i in range(len(head_time)):
        x = [head_x[i], handle_x[i]]
        y = [head_y[i], handle_y[i]]
        z = [head_z[i], handle_z[i]]
        ax.plot(x, y, z, c=cmap(i))
    plt.xlabel("x")
    plt.ylabel("y")
    set_axes_equal(ax)


def set_axes_equal(ax):
    """
    Make axes of 3D plot have equal scale so that spheres appear as spheres,
    cubes as cubes, etc.

    Input
      ax: a matplotlib axis, e.g., as output from plt.gca().
    """

    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = abs(x_limits[1] - x_limits[0])
    x_middle = np.mean(x_limits)
    y_range = abs(y_limits[1] - y_limits[0])
    y_middle = np.mean(y_limits)
    z_range = abs(z_limits[1] - z_limits[0])

    # The plot bounding box is a sphere in the sense of the infinity
    # norm, hence I call half the max range the plot radius.
    plot_radius = 0.5 * max([x_range, y_range, z_range])

    ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
    ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
    ax.set_zlim3d([0, plot_radius])


def time_of_contact(head_frames, handle_frames, ball_frames):
    """ return time at which the ball and bat are closest to each other.
    Not actually required, since the bat tracking data has the time of hits - oops!
    :param head_frames: List[Frame]. tracking data for bat head
    :param handle_frames: List[Frame]. tracking data for bat handle.
    :param ball_frames: List[Frame]. tracking data for ball
    """
    best_dist = np.Infinity  # closest distance between bat and ball
    t_0 = None
    for ball in ball_frames:
        # find the index of head frame which is closest in time to the ball frame.
        # can use the index to get the position of both the head and handle, since they have the same time data
        idx = min(range(len(head_frames)), key=lambda i: abs(head_frames[i].time - ball.time))
        head = head_frames[idx]
        handle = handle_frames[idx]

        # calculate the distance between the ball and bat, using the line defined by the head and handle
        # lin alg explained here: https://mathworld.wolfram.com/Point-LineDistance3-Dimensional.html
        head_pos = np.array([head.x, head.y, head.z])
        handle_pos = np.array([handle.x, handle.y, handle.z])
        ball_pos = np.array([ball.x, ball.y, ball.z])

        v1 = np.cross(ball_pos - handle_pos,
                      ball_pos - head_pos)  # area vector for 2x the triangle defined by the 3 points
        v2 = handle_pos - head_pos  # base of triangle
        dist = np.dot(v1, v1) / np.dot(v2, v2)

        if dist < best_dist:
            best_dist = dist
            t_0 = head.time
    return t_0


def extract_coords_from_frames(frames: List[Frame], start=-999, end=999):
    """
    Takes a list of frames, returns vectors corresponding to each coordinate.
    set start and end to only consider frames within a certain time window
    """
    x = [f.x for f in frames if start < f.time < end]
    y = [f.y for f in frames if start < f.time < end]
    z = [f.z for f in frames if start < f.time < end]
    time = [f.time for f in frames if start < f.time < end]
    return x, y, z, time


@dataclass
class PitchFrames:
    ball: List[Frame]
    head: List[Frame]
    handle: List[Frame]
    hit_time: float

    def has_bat(self):
        return self.head is not None and self.handle is not None

    @staticmethod
    def from_dict(samples_ball, samples_bat):
        """
        Generate a PitchFrames object from the dictionaries in the JSONL files
        :param samples_ball: dict. samples_ball field in .jsonl
        :param samples_bat: dict. samples_bat field in .jsonl
        :return: PitchFrames object with frame data.
        """

        # ball
        ball_frames = [Frame(s["time"], *s["pos"]) for s in samples_ball]

        # bat
        if samples_bat is None or samples_bat[0]["event"] == "No":
            head_frames = None
            handle_frames = None
        else:
            # create Frame objects
            head_frames = [Frame(s["time"], *(s["head"]["pos"])) for s in samples_bat]
            handle_frames = [Frame(s["time"], *(s["handle"]["pos"])) for s in samples_bat]

            # add velocity to Frames
            PitchFrames._calculate_velocity(head_frames)
            PitchFrames._calculate_velocity(handle_frames)

        # get time of contact
        temp = [s["time"] for s in samples_bat if ("event", "Hit") in s.items()]
        try:
            hit_time = temp[0]
        except IndexError:
            # indicates no hit event
            hit_time = None

        return PitchFrames(ball_frames, head_frames, handle_frames, hit_time)

    @staticmethod
    def _calculate_velocity(frames):
        """
        adds velocity information (speed and components) to a list of Frames
        velocity is taken as average over a centred window of 10 frames.
        does not update frames too close to list boundaries

        updates frame object in place.
        :param frames: list of Frame objects
        :returns: None.
        """
        for start, mid, end in zip(frames[:-4], frames[2:-2], frames[4:]):
            # mid takes average velocity over window [start, end]
            delta_time = end.time - start.time
            mid.vx = (end.x-start.x)/delta_time
            mid.vy = (end.y-start.y)/delta_time
            mid.vz = (end.z-start.z)/delta_time
            mid.speed = np.sqrt(mid.vx**2 + mid.vy**2 + mid.vz**2)
