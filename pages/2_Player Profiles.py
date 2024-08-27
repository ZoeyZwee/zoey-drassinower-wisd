import pickle

import numpy as np
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plots
from plots import FigAx

# region Load Data
df = pd.read_csv("data/WISD events.csv")
df = df[df.parse_error.isna()]  # only retain rows without parse errors
df = df.drop("parse_error", axis=1)  # remove parse_error column
gp = df.groupby(["batter_name"])
stats = pd.read_csv("data/WISD stats.csv", index_col="batter_name")
stats = stats[["pitches_received", "hits", "fouls", "fair_foul_ratio", "avg_xxBA"]]

ranks_low = (
    stats[["fouls"]]
    .rank(ascending=True, na_option="top", method="min")
)
ranks_high = (
    stats[["pitches_received", "hits", "fair_foul_ratio", "avg_xxBA"]]
    .rank(ascending=False, na_option="bottom", method="max")
)
ranks = pd.concat([ranks_low, ranks_high], axis=1)
avgs = stats.agg("mean")
with open("data/WISD tracking.pickle", "rb") as f:
    tracking_frames = pickle.load(f)
# endregion Load Data

st.title("Player Profiles")
st.write("Look in-depth at an individual batter's statistics and swings")

batter = st.selectbox("Select a batter (# of hits)",
                      gp.size().sort_values(ascending=False).index,
                      format_func=lambda name: f"{name} ({gp.size()[name]})",
                      index=0
                      )


# region Stats Table
def format_rank(rank):
    match rank % 10:
        case 1:
            rank_repr = f"{rank:n}st"
        case 2:
            rank_repr = f"{rank:n}nd"
        case _:
            rank_repr = f"{rank:n}th"
    return rank_repr


metric_labels = {
    "pitches_received": "Swings",
    "hits": "Hits",
    "fouls": "Fouls",
    "fair_foul_ratio": "Fair-Foul Ratio",
    "avg_xxBA": "Average Estimated xBA"
}
batter_stats = stats.loc[[batter]].transpose(copy=True)
batter_stats.insert(0, "Rank", ranks.loc[batter].apply(format_rank))
batter_stats["League Average"] = avgs
batter_stats.reindex(metric_labels.keys())
batter_stats.index = [metric_labels[x] for x in batter_stats.index]
st.table(batter_stats)
# endregion Stats Table

# region Stat Graphics
bat_df = gp.get_group((batter,))

# region launch angle
st.subheader("Launch Angle")
launch_columns = st.columns(2)
with launch_columns[0]:  # batter
    launch_batter = FigAx(*plt.subplots(1, 1, subplot_kw=dict(projection='polar')))
    plots.launch_plot(launch_batter.ax, bat_df.launch_angle)
    launch_batter.ax.set_title(batter)
    st.pyplot(launch_batter.fig)
with launch_columns[1]:  # league overall
    launch_league = FigAx(*plt.subplots(1, 1, subplot_kw=dict(projection="polar")))
    plots.launch_plot(launch_league.ax, df.launch_angle)
    launch_league.ax.set_title("League Overall")
    st.pyplot(launch_league.fig)
# endregion launch angle

# region spray angle
st.subheader("Spray Angle")
spray_columns = st.columns(2)
with spray_columns[0]:  # batter
    spray_batter = FigAx(*plt.subplots(1, 1, subplot_kw=dict(projection='polar')))
    plots.spray_plot(spray_batter.ax, bat_df.spray_angle)
    spray_batter.ax.set_title(batter)
    st.pyplot(spray_batter.fig)
with spray_columns[1]:  # league overall
    spray_league = FigAx(*plt.subplots(1, 1, subplot_kw=dict(projection="polar")))
    plots.spray_plot(spray_league.ax, df.spray_angle)
    spray_league.ax.set_title("League Overall")
    st.pyplot(spray_league.fig)
# endregion spray angle

# region exit velocity
st.subheader("Exit Velocity")
exitv_ecdf = FigAx(*plt.subplots())
exitv_ecdf.ax.ecdf(bat_df.exit_velocity, complementary=False, label=batter, orientation="horizontal")
exitv_ecdf.ax.ecdf(df.exit_velocity.dropna(), complementary=False, label="League Overall", orientation="horizontal")
exitv_ecdf.ax.set_ylim(0, 120)
exitv_ecdf.ax.legend()
exitv_ecdf.ax.set_xlabel("Percentile")
exitv_ecdf.ax.set_ylabel("Exit Velocity (mph)")
st.pyplot(exitv_ecdf.fig)
# endregion exit velocity
# endregion Stat Graphics
with st.expander("Raw Data"):
    st.dataframe(data=gp.get_group((batter,)))
