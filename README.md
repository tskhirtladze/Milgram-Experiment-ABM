# Milgram Obedience Experiment - Agent-Based Model

An open, interactive agent-based model exploring the relationship between **Milgram's obedience experiments, computational modelling, model assumptions, and reproducibility**.

The model is built with the [Mesa](https://mesa.readthedocs.io/) agent-based modelling framework and provides both a reproducible batch experiment and an interactive [Streamlit](https://streamlit.io/) application.

> **Important:** This is a stylized computational model, not a validated psychological simulation or an empirical replication of Milgram's experiments. The model is intended to explore how assumptions about authority, situational pressure, stress, peer influence, and proximity can produce patterns resembling published findings.

**Try it live:** [milgram-experiment-abm-ts.streamlit.app](https://milgram-experiment-abm-ts.streamlit.app/)

## Why this project?

Milgram's obedience experiments are often presented to students as a set of fixed experimental results. This project provides an interactive way to explore a different question:

> **What assumptions about individual behaviour and social context are required for a computational model to produce a pattern resembling the published results?**

Users can modify model parameters, run repeated simulations, inspect participant-level data, and compare simulated outcomes with published obedience rates.

The project can be used to discuss:

* the difference between empirical evidence and model assumptions;
* computational modelling of social behaviour;
* reproducibility and stochastic variation;
* model calibration and parameter sensitivity;
* the difference between reproducing an outcome and validating an explanation;
* open and reproducible research practices.

## Empirical basis

The model is inspired by several conditions from Stanley Milgram's obedience experiments rather than representing a single experiment.

Milgram's original series included a baseline condition in which the learner was physically separated from the participant and the experimenter remained present. In this condition, **26 of 40 participants (65%)** continued to the maximum 450-volt level.

Later experiments changed specific aspects of the situation, including the physical proximity of the learner, the presence of the experimenter, and the behaviour of peer confederates.

The four empirical targets currently used by the model correspond to the following conditions:

| Model condition     | Milgram experiment | Experimental manipulation                                | `learner_feedback` | Published obedience rate |
| ------------------- | ------------------ | ---------------------------------------------------------- | ------------------: | -----------------------: |
| Baseline            | Experiment 1       | Experimenter present; learner separated from participant | `"none"`            |            65.0% (26/40) |
| Experimenter absent | Experiment 7       | Experimenter leaves and gives instructions by telephone  | `"none"`            |                    20.5% |
| Learner visible     | Experiment 3       | Learner is placed in the same room as the participant    | `"voice"`           |            40.0% (16/40) |
| Two peers rebel     | Experiment 17      | Two peer confederates refuse to continue                 | `"voice"`           |             10.0% (4/40) |

These percentages come from different parts of Milgram's experimental programme and should not be interpreted as four conditions from a single experiment.

The 65% result is associated with Milgram's original baseline condition (Experiment 1). The 40% result comes from the learner-proximity manipulation (Experiment 3), while the 20.5% result comes from the experimenter-absent/telephone condition (Experiment 7). The two-peer condition is Experiment 17, in which only 4 of 40 participants continued to the maximum shock level. These experiment numbers follow Milgram's experimental numbering as presented in *Obedience to Authority* (1974).

### Important distinction: empirical condition vs. model implementation

The historical procedures should not be confused with the mechanisms implemented in this computational model.

In particular, the current model includes a sequence of simulated learner reactions and a stress mechanism. These are **model assumptions inspired by the experimental procedure**, rather than a complete reconstruction of the exact stimulus sequence used in any one historical condition.

The model therefore uses the published obedience rates as **aggregate empirical targets**, while the behavioural mechanisms used to generate those rates are computational assumptions.

### Voice-feedback condition

Milgram also studied a condition in which the learner's vocal responses could be heard but the learner was not visible. A later synthesis of Milgram's conditions reports **25 of 40 participants (62.5%)** reaching the maximum shock in this voice-feedback condition.

This is distinct from the **65% no-feedback baseline**.

The current model contains learner-reaction events that resemble a voice-feedback procedure. Consequently, the model should not be described as an exact reconstruction of the historical Experiment 1 procedure unless the learner-feedback mechanism is explicitly configured to reproduce the no-feedback condition.

This distinction is intentional: the project separates the **empirical target** from the **computational assumptions used to model it**.

### `learner_feedback`: making the no-feedback / voice-feedback distinction explicit

The model now exposes a `learner_feedback` parameter on `MilgramModel`, with two values:

* `"none"` — no scripted learner reactions are generated at any voltage. This is used for the **Baseline** and **Experimenter absent** conditions, which correspond to Milgram's original 65% and 20.5% results.
* `"voice"` — the full scripted reaction sequence (grunt, shout of pain, demands to be released, ... ominous silence) is active, contributing to the participant's simulated stress. This is used for the **Learner visible** and **Two peers rebel** conditions.

This makes the empirical distinction discussed above (65% no-feedback baseline vs. 62.5% voice-feedback condition) something the model can actually represent, rather than only being discussed in prose. Note that the model does not currently include a dedicated 62.5% voice-feedback calibration target — `learner_feedback="voice"` is only exercised, in the four standard conditions, alongside other situational manipulations (learner visibility, peer confederates). Adding a fifth condition that isolates voice feedback alone against the 62.5% target would be a natural extension.

## What is empirical and what is modelled?

An important purpose of this project is to keep empirical findings separate from assumptions introduced by the computational model.

| Component                       | Status                                                   |
| ------------------------------- | -------------------------------------------------------- |
| Published obedience rates       | Empirical findings reported in the literature            |
| Experimental conditions         | Based on published descriptions of Milgram's experiments |
| Participant obedience threshold | Model assumption                                         |
| Stress accumulation             | Model assumption                                         |
| Authority pressure              | Model assumption                                         |
| Peer influence                  | Model assumption                                         |
| Logistic decision function      | Model assumption                                         |
| Learner reaction milestones     | Model assumption inspired by experimental procedure      |
| Situational-effect parameters   | Model parameters calibrated against aggregate outcomes   |

**Calibration does not demonstrate that the model's mechanisms caused the original experimental results.**

A model can reproduce an observed pattern for many different reasons. Matching an empirical outcome therefore does not, by itself, validate the assumptions or mechanisms used by the model.

## How the model works

### Participant agents

`ParticipantAgent` represents the simulated participant/"teacher".

Each participant receives a randomized baseline `obedience_threshold` drawn from:

```text
Uniform(0.1, 0.9)
```

At each of the 30 shock levels, the participant calculates a probability of continuing versus refusing.

The model represents this as a personal breaking point on the voltage scale that can shift according to situational pressure. A logistic function turns this into a gradual, probabilistic transition rather than an all-or-nothing decision.

If a participant hesitates, the experimenter can issue the scripted experimental prods before the participant ultimately refuses or continues.

### Experimenter agent

`ExperimenterAgent` represents the authority figure.

The model includes:

* `base_pressure`
* `proximity_multiplier`

The default proximity multiplier is:

```text
1.0  - experimenter physically present
0.08 - experimenter gives instructions by telephone
```

The telephone condition represents the experimenter-absent variation associated with Milgram's Experiment 7, for which published accounts report a 20.5% full-obedience rate.

### Confederate agents

`ConfederateAgent` represents planted peer participants.

In the **two peers rebel** condition, two confederate peers progressively refuse to continue.

The current model represents the two interventions at:

```text
150 V - first confederate refuses
210 V - second confederate refuses
```

The peer intervention produces a strong downward shift in the simulated participant's breaking point.

Milgram's Experiment 17 produced a **10% full-obedience rate (4 of 40 participants)**.

### Stress

Stress accumulates throughout the simulated experiment as a function of voltage intensity and learner reactions.

The current model includes reaction milestones such as:

* grunt at 75V;
* demand to be released at 150V;
* agonized scream at 270V;
* silence at 330V;
* subsequent reactions at higher voltage levels.

Stress progressively affects the participant's simulated breaking point.

These reactions are used as model inputs inspired by the experimental procedure; they should not be interpreted as a validated quantitative model of human stress.

## Four model conditions

| Condition           | Model manipulation                        | `learner_feedback` | Published rate |
| ------------------- | ------------------------------------------|---------------------|-------------:  |
| Baseline            | Experimenter present; learner not visible | `"none"`            |          65.0% |
| Experimenter absent | Instructions provided by telephone        | `"none"`            |          20.5% |
| Learner visible     | Learner and participant in same room      | `"voice"`           |          40.0% |
| Two peers rebel     | Two confederate peers refuse to continue  | `"voice"`           |          10.0% |

The four published rates are used as **aggregate calibration targets**.

They are not treated as direct estimates of individual psychological parameters.

## Calibration

Several model parameters were calibrated using a grid search against the four published obedience rates:

* `authority_scale`
* `confederate_scale`
* `visible_shift`
* `center_lo`
* `center_span`

The calibration was performed against aggregate obedience rates rather than individual-level psychological measurements. Calibration was re-run after introducing `learner_feedback` (see above), since switching the Baseline and Experimenter-absent conditions to `"none"` shifts their simulated obedience rates.

The current calibrated model was evaluated using:

* **4 conditions**
* **30 replications per condition**
* **60 simulated participants per replication**
* **1,800 simulated participants per condition**
* **7,200 simulated participants in total**

### Current results

| Condition           |    Simulated | Published |
| ------------------- | -----------: | --------: |
| Baseline            | 64.2% (±7.1) |     65.0% |
| Experimenter absent | 18.1% (±5.5) |     20.5% |
| Learner visible     | 38.1% (±6.4) |     40.0% |
| Two peers rebel     |  9.8% (±3.6) |     10.0% |

The values above are outputs of the current model calibration and should not be interpreted as estimates of real-world psychological effects.

The `±` values describe variation across simulation replications rather than uncertainty in the historical empirical results.

### Calibration limitations

The model contains multiple adjustable parameters but is calibrated against only four aggregate outcomes. Consequently:

* different parameter combinations may produce similar obedience rates;
* the calibrated values should not be interpreted as estimates of psychological parameters;
* matching published rates does not establish causal validity;
* the model may reproduce an observed pattern while representing the underlying process incorrectly.

This makes the calibration itself a useful object of study:

> **How many different models can reproduce the same empirical pattern?**

## What can this model teach?

The model can be used to explore several important ideas in computational and open science.

### 1. Reproducibility

The same model configuration and random seed produce the same simulation results.

### 2. Stochastic variation

Different random seeds produce different outcomes even when the experimental condition and model parameters remain unchanged.

### 3. Parameter sensitivity

Changing assumptions about authority, stress, peer influence, or proximity changes simulated behaviour.

### 4. Model calibration

Parameters can be selected so that simulated aggregate outcomes resemble empirical observations.

### 5. Simulation is not replication

A simulation can reproduce a numerical pattern without reproducing the original experiment or validating the explanation for that pattern.

### 6. Assumptions matter

Every computational model contains assumptions. The behaviour produced by an agent-based model depends on the rules and parameters encoded by the modeller.

## Teaching activity

The model can be used as an interactive teaching exercise in:

* research methods;
* psychology;
* computational social science;
* agent-based modelling;
* data science;
* scientific reproducibility;
* open science.

### Activity: Can we reproduce Milgram's findings?

**Step 1 - Run the baseline**

Run the default model and record the simulated obedience rate.

**Step 2 - Repeat the simulation**

Run multiple replications and examine the variation between runs.

**Step 3 - Change one assumption**

Change one parameter, such as authority pressure, while keeping the other parameters constant.

Ask:

> How does the simulated obedience rate change?

**Step 4 - Explore calibration**

Try different parameter combinations and investigate whether different models can produce similar aggregate results.

**Step 5 - Discuss the result**

Ask:

> If we find parameters that reproduce Milgram's published obedience rates, have we demonstrated that these parameters describe how real participants behaved?

The answer should be **no**.

This provides a practical way to discuss the distinction between:

```text
Empirical observation
        ↓
Computational model
        ↓
Model assumptions
        ↓
Simulation
        ↓
Reproduction of a pattern
```

and why reproducing a pattern does not necessarily validate the explanation behind it.

## Reproducibility

The project is designed so that simulation results can be reproduced from the source code and documented parameters.

* Random seeds are explicitly controlled.
* Mesa's internal random number generator is seeded.
* Participant-level random draws are seeded from the same source.
* Model parameters are documented in `parameter_guide.md`.
* Dependencies are specified in `requirements.txt`.
* Batch experiments are implemented in `run_experiment.py`.
* Participant-level simulation data can be exported as CSV.
* The Streamlit application uses the same calibrated defaults as the batch experiment.

Running the same model with the same seed reproduces the same simulation results.

> **Reproducibility does not imply validity.** A model can be perfectly reproducible while still being an imperfect representation of the phenomenon being studied.

## Interactive Streamlit application

The project includes an interactive web application.

Run locally with:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

The application allows users to configure:

* participants per replication;
* number of replications;
* random seed;
* experimental conditions;
* custom conditions;
* learner visibility;
* experimenter proximity;
* confederate participation;
* obedience-threshold ranges;
* stress, authority, and confederate sensitivity;
* experimenter base pressure;
* calibrated situational-effect parameters.

Results are recomputed when a simulation is run and include:

* obedience rate by condition;
* voltage drop-off curves;
* downloadable participant-level data;
* downloadable summary results.

## Project structure

| File                     | Purpose                                                                                         |
| ------------------------ | ----------------------------------------------------------------------------------------------- |
| `agents.py`              | `ParticipantAgent`, `ExperimenterAgent`, and `ConfederateAgent` classes and core decision logic |
| `model.py`               | `MilgramModel` - orchestrates individual simulation runs                                        |
| `run_experiment.py`      | Batch experiment: 4 conditions × 30 replications × 60 participants                              |
| `streamlit_app.py`       | Interactive web application                                                                     |
| `parameter_guide.md`     | Plain-language explanation of model parameters                                                  |
| `theme.py`               | Streamlit and Matplotlib visual styling                                                         |
| `.streamlit/config.toml` | Streamlit theme configuration                                                                   |
| `requirements.txt`       | Python dependencies                                                                             |
| `outputs/`               | Generated simulation results and charts                                                         |

## Outputs

Running:

```bash
python3 run_experiment.py
```

generates:

### `outputs/condition_summary.csv`

One row per condition containing the simulated mean and standard deviation and the corresponding published obedience rate.

### `outputs/participant_level_data.csv`

Participant-level simulation data.

The current batch configuration produces:

```text
4 conditions × 30 replications × 60 participants
= 7,200 simulated participants
```

The dataset contains variables including:

* participant obedience threshold;
* maximum shock administered;
* quit voltage;
* final stress level;
* experimental condition.

### `outputs/obedience_by_condition.png`

Comparison of simulated and published obedience rates.

### `outputs/dropout_curve.png`

A step-style curve showing the percentage of simulated participants still continuing at each of the 30 voltage levels.

## Running the batch experiment

Install the required packages:

```bash
pip install mesa pandas matplotlib
```

Then run:

```bash
python3 run_experiment.py
```

## Running a single condition

```python
from model import MilgramModel

model = MilgramModel(
    n_participants=40,
    proximity="present",
    learner_visible=False,
    use_confederates=False,
    seed=1
)

summary = model.run_full_experiment()

print(summary)
print(model.participant_dataframe().head())
```

Using the same seed reproduces the same random draws and simulation results.

## Limitations

This project should be interpreted as a **computational teaching and modelling resource**, not as a validated psychological model.

Important limitations include:

* The simulated participants are not representations of individual Milgram participants.
* The model does not estimate psychological parameters from individual-level experimental data.
* The behavioural mechanisms are assumptions introduced by the modeller.
* The model is calibrated against aggregate obedience rates.
* Multiple parameter combinations may reproduce similar aggregate outcomes.
* The current learner-reaction mechanism is a stylized representation rather than a complete reconstruction of the historical experimental procedure.
* The model does not capture the full historical, social, interpersonal, and ethical context of Milgram's experiments.
* A match between simulated and published obedience rates does not establish that the model explains why participants behaved as they did.
* The model should not be used to make predictions about the behaviour of real individuals.

## Historical and methodological note

Milgram's work has been extensively discussed and re-evaluated, including questions concerning methodology, interpretation, ethics, archival evidence, and the explanation of obedience.

Later archival work has also examined recordings and documentation from individual Milgram conditions. For example, the two-peer-rebellion condition is identified as **Experiment 17** in Milgram's 1974 book, while archival material has also used a separate condition label for the same experimental condition.

This project deliberately avoids treating the classic obedience percentages as a complete explanation of human obedience.

Instead, it uses the published experimental patterns as an opportunity to examine a more general computational question:

> **How can different assumptions about individuals and social situations generate similar observed outcomes?**

## Citation

If you use this software in research, teaching, presentations, or other work, please cite the version of the software that you used.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22724177.svg)](https://doi.org/10.5281/zenodo.22724177)

Skhirtladze, T. (2026). Milgram Obedience Experiment: An Agent-Based Model (Version v1.0.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.22724177

For software citation, the repository also includes a `CITATION.cff` file.

## License

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for the full text.

See the repository license for the exact terms.

## References

Milgram, S. (1963). Behavioral study of obedience. *The Journal of Abnormal and Social Psychology, 67*(4), 371–378. doi:10.1037/h0040525

Milgram, S. (1974). *Obedience to Authority: An Experimental View*. Harper & Row.

Haslam, N., Loughnan, S., & Perry, G. (2014). Meta-Milgram: An empirical synthesis of the obedience experiments. *PLoS ONE, 9*(4), e93927. doi:10.1371/journal.pone.0093927

Gibson, S. (2022). 'We have a choice': Identity construction and the rhetorical enactment of resistance in the 'two peers rebel' condition of Stanley Milgram's obedience experiment. *European Journal of Social Psychology*. doi:10.1002/ejsp.2734

## Author

**Tornike Skhirtladze**

Research Software Engineer / Data Engineer

Python · Agent-Based Modelling · Research Software · Reproducibility · Open Science