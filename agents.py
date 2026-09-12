import math
import random
import mesa

# Shock levels used in the real generator: 15V increments, 15V to 450V (30 switches)
SHOCK_LEVELS = list(range(15, 465, 15))

# Voltage thresholds at which the (scripted) learner reacts -- based on the
# real experimental script, compressed to the key turning points. This is the
# "voice feedback" reaction set. The "no feedback" set is empty, representing
# Milgram's remote/no-vocal-feedback baseline condition (see README).

NO_FEEDBACK_REACTIONS = {}

VOICE_FEEDBACK_REACTIONS = {
    75: "grunt",
    120: "shout of pain",
    150: "demands to be released",
    180: "cries he can't stand the pain",
    270: "agonized scream",
    300: "refuses to answer",
    315: "violent scream",
    330: "ominous silence",
}

# The four standard experimenter "prods" (paraphrased), used in order.
PRODS = [
    "Please continue.",
    "The experiment requires that you continue.",
    "It is absolutely essential that you continue.",
    "You have no other choice, you must go on.",
]

MAX_PRODS = len(PRODS)


class ExperimenterAgent(mesa.Agent):
    """The authority figure. Doesn't make decisions itself in this model;
    it exposes a `pressure` value that scales with proximity condition and
    is consulted by ParticipantAgent when it hesitates."""

    def __init__(self, model, proximity="present", base_pressure=0.5):
        super().__init__(model)
        # proximity in {"present", "remote"} -- mirrors Milgram's variant
        # where the experimenter gave orders by telephone from another room
        # instead of standing in the room with the participant.
        self.proximity = proximity
        self.base_pressure = base_pressure

    @property
    def proximity_multiplier(self):
        return {
            "present": 1.00,  # baseline: experimenter physically in the room
            "remote": 0.08,   # experimenter absent, instructions given by phone
        }.get(self.proximity, 1.0)

    def step(self):
        # Experimenter is passive; pressure is read by participants on demand.
        pass


class ConfederateAgent(mesa.Agent):
    """A planted co-teacher who may defy the experimenter at a scripted
    voltage, per Milgram's peer-rebellion variant (condition 17)."""

    def __init__(self, model, defect_voltage=150, active=False):
        super().__init__(model)
        self.defect_voltage = defect_voltage
        self.active = active          # whether this confederate is present in this run
        self.has_defected = False

    def step(self):
        if not self.active:
            return
        if self.model.current_voltage >= self.defect_voltage:
            self.has_defected = True


def _safe_sigmoid(x):
    """Numerically stable logistic function. Avoids OverflowError from
    math.exp() on very large magnitude inputs, which can otherwise occur
    with extreme parameter combinations (e.g. large confederate_scale
    together with a steep k)."""
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    else:
        z = math.exp(x)
        return z / (1.0 + z)


class ParticipantAgent(mesa.Agent):
    """The real subject of the experiment ("teacher"). Decides, at each
    shock level, whether to continue administering shocks or refuse."""

    def __init__(
        self,
        model,
        obedience_threshold=None,
        stress_weight=0.6,
        authority_weight=0.9,
        confederate_penalty=0.35,
        learner_feedback="voice",
    ):
        super().__init__(model)
        # Baseline personal disposition toward obeying authority (0=defiant, 1=compliant)
        self.obedience_threshold = (
            obedience_threshold
            if obedience_threshold is not None
            else self.random.uniform(0.1, 0.9)
        )
        self.stress_weight = stress_weight
        self.authority_weight = authority_weight
        self.confederate_penalty = confederate_penalty

        if learner_feedback not in ("none", "voice"):
            raise ValueError("learner_feedback must be 'none' or 'voice'")
        self.learner_feedback = learner_feedback

        self.stress_level = 0.0
        self.prods_used = 0
        self.has_quit = False
        self.max_shock_given = 0
        self.quit_voltage = None

    @property
    def learner_reactions(self):
        """The active reaction schedule, based on this participant's
        learner_feedback condition ('none' -> no vocal reactions at all,
        'voice' -> the full scripted reaction sequence)."""
        return VOICE_FEEDBACK_REACTIONS if self.learner_feedback == "voice" else NO_FEEDBACK_REACTIONS

    def _compliance_probability(self, voltage, experimenter, confederate_defected):
        """
        Core decision function. Rather than an independent coin-flip at every
        one of the 30 switches (which compounds into unrealistic early
        attrition), each participant has a personal "breaking point" on the
        voltage scale, softened into a logistic curve so the transition from
        obeying to refusing is gradual and noisy rather than a hard cutoff.

        Returns P(continue) at this voltage.

        Constants below were calibrated (via grid search against Milgram's
        published obedience rates for each condition) so that, in aggregate
        across many simulated participants, the model reproduces roughly:
            baseline (voice feedback, experimenter present) ~ 65%
            experimenter absent / phone instructions          ~ 20.5%
            learner visible in same room                      ~ 40%
            two peer confederates refuse                       ~ 10%
        See run_experiment.py for the validation against these targets.
        """
        max_v = max(SHOCK_LEVELS)

        # Stress rises with voltage and spikes at learner-reaction milestones
        intensity = voltage / max_v
        reaction_bump = 0.12 if voltage in self.learner_reactions else 0.0
        self.stress_level = min(1.0, self.stress_level + intensity / 45 + reaction_bump)

        # Personal breaking point: disposition maps onto where on the voltage
        # scale this person tends to balk, before situational factors act on it.
        base_center = self.model.center_lo + self.model.center_span * self.obedience_threshold

        # Learner visibility (same-room condition) makes the act more
        # immediate and harder to continue, independent of the experimenter.
        if self.model.learner_visible:
            base_center += self.model.visible_shift

        # Authority pressure raises the breaking point (harder to refuse);
        # scales with the experimenter's presence/proximity and with prods
        # already issued in this sequence of hesitation.
        pressure = experimenter.base_pressure * experimenter.proximity_multiplier
        pressure += 0.15 * self.prods_used
        authority_shift = self.authority_weight * pressure * self.model.authority_scale

        # Peer dissent sharply lowers the breaking point
        confederate_shift = (
            -self.confederate_penalty * self.model.confederate_scale
            if confederate_defected
            else 0.0
        )

        # Accumulated stress erodes willingness a bit further as the trial wears on
        stress_shift = -self.stress_weight * self.stress_level * 55

        center = base_center + authority_shift + confederate_shift + stress_shift

        # Logistic curve: steep enough to make the transition feel like a
        # "breaking point" rather than a smooth ramp, gentle enough to allow
        # some randomness/noise around that point.
        k = self.model.k
        p_continue = _safe_sigmoid(k * (center - voltage))
        return max(0.0, min(1.0, p_continue))

    def step(self):
        if self.has_quit or self.model.current_voltage is None:
            return

        experimenter = self.model.experimenter
        confederate_defected = any(
            c.has_defected for c in self.model.confederates if c.active
        )
        voltage = self.model.current_voltage

        p_continue = self._compliance_probability(voltage, experimenter, confederate_defected)

        if self.model.random.random() < p_continue:
            # Complies: administers this shock
            self.max_shock_given = voltage
            self.prods_used = 0  # reset prod counter after successful compliance
        else:
            # Hesitates -- experimenter issues a prod, up to MAX_PRODS times
            if self.prods_used < MAX_PRODS:
                self.prods_used += 1
                # Re-roll once with the added pressure from this prod
                p_retry = self._compliance_probability(voltage, experimenter, confederate_defected)
                if self.model.random.random() < p_retry:
                    self.max_shock_given = voltage
                    self.prods_used = 0
                else:
                    self.has_quit = True
                    self.quit_voltage = voltage
            else:
                self.has_quit = True
                self.quit_voltage = voltage