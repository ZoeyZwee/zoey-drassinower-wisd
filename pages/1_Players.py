import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

df = pd.read_csv("data/WISD events.csv")
df = df[df.parse_error.isna()]
df = df.drop("parse_error", axis=1)
df = df[df.has_bat & df.has_hit]

st.write("This page contains an interactive chart. ")
# region Batter Dropdown
batter_counts = df.batter_name.value_counts()
batters = st.multiselect(
    "Batter (# of hits)",
    batter_counts.index,
    format_func=lambda name: f"{name} ({batter_counts[name]})",
    placeholder="select batters..."
)
df = df[df.batter_name.isin(batters)]
# endregion

# region Stats Table
with st.expander("Raw Data"):
    st.write("Use the left-most column to highlight points in the interactive plot!")
    st_df = st.dataframe(
        df,
        on_select="rerun",
        selection_mode="multi-row",
        column_order=["batter_name", "result", "action", "exit_velocity", "head_speed",
                      "launch_angle", "spray_angle", "bat_elevation", "bat_forward_tilt"],
        hide_index=True
    )
    
# region Plot Features
# region Feature Select Boxes
c1, c2, c3 = st.columns(3)
with c1:
    x_feature = st.selectbox("X",
                             ["exit_velocity", "head_speed", "launch_angle", "spray_angle", "bat_elevation", "bat_forward_tilt"],
                            index=0
                             )
with c2:
    y_feature = st.selectbox("Y",
                             ["exit_velocity", "head_speed", "launch_angle", "spray_angle", "bat_elevation", "bat_forward_tilt"],
                             index=2
                             )
with c3:
    group_feature = st.selectbox("Group By",
                                  ["None", "batter_name", "result"])
    if group_feature == "None":
        group_feature = None  # nightmare fuel line??
        groups = [("", slice(None))]  # includes everything
    else:
        # a single group is a boolean vector for indexing into df
        groups = [(g, df[group_feature] == g) for g in df[group_feature].unique()]
# endregion
# region Plot

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
# endregion
