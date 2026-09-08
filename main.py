import csv
import random

from experiments import (
    true_likelihoods,
    run_state_sweep
)


FINAL_TEST_STATES = [
    {
        "name": "equity_band_1",
        "user_cards": [
            {"rank": "5", "suit": "spades"},
            {"rank": "3", "suit": "clubs"}
        ],
        "community_cards": [
            {"rank": "10", "suit": "hearts"},
            {"rank": "7", "suit": "hearts"},
            {"rank": "A", "suit": "spades"}
        ],
        "screening_equity": 0.124,
        "exact_bet_equity": 0.13294527363184072
    },

    {
        "name": "equity_band_2",
        "user_cards": [
            {"rank": "8", "suit": "diamonds"},
            {"rank": "4", "suit": "diamonds"}
        ],
        "community_cards": [
            {"rank": "Q", "suit": "diamonds"},
            {"rank": "K", "suit": "spades"},
            {"rank": "10", "suit": "spades"}
        ],
        "screening_equity": 0.177,
        "exact_bet_equity": 0.19058852373765678
    },

    {
        "name": "equity_band_3",
        "user_cards": [
            {"rank": "J", "suit": "spades"},
            {"rank": "8", "suit": "clubs"}
        ],
        "community_cards": [
            {"rank": "K", "suit": "diamonds"},
            {"rank": "2", "suit": "diamonds"},
            {"rank": "7", "suit": "diamonds"}
        ],
        "screening_equity": 0.2165,
        "exact_bet_equity": 0.22304456571168904
    },

    {
        "name": "equity_band_4",
        "user_cards": [
            {"rank": "J", "suit": "spades"},
            {"rank": "8", "suit": "diamonds"}
        ],
        "community_cards": [
            {"rank": "3", "suit": "diamonds"},
            {"rank": "7", "suit": "diamonds"},
            {"rank": "2", "suit": "clubs"}
        ],
        "screening_equity": 0.29783333333333334,
        "exact_bet_equity": 0.30185142469470555
    },

    {
        "name": "equity_band_5",
        "user_cards": [
            {"rank": "J", "suit": "clubs"},
            {"rank": "2", "suit": "spades"}
        ],
        "community_cards": [
            {"rank": "8", "suit": "diamonds"},
            {"rank": "10", "suit": "clubs"},
            {"rank": "10", "suit": "diamonds"}
        ],
        "screening_equity": 0.3095,
        "exact_bet_equity": 0.3066176322108518
    },

    {
        "name": "equity_band_6",
        "user_cards": [
            {"rank": "A", "suit": "spades"},
            {"rank": "2", "suit": "diamonds"}
        ],
        "community_cards": [
            {"rank": "5", "suit": "diamonds"},
            {"rank": "J", "suit": "clubs"},
            {"rank": "K", "suit": "hearts"}
        ],
        "screening_equity": 0.3423333333333333,
        "exact_bet_equity": 0.3438295642997151
    },

    {
        "name": "equity_band_7",
        "user_cards": [
            {"rank": "Q", "suit": "diamonds"},
            {"rank": "6", "suit": "diamonds"}
        ],
        "community_cards": [
            {"rank": "2", "suit": "spades"},
            {"rank": "3", "suit": "hearts"},
            {"rank": "3", "suit": "spades"}
        ],
        "screening_equity": 0.366,
        "exact_bet_equity": 0.3622424154627566
    },

    {
        "name": "equity_band_8",
        "user_cards": [
            {"rank": "A", "suit": "clubs"},
            {"rank": "7", "suit": "hearts"}
        ],
        "community_cards": [
            {"rank": "4", "suit": "hearts"},
            {"rank": "2", "suit": "clubs"},
            {"rank": "8", "suit": "clubs"}
        ],
        "screening_equity": 0.40166666666666667,
        "exact_bet_equity": 0.3983991406603344
    },

    {
        "name": "equity_band_9",
        "user_cards": [
            {"rank": "3", "suit": "diamonds"},
            {"rank": "Q", "suit": "clubs"}
        ],
        "community_cards": [
            {"rank": "4", "suit": "hearts"},
            {"rank": "2", "suit": "hearts"},
            {"rank": "5", "suit": "clubs"}
        ],
        "screening_equity": 0.42816666666666664,
        "exact_bet_equity": 0.4132328113425342
    },

    {
        "name": "equity_band_10",
        "user_cards": [
            {"rank": "7", "suit": "clubs"},
            {"rank": "3", "suit": "hearts"}
        ],
        "community_cards": [
            {"rank": "A", "suit": "diamonds"},
            {"rank": "3", "suit": "diamonds"},
            {"rank": "9", "suit": "hearts"}
        ],
        "screening_equity": 0.44383333333333336,
        "exact_bet_equity": 0.4320806490097833
    }
]


# ============================================================
# FINAL MISSPECIFICATION EXPERIMENT
# ============================================================

# Makes the experiment reproducible
random.seed(42)

alphas = [
    0.0,
    0.1,
    0.2,
    0.3,
    0.4,
    0.5,
    0.6,
    0.7,
    0.8,
    0.9,
    1.0
]

all_results = []

for state in FINAL_TEST_STATES:
    print("\nRunning state:", state["name"])

    state_results = run_state_sweep(
        state,
        true_likelihoods,
        alphas,
        equity_simulations=50000,
        num_trials=100000
    )

    all_results.extend(state_results)

    print("Finished:", state["name"])


# ============================================================
# SAVE RESULTS
# ============================================================

with open(
    "results/final_misspecification_results.csv",
    "w",
    newline=""
) as file:

    fieldnames = all_results[0].keys()

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(all_results)


print("\n===== EXPERIMENT COMPLETE =====")
print("States:", len(FINAL_TEST_STATES))
print("Alpha levels:", len(alphas))
print("Decision trials per alpha:", 100000)
print(
    "Total decision evaluations:",
    len(FINAL_TEST_STATES) * len(alphas) * 100000
)

print(
    "\nResults saved to:",
    "results/final_misspecification_results.csv"
)