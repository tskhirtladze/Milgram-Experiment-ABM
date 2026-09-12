import mesa
import pandas as pd

from agents import ParticipantAgent, ExperimenterAgent, ConfederateAgent, SHOCK_LEVELS


class MilgramModel(mesa.Model):
    """
    Parameters
    ----------
    n_participants : int
        Number of independent simulated subjects in this run.
    proximity : {"present", "remote"}
        Whether the experimenter is physically present or gives orders by
        phone from another room (Milgram's "experimenter absent" variant).
    learner_visible : bool
        Whether the learner is in the same room, visible to the participant
        (Milgram's "proximity" variant), instead of the standard condition
        where the learner is heard through a wall but not seen.
    experimenter_base_pressure : float
        Baseline authority pressure exerted by the experimenter.
    use_confederates : bool
        Whether two peer confederates are present (Milgram condition 17).
    confederate_defect_voltages : tuple(int, int)
        Voltages at which the two confederates refuse, if active.
    authority_scale, confederate_scale, visible_shift : float
        Calibrated magnitudes for how strongly each situational factor
        shifts a participant's personal breaking point (see agents.py).
    center_lo, center_span : float
        Range of the personal-disposition "breaking point" before
        situational factors act on it (higher span = more individual
        variation between participants).
    obedience_threshold_range : tuple(float, float)
        Range from which each participant's raw disposition
        (0=defiant, 1=compliant) is drawn uniformly at random.
    stress_weight, authority_weight, confederate_penalty : float
        Per-agent sensitivity to stress, authority pressure, and peer
        dissent respectively (see ParticipantAgent).
    k : float
        Steepness of the logistic obey/refuse transition around each
        participant's personal breaking point.
    seed : int, optional
        RNG seed for reproducibility.
    """

    def __init__(
        self,
        n_participants=40,
        proximity="present",
        learner_visible=False,
        experimenter_base_pressure=0.5,
        use_confederates=False,
        confederate_defect_voltages=(150, 210),
        authority_scale=710,
        confederate_scale=940,
        visible_shift=-140,
        center_lo=-250,
        center_span=800,
        obedience_threshold_range=(0.1, 0.9),
        stress_weight=0.6,
        authority_weight=0.9,
        confederate_penalty=0.35,
        k=0.09,
        learner_feedback="voice",
        seed=None,
    ):

        super().__init__(rng=seed)

        if learner_feedback not in ("none", "voice"):
            raise ValueError("learner_feedback must be 'none' or 'voice'")
        self.learner_feedback = learner_feedback

        self.proximity = proximity
        self.learner_visible = learner_visible
        self.use_confederates = use_confederates
        self.authority_scale = authority_scale
        self.confederate_scale = confederate_scale
        self.visible_shift = visible_shift
        self.center_lo = center_lo
        self.center_span = center_span
        self.k = k
        self.current_voltage = SHOCK_LEVELS[0]
        self._voltage_index = 0

        # Single shared experimenter for this run
        self.experimenter = ExperimenterAgent(
            self, proximity=proximity, base_pressure=experimenter_base_pressure
        )

        # Two confederate co-teachers (only "active" if this condition uses them)
        v1, v2 = confederate_defect_voltages
        self.confederates = [
            ConfederateAgent(self, defect_voltage=v1, active=use_confederates),
            ConfederateAgent(self, defect_voltage=v2, active=use_confederates),
        ]

        # N independent participants
        lo, hi = obedience_threshold_range
        self.participants = [
            ParticipantAgent(
                self,
                obedience_threshold=self.random.uniform(lo, hi),
                stress_weight=stress_weight,
                authority_weight=authority_weight,
                confederate_penalty=confederate_penalty,
                learner_feedback=self.learner_feedback,
            )
            for _ in range(n_participants)
        ]

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "voltage": lambda m: m.current_voltage,
                "pct_still_obeying": lambda m: m._pct_still_obeying(),
                "mean_stress": lambda m: m._mean_stress(),
            },
        )

        self.running = True

    def _pct_still_obeying(self):
        if not self.participants:
            return 0.0
        still_going = sum(1 for p in self.participants if not p.has_quit)
        return 100.0 * still_going / len(self.participants)

    def _mean_stress(self):
        if not self.participants:
            return 0.0
        return sum(p.stress_level for p in self.participants) / len(self.participants)

    def step(self):
        """Advance the experiment by one shock-level tick."""
        if self._voltage_index >= len(SHOCK_LEVELS):
            self.running = False
            return

        self.current_voltage = SHOCK_LEVELS[self._voltage_index]

        # Confederates act (may defect) before participants decide
        for c in self.confederates:
            c.step()

        # All participants decide independently at this voltage
        for p in self.participants:
            p.step()

        self.datacollector.collect(self)

        self._voltage_index += 1
        if self._voltage_index >= len(SHOCK_LEVELS):
            self.running = False

    def run_full_experiment(self):
        """Run all 30 shock levels to completion and return summary stats."""
        while self.running:
            self.step()
        return self.summary()

    def summary(self):
        max_v = max(SHOCK_LEVELS)
        obeyed_fully = sum(1 for p in self.participants if p.max_shock_given >= max_v)
        n = len(self.participants)
        return {
            "n_participants": n,
            "proximity": self.proximity,
            "learner_visible": self.learner_visible,
            "use_confederates": self.use_confederates,
            "obedience_rate_pct": 100.0 * obeyed_fully / n if n else 0.0,
            "mean_max_shock": sum(p.max_shock_given for p in self.participants) / n if n else 0.0,
            "mean_quit_voltage": (
                sum(p.quit_voltage for p in self.participants if p.quit_voltage is not None)
                / max(1, sum(1 for p in self.participants if p.quit_voltage is not None))
            ),
        }

    def participant_dataframe(self):
        """Per-agent outcomes for this run."""
        rows = []
        for p in self.participants:
            rows.append(
                {
                    "obedience_threshold": round(p.obedience_threshold, 3),
                    "max_shock_given": p.max_shock_given,
                    "quit_voltage": p.quit_voltage,
                    "fully_obedient": p.max_shock_given >= max(SHOCK_LEVELS),
                    "final_stress": round(p.stress_level, 3),
                }
            )
        return pd.DataFrame(rows)