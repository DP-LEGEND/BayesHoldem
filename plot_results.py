import csv
import os
import matplotlib.pyplot as plt


# ============================================================
# LOAD RESULTS
# ============================================================

os.makedirs("figures", exist_ok=True)

rows = []

with open(
    "results/final_misspecification_results.csv",
    "r"
) as file:

    reader = csv.DictReader(file)

    for row in reader:
        rows.append({
            "state": row["state"],
            "alpha": float(row["alpha"]),
            "likelihood_rmse": float(row["likelihood_rmse"]),
            "naive_mean_regret": float(row["naive_mean_regret"]),
            "agent_mean_regret": float(row["agent_mean_regret"]),
            "naive_error_rate": float(row["naive_error_rate"]),
            "agent_error_rate": float(row["agent_error_rate"])
        })


# ============================================================
# AGGREGATE ACROSS STATES
# ============================================================

alphas = sorted(set(row["alpha"] for row in rows))

aggregate = {}

for alpha in alphas:

    alpha_rows = [
        row for row in rows
        if row["alpha"] == alpha
    ]

    aggregate[alpha] = {
        "rmse": sum(
            row["likelihood_rmse"]
            for row in alpha_rows
        ) / len(alpha_rows),

        "agent_regret": sum(
            row["agent_mean_regret"]
            for row in alpha_rows
        ) / len(alpha_rows),

        "naive_regret": sum(
            row["naive_mean_regret"]
            for row in alpha_rows
        ) / len(alpha_rows),

        "agent_error": sum(
            row["agent_error_rate"]
            for row in alpha_rows
        ) / len(alpha_rows),

        "naive_error": sum(
            row["naive_error_rate"]
            for row in alpha_rows
        ) / len(alpha_rows)
    }


x = [
    aggregate[alpha]["rmse"]
    for alpha in alphas
]


# ============================================================
# FIGURE 1 — MODEL ERROR VS DECISION REGRET
# ============================================================

agent_regret = [
    aggregate[alpha]["agent_regret"]
    for alpha in alphas
]

naive_regret = [
    aggregate[alpha]["naive_regret"]
    for alpha in alphas
]

plt.figure(figsize=(8, 5))

plt.plot(
    x,
    agent_regret,
    marker="o",
    label="Bayesian agent"
)

plt.plot(
    x,
    naive_regret,
    linestyle="--",
    label="Naive baseline"
)

plt.xlabel("Likelihood-model RMSE")
plt.ylabel("Mean decision regret")

plt.title(
    "Decision Regret Under Opponent-Model Misspecification"
)

plt.legend()
plt.grid(alpha=0.25)
plt.tight_layout()

plt.savefig(
    "figures/regret_vs_model_error.png",
    dpi=300
)

plt.close()


# ============================================================
# FIGURE 2 — MODEL ERROR VS DECISION ERROR RATE
# ============================================================

agent_error = [
    aggregate[alpha]["agent_error"] * 100
    for alpha in alphas
]

naive_error = [
    aggregate[alpha]["naive_error"] * 100
    for alpha in alphas
]

plt.figure(figsize=(8, 5))

plt.plot(
    x,
    agent_error,
    marker="o",
    label="Bayesian agent"
)

plt.plot(
    x,
    naive_error,
    linestyle="--",
    label="Naive baseline"
)

plt.xlabel("Likelihood-model RMSE")
plt.ylabel("Incorrect decisions (%)")

plt.title(
    "Decision Error Under Opponent-Model Misspecification"
)

plt.legend()
plt.grid(alpha=0.25)
plt.tight_layout()

plt.savefig(
    "figures/error_rate_vs_model_error.png",
    dpi=300
)

plt.close()


# ============================================================
# FIGURE 3 — STATE SENSITIVITY
# ============================================================

states = sorted(
    set(row["state"] for row in rows)
)

plt.figure(figsize=(9, 6))

for state in states:

    state_rows = [
        row for row in rows
        if row["state"] == state
    ]

    state_rows.sort(
        key=lambda row: row["alpha"]
    )

    state_x = [
        row["likelihood_rmse"]
        for row in state_rows
    ]

    state_regret = [
        row["agent_mean_regret"]
        for row in state_rows
    ]

    plt.plot(
        state_x,
        state_regret,
        marker="o",
        markersize=3,
        label=state
    )

plt.xlabel("Likelihood-model RMSE")
plt.ylabel("Mean decision regret")

plt.title(
    "State-Level Sensitivity to Model Misspecification"
)

plt.legend(
    fontsize=8,
    ncol=2
)

plt.grid(alpha=0.25)
plt.tight_layout()

plt.savefig(
    "figures/state_sensitivity.png",
    dpi=300
)

plt.close()


print("Figures generated successfully.")