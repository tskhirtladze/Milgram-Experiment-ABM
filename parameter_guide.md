# Milgram ABM - Plain-Language Guide to Every Control

This walks through every slider and setting in the sidebar: what it does, why it has the range it has, and what changing it means for the simulation.

---

## Simulation setup

### Participants per replication (5 – 300, default 60)
How many pretend "participants" are simulated in **one run** of a condition. Each one is an independent little agent with its own personality (see "Obedience threshold range" below) who goes through the whole experiment on its own.
- **Low numbers (5–20):** fast, but noisy - results can swing a lot by chance, like flipping a coin only 10 times.
- **High numbers (100+):** smoother, more reliable percentages, but slower to run.
- The real Milgram study used 40 participants per condition, which is why that's a common number to test around.

### Replications per condition (1 – 100, default 30)
How many times the **whole batch** of participants is re-run from scratch, with a different random seed each time. This is not about single participants - it's about running the entire simulated experiment over and over to see how consistent the *average* result is.
- 1 replication = you only see one possible outcome, which might be lucky or unlucky.
- More replications = you get a mean and a spread (the error bars on the bar chart), so you can trust the number more.

### Base random seed
A starting number that controls the "random dice rolls" behind the simulation (which disposition each participant gets, etc.). The same seed always produces the same results - useful for reproducing a run exactly. Change it to explore a different set of random outcomes.

---

## Conditions to run

These checkboxes pick which experimental setups to simulate. Each mirrors a real variation Milgram ran:

- **Baseline (experimenter present):** the original setup - experimenter in the room, learner unseen, no vocal feedback from the learner. Published result: ~65% went all the way.
- **Experimenter absent (phone):** the experimenter gives orders by phone instead of standing in the room, no vocal feedback from the learner. Published result: ~20.5%. (Without someone watching, people find it much easier to stop.)
- **Learner visible (same room):** the person being "shocked" is in the same room, visible, instead of just heard through a wall, with vocal feedback (grunts, cries, demands to be released, etc.) active. Published result: ~40%. (Seeing someone's distress makes it harder to continue.)
- **Two peers rebel:** two other "teachers" (confederates) refuse to continue partway through, with vocal feedback active. Published result: ~10%. (Watching someone else say no makes it much easier to also say no.)

Two of these ingredients - vocal feedback and learner visibility - are set separately in the model, because Milgram's published obedience rates come from slightly different underlying procedures. The **Baseline** and **Experimenter absent** conditions correspond to Milgram's original "no vocal feedback" procedure; the **Learner visible** and **Two peers rebel** conditions are built on the "voice feedback" version (the version where you hear the learner grunt, cry out, and so on). This matters because a separate published condition with voice feedback but no other manipulation reports 62.5% obedience - noticeably lower than the 65% no-feedback baseline - showing the vocal-feedback mechanism itself has a real (if modest) effect on the simulated participants.

**➕ Add a custom condition** lets you mix and match these ingredients yourself (experimenter present/remote, learner visible or not, confederates present or not, learner feedback on or off) to test combinations Milgram never actually ran.

### Learner feedback (None / Voice)
Controls whether the scripted sequence of learner reactions (grunt at 75V, shout of pain at 120V, demands to be released at 150V, ... ominous silence at 330V) is active for this condition.
- **None:** the learner gives no scripted vocal reactions. Participants' stress only builds from the rising voltage itself, not from specific reaction milestones. Used for the two conditions calibrated against Milgram's no-feedback baseline.
- **Voice:** the full reaction sequence is active, adding extra stress at each milestone voltage on top of the general rise from increasing intensity. Used for the two conditions built on Milgram's voice-feedback procedure.

Switching a condition from "None" to "Voice" (or back) will change its simulated obedience rate somewhat, since the added stress from reaction milestones makes simulated participants a little more likely to refuse.

---

## Agent parameters

These control how each simulated participant "thinks."

### Obedience threshold range - disposition (0.00 – 1.00, default 0.10–0.90)
Every participant is given a random personal "compliance" score somewhere in this range: 0 means naturally defiant, 1 means naturally compliant. The range is capped at 0–1 because that's just how the scale is defined (0% to 100% compliant).
- A **narrow range** (e.g. 0.4–0.6) makes participants more similar to each other.
- A **wide range** (e.g. 0.0–1.0) creates more variety - some very stubborn people, some very compliant people, like real populations.

### Stress sensitivity (0.00 – 2.00, default 0.60)
How much a participant's *own building stress* (from hearing the learner suffer, going up in voltage, etc.) pushes them toward quitting. Higher = stress wears them down faster and they quit sooner. Set to 0, stress wouldn't matter to them at all. The upper limit (2.0) is just a practical ceiling - well past it, stress alone would overwhelm every other factor.

### Authority sensitivity (0.00 – 2.00, default 0.90)
How much the experimenter's pressure ("please continue," "you have no choice, you must go on") raises a participant's willingness to keep going. Higher = participants are more swayed by being told what to do by an authority figure. At 0, the experimenter's insistence would have no effect at all.

### Confederate defection sensitivity (0.00 – 1.00, default 0.35)
How much it affects a participant when a peer (confederate) refuses to continue. Higher = seeing someone else say "no" makes this participant much more likely to also stop. Capped at 1.0 because it's meant to represent a percentage-style influence, not a runaway multiplier.

### Experimenter base pressure (0.00 – 2.00, default 0.50)
How firmly the experimenter pushes back *before* factoring in the participant's own authority sensitivity above - think of it as "how insistent is this particular experimenter," independent of how each participant personally reacts to being pressured.

### Confederate defection voltages (15 – 450, default 150 & 210)
The two voltage levels at which the two peer confederates (in the "Two peers rebel" condition) each say "I won't continue." The range matches the actual voltage ladder used in the experiment (15V to 450V, the full range of shocks). Lowering these numbers means the peers rebel earlier (sooner pressure to stop); raising them means the peers hold out longer.

---

## ⚙️ Situational-effect magnitudes (calibrated defaults)

These are more technical "under the hood" numbers that control *how strongly* the situation shifts a participant's personal breaking point (the voltage at which they'd normally quit). You generally shouldn't need to touch these - they've already been tuned to reproduce Milgram's real percentages - but here's what they mean if you want to experiment:

### Authority scale (0 – 1200, default 710)
How big a push the experimenter's presence/pressure gives toward a *higher* breaking point (i.e., toward continuing longer). The app's own tooltip warns that values much above ~900 tend to force almost everyone to obey, regardless of anything else - so above that the authority effect basically overrides individual personality.

### Confederate scale (0 – 1200, default 940)
Same idea, but for the effect of a peer defecting - how big a push it gives toward a *lower* breaking point (quitting sooner) once a confederate refuses. Values much above ~1000 tend to force almost everyone to quit as soon as a peer does.

### Learner-visible shift (-500 – 0, default -140)
A flat shift *downward* applied to the breaking point when the learner is visible in the room. It's restricted to negative numbers (or zero) because seeing the learner's distress should only ever make people *more* likely to stop, never less.

### Disposition center (low) (-500 – 100, default -250)
Together with "Disposition center (span)" below, this defines the underlying range that each participant's personal breaking point is drawn from, *before* any situational shifts (authority, confederates, visibility) are applied. This is the "low end" of that starting range.

### Disposition center (span) (100 – 1000, default 800)
The *width* of that starting range of personal breaking points. A bigger span means more natural variation between participants before the situation starts pushing them around; a smaller span makes participants start out more alike.

### Transition steepness - k (0.02 – 0.3, default 0.09)
Participants don't switch from "obeying" to "refusing" like a light switch - it's a gradual probability curve around their personal breaking point. This controls how *sharp* that curve is.
- **Low k (close to 0.02):** a gentle, gradual transition - participants might waver for a wide range of voltages before fully quitting.
- **High k (close to 0.3):** a sharp, almost switch-like transition - participants obey right up until their breaking point, then quit almost immediately once past it.

---

*Tip: the "Situational-effect magnitudes" section is collapsed by default because the defaults were calibrated to match Milgram's real published percentages - the bar chart in the app compares your simulated results directly against those published numbers, so drastic changes here will pull the simulation away from that real-world comparison.*