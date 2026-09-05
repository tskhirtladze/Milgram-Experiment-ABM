

import statistics as stats

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

import sys

st.set_page_config(page_title="Milgram Obedience ABM", layout="wide")

import theme
theme.inject_css()

try:
    from model import MilgramModel
    from agents import SHOCK_LEVELS
except ModuleNotFoundError as e:
    st.error(f"Import failed: {e}")
    st.write("Python executable Streamlit is using:", sys.executable)
    st.write("sys.path:", sys.path)
    try:
        import mesa
        st.write("mesa found at:", mesa.__file__, "version:", mesa.__version__)
    except ModuleNotFoundError:
        st.write("mesa is NOT importable from this interpreter.")
    st.stop()

# --------------------------------------------------------------------------
# Standard conditions (mirrors run_experiment.py) with published comparison
# --------------------------------------------------------------------------
STANDARD_CONDITIONS = {
    "Baseline (experimenter present)": dict(
        params=dict(proximity="present", learner_visible=False, use_confederates=False),
        published_pct=65.0,
    ),
    "Experimenter absent (phone)": dict(
        params=dict(proximity="remote", learner_visible=False, use_confederates=False),
        published_pct=20.5,
    ),
    "Learner visible (same room)": dict(
        params=dict(proximity="present", learner_visible=True, use_confederates=False),
        published_pct=40.0,
    ),
    "Two peers rebel": dict(
        params=dict(proximity="present", learner_visible=False, use_confederates=True),
        published_pct=10.0,
    ),
}

if "custom_conditions" not in st.session_state:
    st.session_state.custom_conditions = {}

# --------------------------------------------------------------------------
# Sidebar - simulation setup
# --------------------------------------------------------------------------
st.sidebar.header("Simulation setup")

n_participants = st.sidebar.slider(
    "Participants per replication", min_value=5, max_value=300, value=60, step=5
)
n_replications = st.sidebar.slider(
    "Replications per condition", min_value=1, max_value=100, value=30, step=1
)
base_seed = st.sidebar.number_input("Base random seed", value=1000, step=1)

st.sidebar.header("Conditions to run")
selected_standard = []
for label in STANDARD_CONDITIONS:
    if st.sidebar.checkbox(label, value=True, key=f"std_{label}"):
        selected_standard.append(label)

with st.sidebar.expander("➕ Add a custom condition"):
    custom_name = st.text_input("Condition name", key="custom_name")
    custom_proximity = st.selectbox(
        "Experimenter proximity", ["present", "remote"], key="custom_proximity"
    )
    custom_visible = st.checkbox("Learner visible (same room)", key="custom_visible")
    custom_confed = st.checkbox("Confederates present", key="custom_confed")
    custom_published = st.number_input(
        "Published/expected obedience % (optional, for comparison)",
        min_value=0.0, max_value=100.0, value=0.0, step=0.5, key="custom_published",
    )
    if st.button("Add condition"):
        if custom_name.strip():
            st.session_state.custom_conditions[custom_name] = dict(
                params=dict(
                    proximity=custom_proximity,
                    learner_visible=custom_visible,
                    use_confederates=custom_confed,
                ),
                published_pct=custom_published if custom_published > 0 else None,
            )
        else:
            st.warning("Give the condition a name first.")

selected_custom = []
if st.session_state.custom_conditions:
    st.sidebar.caption("Custom conditions")
    for label in list(st.session_state.custom_conditions):
        col1, col2 = st.sidebar.columns([4, 1])
        with col1:
            if st.checkbox(label, value=True, key=f"custom_chk_{label}"):
                selected_custom.append(label)
        with col2:
            if st.button("✕", key=f"remove_{label}"):
                del st.session_state.custom_conditions[label]
                st.rerun()

st.sidebar.header("Agent parameters")
obedience_range = st.sidebar.slider(
    "Obedience threshold range (disposition)",
    min_value=0.0, max_value=1.0, value=(0.1, 0.9), step=0.05,
    help="Each participant's baseline compliance disposition is drawn uniformly from this range.",
)
stress_weight = st.sidebar.slider(
    "Stress sensitivity", min_value=0.0, max_value=2.0, value=0.6, step=0.05,
    help="How much accumulated stress erodes willingness to continue.",
)
authority_weight = st.sidebar.slider(
    "Authority sensitivity", min_value=0.0, max_value=2.0, value=0.9, step=0.05,
    help="How much the experimenter's pressure raises the breaking point.",
)
confederate_penalty = st.sidebar.slider(
    "Confederate defection sensitivity", min_value=0.0, max_value=1.0, value=0.35, step=0.05,
    help="How strongly a peer's refusal lowers the participant's breaking point.",
)
experimenter_base_pressure = st.sidebar.slider(
    "Experimenter base pressure", min_value=0.0, max_value=2.0, value=0.5, step=0.05,
)
confed_v1, confed_v2 = st.sidebar.slider(
    "Confederate defection voltages",
    min_value=15, max_value=450, value=(150, 210), step=15,
    help="Voltages at which the two confederates refuse, in conditions where they're present.",
)

with st.sidebar.expander("⚙️ Situational-effect magnitudes (calibrated defaults)"):
    authority_scale = st.slider(
        "Authority scale", min_value=0, max_value=1200, value=700, step=10,
        help="Magnitude of the authority-pressure shift on the breaking point. "
             "Values much above ~900 tend to force near-100% obedience regardless of other settings.",
    )
    confederate_scale = st.slider(
        "Confederate scale", min_value=0, max_value=1200, value=950, step=10,
        help="Magnitude of the peer-defection shift on the breaking point. "
             "Values much above ~1000 tend to force near-0% obedience once a confederate defects.",
    )
    visible_shift = st.slider(
        "Learner-visible shift", min_value=-500, max_value=0, value=-150, step=10,
        help="Shift applied to the breaking point when the learner is visible.",
    )
    center_lo = st.slider(
        "Disposition center (low)", min_value=-500, max_value=100, value=-250, step=10,
    )
    center_span = st.slider(
        "Disposition center (span)", min_value=100, max_value=1000, value=800, step=10,
    )
    k = st.slider(
        "Transition steepness (k)", min_value=0.02, max_value=0.3, value=0.09, step=0.01,
        help="How sharp the obey→refuse transition is around each participant's breaking point.",
    )

# --------------------------------------------------------------------------
# Build the list of conditions to run
# --------------------------------------------------------------------------
conditions_to_run = {}
for label in selected_standard:
    conditions_to_run[label] = STANDARD_CONDITIONS[label]
for label in selected_custom:
    conditions_to_run[label] = st.session_state.custom_conditions[label]

# --------------------------------------------------------------------------
# Main panel
# --------------------------------------------------------------------------
theme.masthead(
    "Milgram Obedience Experiment",
    "An agent-based reconstruction · Configure agents and situational parameters in the sidebar",
)
st.markdown("""
## About the Milgram Obedience Experiment

In 1963, psychologist **Stanley Milgram** ran a study at Yale to answer a
troubling question: how far would ordinary people go in harming another
person, simply because an authority figure told them to?

Participants were told they were helping test how punishment affects
learning. Playing the "teacher," they were instructed to give a "learner"
(secretly an actor, never actually shocked) increasingly painful electric
shocks - from **15V up to a lethal-looking 450V** - every time an answer
was wrong. As the voltage rose, the learner would grunt, cry out, beg to
be released, and eventually fall silent. Whenever a participant hesitated,
the experimenter simply insisted they continue.

The result shocked the field: **about 65% of participants went all the
way to 450V**, despite visible distress. Milgram ran several variations -
moving the experimenter out of the room, making the learner visible, or
adding peers who refused to continue - and found obedience swung sharply
with the situation, from as low as 10% to as high as 65%.

This app lets you explore an **agent-based model (ABM)** of that
experiment: simulated participants, each with their own disposition,
"decide" whether to keep obeying at every voltage step, shaped by
authority pressure, stress, and peer influence - so you can test how
those forces interact under conditions Milgram never even ran.
""")

total_runs = n_participants * n_replications * max(1, len(conditions_to_run))
st.caption(
    f"This will simulate **{len(conditions_to_run)}** condition(s) × "
    f"**{n_replications}** replications × **{n_participants}** participants "
    f"({total_runs:,} simulated participants total, 30 voltage steps each)."
)

run_clicked = st.button("🔬 Run simulation", type="primary", disabled=(len(conditions_to_run) == 0))

if len(conditions_to_run) == 0:
    st.info("Select at least one condition in the sidebar to run the simulation.")


def run_batch(conditions, n_participants, n_replications, base_seed, agent_kwargs, situational_kwargs):
    summary_rows = []
    participant_rows = []
    dropout_curves = {}

    progress = st.progress(0.0, text="Starting...")
    total_steps = len(conditions) * n_replications
    step_count = 0

    for label, cfg in conditions.items():
        rep_obedience_rates = []
        rep_dropout_matrices = []

        for rep in range(n_replications):
            model = MilgramModel(
                n_participants=n_participants,
                seed=int(base_seed) + rep,
                **cfg["params"],
                **situational_kwargs,
                **agent_kwargs,
            )
            voltage_pct = []
            while model.running:
                model.step()
                voltage_pct.append(model._pct_still_obeying())
            rep_dropout_matrices.append(voltage_pct)

            summ = model.summary()
            rep_obedience_rates.append(summ["obedience_rate_pct"])

            df = model.participant_dataframe()
            df["condition"] = label
            df["replication"] = rep
            participant_rows.append(df)

            step_count += 1
            progress.progress(step_count / total_steps, text=f"Running: {label} (rep {rep + 1}/{n_replications})")

        mean_obedience = stats.mean(rep_obedience_rates)
        sd_obedience = stats.pstdev(rep_obedience_rates) if len(rep_obedience_rates) > 1 else 0.0
        avg_curve = [
            stats.mean(rep[i] for rep in rep_dropout_matrices) for i in range(len(SHOCK_LEVELS))
        ]
        dropout_curves[label] = avg_curve

        summary_rows.append(
            {
                "condition": label,
                "n_participants_per_rep": n_participants,
                "n_replications": n_replications,
                "simulated_obedience_pct_mean": round(mean_obedience, 1),
                "simulated_obedience_pct_sd": round(sd_obedience, 1),
                "published_obedience_pct": cfg["published_pct"],
            }
        )

    progress.empty()
    summary_df = pd.DataFrame(summary_rows)
    participant_df = pd.concat(participant_rows, ignore_index=True)
    return summary_df, participant_df, dropout_curves


def make_bar_chart(summary_df):
    has_published = summary_df["published_obedience_pct"].notna().any()
    fig, ax = plt.subplots(figsize=(8, 5))
    x = range(len(summary_df))
    width = 0.35 if has_published else 0.5

    offset = width / 2 if has_published else 0
    ax.bar(
        [i - offset for i in x],
        summary_df["simulated_obedience_pct_mean"],
        width,
        yerr=summary_df["simulated_obedience_pct_sd"],
        capsize=4,
        label="ABM simulation",
        color=theme.NAVY,
    )
    if has_published:
        ax.bar(
            [i + width / 2 for i in x],
            summary_df["published_obedience_pct"],
            width,
            label="Published / expected",
            color=theme.GOLD,
        )

    ax.set_xticks(list(x))
    ax.set_xticklabels(summary_df["condition"], rotation=20, ha="right")
    ax.set_ylabel("% of participants obedient to 450V")
    ax.set_title("Simulated Obedience Rate by Condition")
    ax.legend()
    fig.tight_layout()
    theme.style_chart(fig, ax)
    return fig


def make_dropout_chart(dropout_curves):
    fig, ax = plt.subplots(figsize=(8, 5))
    for color, (label, curve) in zip(theme.CHART_PALETTE, dropout_curves.items()):
        ax.plot(SHOCK_LEVELS, curve, marker="o", markersize=3, label=label, color=color)
    ax.set_xlabel("Shock level administered (Volts)")
    ax.set_ylabel("% of participants still obeying")
    ax.set_title("Obedience Drop-off Curve by Voltage")
    ax.axvline(330, color=theme.INK_SOFT, linestyle="--", linewidth=1, label="Learner falls silent (330V)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    theme.style_chart(fig, ax)
    return fig


if run_clicked and conditions_to_run:
    agent_kwargs = dict(
        obedience_threshold_range=tuple(obedience_range),
        stress_weight=stress_weight,
        authority_weight=authority_weight,
        confederate_penalty=confederate_penalty,
        experimenter_base_pressure=experimenter_base_pressure,
        confederate_defect_voltages=(confed_v1, confed_v2),
    )
    situational_kwargs = dict(
        authority_scale=authority_scale,
        confederate_scale=confederate_scale,
        visible_shift=visible_shift,
        center_lo=center_lo,
        center_span=center_span,
        k=k,
    )

    with st.spinner("Running simulation..."):
        summary_df, participant_df, dropout_curves = run_batch(
            conditions_to_run, n_participants, n_replications, base_seed, agent_kwargs, situational_kwargs
        )

    st.session_state["summary_df"] = summary_df
    st.session_state["participant_df"] = participant_df
    st.session_state["dropout_curves"] = dropout_curves

if "summary_df" in st.session_state:
    summary_df = st.session_state["summary_df"]
    participant_df = st.session_state["participant_df"]
    dropout_curves = st.session_state["dropout_curves"]

    st.subheader("Results")
    col1, col2 = st.columns(2)
    with col1:
        st.pyplot(make_bar_chart(summary_df))
    with col2:
        st.pyplot(make_dropout_chart(dropout_curves))

    theme.eyebrow("Data")
    st.markdown("**Condition summary**")
    st.dataframe(summary_df, width="stretch")
    st.download_button(
        "⬇️ Download condition summary (CSV)",
        summary_df.to_csv(index=False),
        file_name="condition_summary.csv",
        mime="text/csv",
    )

    with st.expander("Participant-level data"):
        st.dataframe(participant_df, width="stretch")
        st.download_button(
            "⬇️ Download participant-level data (CSV)",
            participant_df.to_csv(index=False),
            file_name="participant_level_data.csv",
            mime="text/csv",
        )
else:
    st.info("Configure parameters in the sidebar and click **Run simulation** to see results.")

theme.footer("<strong>Milgram Obedience ABM</strong> - agent-based simulation, not human-subject data")