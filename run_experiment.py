import os
import statistics as stats
import pandas as pd
import matplotlib.pyplot as plt

from model import MilgramModel, SHOCK_LEVELS

OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUT_DIR, exist_ok=True)


CONDITIONS = [
    ("Baseline (experimenter present)",
     dict(proximity="present", learner_visible=False, use_confederates=False,
          learner_feedback="none"), 65.0),
    ("Experimenter absent (phone)",
     dict(proximity="remote", learner_visible=False, use_confederates=False,
          learner_feedback="voice"), 20.5),
    ("Learner visible (same room)",
     dict(proximity="present", learner_visible=True, use_confederates=False,
          learner_feedback="voice"), 40.0),
    ("Two peers rebel",
     dict(proximity="present", learner_visible=False, use_confederates=True,
          learner_feedback="voice"), 10.0),
]

N_PARTICIPANTS = 60
N_REPLICATIONS = 30


def run_all():
    summary_rows = []
    participant_rows = []
    dropout_curves = {}  # label -> list of mean % still obeying at each voltage (averaged over reps)

    for label, kwargs, real_pct in CONDITIONS:
        rep_obedience_rates = []
        rep_dropout_matrices = []  # each: list of pct_still_obeying per voltage step

        for rep in range(N_REPLICATIONS):
            model = MilgramModel(n_participants=N_PARTICIPANTS, seed=1000 + rep, **kwargs)
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

        mean_obedience = stats.mean(rep_obedience_rates)
        sd_obedience = stats.pstdev(rep_obedience_rates)

        # average the dropout curve across replications, voltage by voltage
        avg_curve = [
            stats.mean(rep[i] for rep in rep_dropout_matrices)
            for i in range(len(SHOCK_LEVELS))
        ]
        dropout_curves[label] = avg_curve

        summary_rows.append(
            {
                "condition": label,
                "n_participants_per_rep": N_PARTICIPANTS,
                "n_replications": N_REPLICATIONS,
                "simulated_obedience_pct_mean": round(mean_obedience, 1),
                "simulated_obedience_pct_sd": round(sd_obedience, 1),
                "published_milgram_obedience_pct": real_pct,
            }
        )
        print(f"{label:30s} simulated={mean_obedience:5.1f}%  (Milgram reported: {real_pct}%)")

    summary_df = pd.DataFrame(summary_rows)
    participant_df = pd.concat(participant_rows, ignore_index=True)

    summary_df.to_csv(os.path.join(OUT_DIR, "condition_summary.csv"), index=False)
    participant_df.to_csv(os.path.join(OUT_DIR, "participant_level_data.csv"), index=False)

    make_bar_chart(summary_df)
    make_dropout_chart(dropout_curves)

    return summary_df, participant_df


def make_bar_chart(summary_df):
    fig, ax = plt.subplots(figsize=(8, 5))
    x = range(len(summary_df))
    width = 0.35

    ax.bar(
        [i - width / 2 for i in x],
        summary_df["simulated_obedience_pct_mean"],
        width,
        yerr=summary_df["simulated_obedience_pct_sd"],
        capsize=4,
        label="ABM simulation",
        color="#4C72B0",
    )
    ax.bar(
        [i + width / 2 for i in x],
        summary_df["published_milgram_obedience_pct"],
        width,
        label="Milgram's published results",
        color="#DD8452",
    )

    ax.set_xticks(list(x))
    ax.set_xticklabels(summary_df["condition"], rotation=20, ha="right")
    ax.set_ylabel("% of participants obedient to 450V")
    ax.set_title("Simulated vs. Published Obedience Rates by Condition")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "obedience_by_condition.png"), dpi=150)
    plt.close(fig)


def make_dropout_chart(dropout_curves):
    fig, ax = plt.subplots(figsize=(8, 5))
    for label, curve in dropout_curves.items():
        ax.plot(SHOCK_LEVELS, curve, marker="o", markersize=3, label=label)

    ax.set_xlabel("Shock level administered (Volts)")
    ax.set_ylabel("% of participants still obeying")
    ax.set_title("Simulated Obedience Drop-off Curve by Voltage")
    ax.axvline(330, color="gray", linestyle="--", linewidth=1, label="Learner falls silent (330V)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "dropout_curve.png"), dpi=150)
    plt.close(fig)

if __name__ == "__main__":
    run_all()
    print(f"\nDone. Outputs written to: {OUT_DIR}")