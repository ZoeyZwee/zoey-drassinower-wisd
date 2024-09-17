import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

df = pd.read_csv("data/WISD events.csv")
df = df[df.parse_error.isna()]
df = df.drop("parse_error", axis=1)
df = df[df.has_bat & df.has_hit]

st.title("Data Explorer")
st.write("Use this interactive plot to compare features and discover trends in the data!")

st.subheader("Configure Plot")
# region Filters
with st.expander("Filters"):
    result_cols = st.columns(2)
    with result_cols[0]:
        include_hits = st.checkbox("Include Hits", value=True)
    with result_cols[1]:
        include_fouls = st.checkbox("Include Fouls", value=True)

    hit_mask = (df.result == "HitIntoPlay") == include_hits
    foul_mask = (df.result == "Strike") == include_fouls
    df = df[hit_mask | foul_mask]

    batter_filter_options = {
        "all": "Include all batters",
        "include": "Only include selected batters",
        "exclude": "Exclude selected batters"
    }
    batter_filter = st.selectbox("Filter Batters",
                                 options=batter_filter_options.keys(),
                                 format_func=batter_filter_options.get,
                                 )
    if batter_filter in ["include", "exclude"]:
        batter_counts = df.batter_name.value_counts()
        batters = st.multiselect(
            "Batter (# of hits)",
            batter_counts.index,
            format_func=lambda name: f"{name} ({batter_counts[name]})",
            placeholder="select batters..."
        )
        if batter_filter == "include":
            df = df[df.batter_name.isin(batters)]
        elif batter_filter == "exclude":
            df = df[~df.batter_name.isin(batters)]

    if df.size==0:
        st.markdown("**WARNING:** Dataset is empty after applying filters!")
# endregion Filters
# region Colour Groups
with st.expander("Group Data"):
    group_feature = st.selectbox(
        label="Group By",
        options=["None", "batter_name", "result"],
        index=1
    )
    match group_feature:
        case "None":
            groups = [("_", True)]  # nightmare fuel line??
        case _:
            group_options = df[group_feature].value_counts()
            group_highlight = st.multiselect(
                label="Select groups to highlight",
                options=group_options.index,
                format_func=lambda name: f"{name} ({group_options[name]})",
                default=df[group_feature].unique() if (group_options.size < 5) else None,
                placeholder="Select multiple...",
            )

            groups = [(name, df[group_feature] == name) for name in group_highlight]
            groups.insert(0, ("_all", True))
    st.write("Note: Changing filter settings may cause group settings to reset")
# endregion Colour Groups

# region Features
feature_cols = st.columns(2)
with feature_cols[0]:
    x_feature = st.selectbox(
        label="X",
        options=["xxBA", "exit_velocity", "head_speed", "head_speed_x", "head_speed_y", "head_speed_z",
                     "handle_speed", "handle_speed_x", "handle_speed_y", "handle_speed_z", "launch_angle",
                     "spray_angle", "bat_elevation", "bat_forward_tilt"],
        index=1
    )

    with feature_cols[1]:
        y_feature = st.selectbox(
            label="Y",
            options=["xxBA", "exit_velocity", "head_speed", "head_speed_x", "head_speed_y", "head_speed_z",
                     "handle_speed", "handle_speed_x", "handle_speed_y", "handle_speed_z", "launch_angle",
                     "spray_angle", "bat_elevation", "bat_forward_tilt"],
            index=0
        )
# endregion Features
# region Data Range
with st.expander("Data Range"):
    x_min, x_max = st.slider(
        label="X Range",
        min_value=df[x_feature].min(),
        max_value=df[x_feature].max(),
        step=0.5,
        value=(df[x_feature].min(), df[x_feature].max()),
        format="%.1f",
        key="x slider"
    )
    y_min, y_max = st.slider(
        label="Y Range",
        min_value=df[y_feature].min(),
        max_value=df[y_feature].max(),
        step=0.5,
        value=(df[y_feature].min(), df[y_feature].max()),
        format="%.1f",
        key="y slider"
    )

# True if point is within bounds
range_mask = ((df[x_feature] > x_min) &
              (df[x_feature] < x_max) &
              (df[y_feature] > y_min) &
              (df[y_feature] < y_max))

# endregion Data Range
# region Generate Figure
fig, ax = plt.subplots()
ax.set_xlabel(x_feature)
ax.set_ylabel(y_feature)
for label, g in groups:
    ax.scatter(
        (df[g & range_mask])[[x_feature]],
        (df[g & range_mask])[[y_feature]],
        label=label,
        s=10
    )

ax.legend()
st.pyplot(fig=fig)
# endregion
