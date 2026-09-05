# Milgram Obedience Experiment - Agent-Based Model

An agent-based reconstruction of Stanley Milgram's 1963 obedience experiment,
built with the [Mesa](https://mesa.readthedocs.io/) ABM framework (v3.5).

## Files

| File | Purpose |
|---|---|
| `agents.py` | `ParticipantAgent`, `ExperimenterAgent`, `ConfederateAgent` classes and the core decision logic |
| `model.py` | `MilgramModel` - orchestrates one run: N participants stepping together through the 15V→450V shock ladder |
| `run_experiment.py` | Batch runner: simulates 4 conditions × 30 replications × 60 participants, produces charts + CSVs |
| `streamlit_app.py` | Interactive web app - configure agents, model parameters, participants, and replications from the browser |
| `theme.py` | "Scholarly ledger" visual theme for the Streamlit app - CSS injection, masthead/footer helpers, and matplotlib chart styling |
| `.streamlit/config.toml` | Streamlit's own theme config (base colors, font). Must live in a `.streamlit/` folder next to `streamlit_app.py`, or Streamlit silently ignores it and falls back to the visitor's OS/browser theme |
| `parameter_guide.md` | Plain-language explanation of every sidebar control in the Streamlit app - what each value means, why it has the range it does, and how changing it affects the simulation |
| `requirements.txt` | Dependencies for the Streamlit app |
| `outputs/` | Generated results (see below) |

## Interactive Streamlit app

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

The app lets you configure, from the sidebar, everything the batch script
hardcodes:

- **Simulation setup**: number of participants per replication, number of
  replications per condition, random seed.
- **Conditions to run**: toggle any of the four standard conditions on/off,
  or define your own custom condition (experimenter proximity, learner
  visibility, confederates present, and an optional published/expected %
  to compare against).
- **Agent parameters**: the obedience-threshold range participants are
  drawn from, stress/authority/confederate sensitivity weights, and the
  experimenter's base pressure.
- **Situational-effect magnitudes** (collapsed by default): the calibrated
  constants - `authority_scale`, `confederate_scale`, `visible_shift`,
  `center_lo`/`center_span`, and the logistic transition steepness `k`.

All sliders default to the calibrated values used in `run_experiment.py`
(see the Calibration section below), so running with no changes reproduces
the same results. Results include the obedience-by-condition bar chart, the
voltage drop-off curve, and downloadable CSVs - all recomputed live as you
change parameters and click **Run simulation**.

The app's look (white paper background, ink-navy headings, brass/gold
accents) comes from two files working together: `.streamlit/config.toml`
sets Streamlit's own base theme, and `theme.py` layers custom CSS and chart
styling on top. Both are required for the intended appearance - if
`config.toml` isn't found in a `.streamlit/` folder, Streamlit falls back
to the browser's light/dark preference, which can leave some native
widgets (like the data table) mismatched against `theme.py`'s custom
styling.

## How the model works

**Agents**
- `ParticipantAgent` (the real subject / "teacher"): has a randomized
  `obedience_threshold ~ Uniform(0.1, 0.9)` representing baseline disposition.
  At each of the 30 shock levels it computes a probability of continuing
  vs. refusing, via a **personal "breaking point"** on the voltage scale that
  shifts up or down based on situational pressure - softened into a logistic
  curve so the transition from obeying to refusing is a gradual, noisy
  threshold rather than an all-or-nothing switch. If it hesitates, the
  experimenter issues a scripted "prod" (up to 4, matching Milgram's real
  script) which raises the pressure and prompts a retry before the
  participant genuinely quits.
- `ExperimenterAgent` (authority figure): exposes `base_pressure` and a
  `proximity_multiplier` - 1.0 when physically present, 0.08 when giving
  instructions by phone from another room (Milgram's "experimenter absent"
  variant).
- `ConfederateAgent` (planted peer "teacher"): in the "two peers rebel"
  condition (Milgram's condition 17), defects at a scripted voltage (150V),
  which sharply lowers every real participant's breaking point from that
  point on.

**Stress** accumulates each step as a function of voltage intensity, plus a
bump at each learner-reaction milestone (grunt at 75V, demands to be
released at 150V, agonized scream at 270V, ominous silence at 330V, etc.),
and itself erodes the breaking point over the course of the trial.

**Four conditions simulated** (matching real manipulations Milgram ran):

| Condition | What changes | Milgram's published obedience rate |
|---|---|---|
| Baseline | Experimenter present, learner heard but not seen | 65% |
| Experimenter absent | Instructions given by phone | 20.5% |
| Learner visible | Learner in the same room, visible | 40% |
| Two peers rebel | Two confederate co-teachers refuse at 150V | 10% |

## Calibration

The situational-effect constants (`authority_scale`, `confederate_scale`,
`visible_shift`, and the base disposition spread `center_lo`/`center_span`)
were calibrated by grid search against these four published obedience rates
- not hand-picked to look nice. The result (30 replications × 60 simulated
participants per condition):

| Condition | Simulated | Published |
|---|---|---|
| Baseline | 59.6% (±5.9) | 65.0% |
| Experimenter absent | 15.3% (±4.0) | 20.5% |
| Learner visible | 37.1% (±7.4) | 40.0% |
| Two peers rebel | 10.0% (±3.5) | 10.0% |

This is a stylized model, not a validated psychological simulation - the
point is to show how a handful of mechanisms (authority pressure, stress,
peer influence, proximity) can jointly reproduce the *pattern* of Milgram's
results, not to make claims about real obedience mechanisms.

## Outputs

Running `python3 run_experiment.py` regenerates:

- **`outputs/condition_summary.csv`** - one row per condition with mean/SD
  obedience rate vs. the published figure.
- **`outputs/participant_level_data.csv`** - one row per simulated
  participant (7,200 rows: 4 conditions × 30 reps × 60 participants), with
  their obedience threshold, max shock administered, quit voltage (if any),
  and final stress level.
- **`outputs/obedience_by_condition.png`** - bar chart, simulated vs.
  published obedience rate per condition.
- **`outputs/dropout_curve.png`** - the classic Milgram-style step chart:
  % of participants still obeying at each of the 30 voltage levels, one
  line per condition.

## Running it

```bash
pip install mesa pandas matplotlib
python3 run_experiment.py
```

To run a single condition interactively:

```python
from model import MilgramModel

model = MilgramModel(n_participants=40, proximity="present",
                      learner_visible=False, use_confederates=False, seed=1)
summary = model.run_full_experiment()
print(summary)
print(model.participant_dataframe().head())
```

Runs with the same `seed` are fully reproducible: both Mesa's own internal
randomness (via `rng=`) and each participant's `obedience_threshold` draw
are seeded from the same source, so re-running with the same seed
reproduces identical results, not just identical model-level randomness.

