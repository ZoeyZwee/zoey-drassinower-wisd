import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import pickle

df = pd.read_csv("data/WISD events.csv")
df = df[df.parse_error.isna()]
df = df.drop("parse_error", axis=1)
df = df[df.has_bat & df.has_hit]

st.title("Data Explorer")
st.write("Use this interactive plot to compare features and discover trends in the data!")

# region Batter Dropdown

st.subheader("Select Batters")
batter_counts = df.batter_name.value_counts()
batters = st.multiselect(
    "Batter (# of hits)",
    batter_counts.index,
    format_func=lambda name: f"{name} ({batter_counts[name]})",
    placeholder="select batters..."
)
if batters:
    df = df[df.batter_name.isin(batters)]
# endregion

# region Stats Table
with st.expander("Highlight Data"):
    st.write("Use the left-most column to highlight points in the interactive plot!")
    st_df = st.dataframe(
        df,
        on_select="rerun",
        selection_mode="multi-row",
        column_order=["batter_name", "result", "action", "xxBA", "exit_velocity", "head_speed",
                      "launch_angle", "spray_angle", "bat_elevation", "bat_forward_tilt"],
        hide_index=True
    )

# endregion

# region Select Plotting Features
st.subheader("Select Features")
c1, c2, c3 = st.columns(3)
with c1:
    x_feature = st.selectbox("X",
                             ["xxBA", "exit_velocity", "head_speed", "launch_angle", "spray_angle", "bat_elevation",
                              "bat_forward_tilt"],
                             index=3
                             )
with c2:
    y_feature = st.selectbox("Y",
                             ["xxBA", "exit_velocity", "head_speed", "launch_angle", "spray_angle", "bat_elevation",
                              "bat_forward_tilt"],
                             index=1
                             )
with c3:
    group_feature = st.selectbox("Group By",
                                 ["None", "batter_name", "result"])
    if group_feature == "None":
        group_feature = None  # nightmare fuel line??


with st.expander(label="Set Data Range"):
    x_min, x_max = st.slider(
        label=x_feature,
        min_value=df[x_feature].min(),
        max_value=df[x_feature].max(),
        step=0.01,
        value=(df[x_feature].min(), df[x_feature].max()),
        format="%.1f",
        key="x slider"
    )
    y_min, y_max = st.slider(
        label=y_feature,
        min_value=df[y_feature].min(),
        max_value=df[y_feature].max(),
        step=0.01,
        value=(df[y_feature].min(), df[y_feature].max()),
        format="%.1f",
        key="y slider"
    )

# apply data range
df = df[(df[x_feature]>x_min) & (df[x_feature]<x_max) & (df[y_feature]>y_min) & (df[y_feature]<y_max)]
# create groups
if group_feature is None:
    groups = [("", slice(None))]  # includes everything
else:
    # a group is a boolean vector for indexing into df
    # groups is a list of groups
    groups = [(g, df[group_feature] == g) for g in df[group_feature].unique()]

# endregion

# region Show Plot
fig, ax = plt.subplots()
ax.set_xlabel(x_feature)
ax.set_ylabel(y_feature)
for (label, g) in groups:
    ax.scatter(
        (df[g])[[x_feature]],
        (df[g])[[y_feature]],
        label=label
    )
# highlight selected swings
if st_df.selection.rows:
    # get row data for highlighted swing
    highlights = df.iloc[st_df.selection.rows]
    ax.scatter(highlights[[x_feature]], highlights[[y_feature]],
               marker="o", facecolors="none", edgecolors="magenta",
               linewidth=1, s=85)

if group_feature is not None:
    ax.legend()
st.pyplot(fig=fig)
# endregion
