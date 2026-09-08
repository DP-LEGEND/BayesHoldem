import random
import math
from cards import create_deck
from opponent_model import classify_hand_strength, calculate_strength_priors, bayesian_update, group_opponent_hands
from equity import monte_carlo_equity, bayesian_equity, exact_bayesian_flop_equity
from decision import call_decision

true_likelihoods = {
    "WEAK": 0.20,
    "MEDIUM": 0.45,
    "STRONG": 0.70,
    "VERY STRONG": 0.90
}

test_states = [
    {
        "name": "AK_high_dry",
        "user_cards": [
            {"rank": "A", "suit": "spades"},
            {"rank": "K", "suit": "spades"}
        ],
        "community_cards": [
            {"rank": "Q", "suit": "hearts"},
            {"rank": "7", "suit": "diamonds"},
            {"rank": "2", "suit": "clubs"}
        ]
    },

    {
        "name": "top_pair",
        "user_cards": [
            {"rank": "A", "suit": "spades"},
            {"rank": "Q", "suit": "clubs"}
        ],
        "community_cards": [
            {"rank": "Q", "suit": "hearts"},
            {"rank": "8", "suit": "diamonds"},
            {"rank": "3", "suit": "clubs"}
        ]
    },

    {
        "name": "overpair",
        "user_cards": [
            {"rank": "K", "suit": "spades"},
            {"rank": "K", "suit": "diamonds"}
        ],
        "community_cards": [
            {"rank": "J", "suit": "hearts"},
            {"rank": "7", "suit": "clubs"},
            {"rank": "2", "suit": "diamonds"}
        ]
    },

    {
        "name": "middle_pair",
        "user_cards": [
            {"rank": "9", "suit": "spades"},
            {"rank": "8", "suit": "spades"}
        ],
        "community_cards": [
            {"rank": "K", "suit": "hearts"},
            {"rank": "9", "suit": "diamonds"},
            {"rank": "3", "suit": "clubs"}
        ]
    },

    {
        "name": "flush_draw",
        "user_cards": [
            {"rank": "A", "suit": "spades"},
            {"rank": "J", "suit": "spades"}
        ],
        "community_cards": [
            {"rank": "8", "suit": "spades"},
            {"rank": "4", "suit": "spades"},
            {"rank": "K", "suit": "diamonds"}
        ]
    },

    {
        "name": "open_ended_draw",
        "user_cards": [
            {"rank": "9", "suit": "clubs"},
            {"rank": "8", "suit": "diamonds"}
        ],
        "community_cards": [
            {"rank": "7", "suit": "hearts"},
            {"rank": "6", "suit": "clubs"},
            {"rank": "K", "suit": "spades"}
        ]
    },

    {
        "name": "two_pair",
        "user_cards": [
            {"rank": "Q", "suit": "spades"},
            {"rank": "7", "suit": "clubs"}
        ],
        "community_cards": [
            {"rank": "Q", "suit": "hearts"},
            {"rank": "7", "suit": "diamonds"},
            {"rank": "2", "suit": "clubs"}
        ]
    },

    {
        "name": "set",
        "user_cards": [
            {"rank": "7", "suit": "spades"},
            {"rank": "7", "suit": "clubs"}
        ],
        "community_cards": [
            {"rank": "7", "suit": "hearts"},
            {"rank": "K", "suit": "diamonds"},
            {"rank": "2", "suit": "clubs"}
        ]
    },

    {
        "name": "paired_board",
        "user_cards": [
            {"rank": "A", "suit": "diamonds"},
            {"rank": "J", "suit": "clubs"}
        ],
        "community_cards": [
            {"rank": "8", "suit": "spades"},
            {"rank": "8", "suit": "hearts"},
            {"rank": "3", "suit": "diamonds"}
        ]
    },

    {
        "name": "low_connected_board",
        "user_cards": [
            {"rank": "A", "suit": "clubs"},
            {"rank": "K", "suit": "diamonds"}
        ],
        "community_cards": [
            {"rank": "6", "suit": "spades"},
            {"rank": "5", "suit": "hearts"},
            {"rank": "4", "suit": "clubs"}
        ]
    }
]



def calculate_regret(agent_decision, true_call_ev):
    # Best possible EV between CALL and FOLD
    optimal_ev = max(0, true_call_ev)

    # EV of the action the agent actually chose
    if agent_decision == "CALL":
        chosen_ev = true_call_ev
    else:
        chosen_ev = 0

    # Value lost by not choosing the optimal action
    regret = optimal_ev - chosen_ev

    return regret



def decision_margin(
    true_equity,
    pot,
    opponent_bet
):
    required_equity = (
        opponent_bet /
        (pot + 2 * opponent_bet)
    )

    return abs(
        true_equity - required_equity
    )



def generate_misspecified_likelihoods(true_likelihoods, alpha):
    misspecified_likelihoods = {}

    for strength, true_probability in true_likelihoods.items():
        inverted_probability = 1 - true_probability

        misspecified_likelihoods[strength] = (
            (1 - alpha) * true_probability
            + alpha * inverted_probability
        )

    return misspecified_likelihoods



def likelihood_rmse(true_likelihoods, model_likelihoods):
    sum_squared_errors = 0
    number_of_strengths = len(true_likelihoods)

    for strength in true_likelihoods:
        error = (
            model_likelihoods[strength]
            - true_likelihoods[strength]
        )

        sum_squared_errors += error ** 2

    rmse = math.sqrt(
        sum_squared_errors / number_of_strengths
    )

    return rmse



def generate_scenarios(
    num_trials,
    pot=100,
    min_bet=10,
    max_bet=400
):
    scenarios = []

    for _ in range(num_trials):
        opponent_bet = random.randint(
            min_bet,
            max_bet
        )

        scenarios.append({
            "opponent_bet": opponent_bet,
            "pot": pot
        })

    return scenarios




# ============================================================
# FIND DECISION-RELEVANT FLOP STATES
# ============================================================

TARGET_BANDS = [
    (0.10, 0.15),
    (0.15, 0.20),
    (0.20, 0.25),
    (0.25, 0.30),
    (0.30, 0.33),
    (0.33, 0.36),
    (0.36, 0.39),
    (0.39, 0.41),
    (0.41, 0.43),
    (0.43, 0.445)
]


def generate_random_flop_state():
    deck = create_deck()

    cards = random.sample(deck, 5)

    return {
        "user_cards": cards[:2],
        "community_cards": cards[2:]
    }


def estimate_true_bet_equity(
    user_cards,
    community_cards,
    true_likelihoods,
    simulations
):
    priors = calculate_strength_priors(
        user_cards,
        community_cards
    )

    hand_groups = group_opponent_hands(
        user_cards,
        community_cards
    )

    true_bet_posterior = bayesian_update(
        priors,
        true_likelihoods,
        "BET"
    )

    result = bayesian_equity(
        user_cards,
        community_cards,
        hand_groups,
        true_bet_posterior,
        simulations
    )

    return result["equity"]


def find_informative_states(
    true_likelihoods,
    target_bands=TARGET_BANDS,
    screening_simulations=3000,
    max_attempts=1000
):
    selected_states = [None] * len(target_bands)

    attempts = 0

    while (
        any(state is None for state in selected_states)
        and attempts < max_attempts
    ):
        attempts += 1

        state = generate_random_flop_state()

        estimated_equity = estimate_true_bet_equity(
            state["user_cards"],
            state["community_cards"],
            true_likelihoods,
            screening_simulations
        )

        for i, (lower, upper) in enumerate(target_bands):

            if (
                selected_states[i] is None
                and lower <= estimated_equity < upper
            ):
                state["name"] = f"equity_band_{i + 1}"
                state["screening_equity"] = estimated_equity

                selected_states[i] = state

                print(
                    "Found",
                    state["name"],
                    "| equity:",
                    round(estimated_equity, 4),
                    "| attempts:",
                    attempts
                )

                break

    selected_states = [
        state
        for state in selected_states
        if state is not None
    ]

    print(
        "\nFound",
        len(selected_states),
        "of",
        len(target_bands),
        "target states in",
        attempts,
        "attempts"
    )

    return selected_states



def precompute_ground_truth(
    user_cards,
    community_cards,
    true_likelihoods,
    simulations
):
    priors = calculate_strength_priors(
        user_cards,
        community_cards
    )

    hand_groups = group_opponent_hands(
        user_cards,
        community_cards
    )

    naive_equity = monte_carlo_equity(
        user_cards,
        community_cards,
        simulations
    )["equity"]

    true_bet_posterior = bayesian_update(
        priors,
        true_likelihoods,
        "BET"
    )

    true_bet_equity = exact_bayesian_flop_equity(
        user_cards,
        community_cards,
        hand_groups,
        true_bet_posterior
    )

    return {
        "priors": priors,
        "hand_groups": hand_groups,
        "naive_equity": naive_equity,
        "true_bet_equity": true_bet_equity
    }


def precompute_agent_equity(
    user_cards,
    community_cards,
    ground_truth,
    agent_likelihoods,
    simulations
):
    agent_bet_posterior = bayesian_update(
        ground_truth["priors"],
        agent_likelihoods,
        "BET"
    )

    agent_bet_equity = bayesian_equity(
        user_cards,
        community_cards,
        ground_truth["hand_groups"],
        agent_bet_posterior,
        simulations
    )["equity"]

    return {
        "naive_equity": ground_truth["naive_equity"],
        "agent_bet_equity": agent_bet_equity,
        "true_bet_equity": ground_truth["true_bet_equity"]
    }



def run_experiment(
    scenarios,
    precomputed
):
    total_naive_regret = 0
    total_agent_regret = 0

    naive_wrong_decisions = 0
    agent_wrong_decisions = 0

    for scenario in scenarios:
        pot = scenario["pot"]
        opponent_bet = scenario["opponent_bet"]

        naive_equity = precomputed["naive_equity"]
        agent_equity = precomputed["agent_bet_equity"]
        true_equity = precomputed["true_bet_equity"]

        naive_result = call_decision(
            naive_equity,
            pot,
            opponent_bet
        )

        agent_result = call_decision(
            agent_equity,
            pot,
            opponent_bet
        )

        true_result = call_decision(
            true_equity,
            pot,
            opponent_bet
        )

        true_call_ev = true_result["call_ev"]

        naive_regret = calculate_regret(
            naive_result["decision"],
            true_call_ev
        )

        agent_regret = calculate_regret(
            agent_result["decision"],
            true_call_ev
        )

        total_naive_regret += naive_regret
        total_agent_regret += agent_regret

        if naive_result["decision"] != true_result["decision"]:
            naive_wrong_decisions += 1

        if agent_result["decision"] != true_result["decision"]:
            agent_wrong_decisions += 1

    num_trials = len(scenarios)

    return {
        "naive_mean_regret":
            total_naive_regret / num_trials,

        "agent_mean_regret":
            total_agent_regret / num_trials,

        "naive_error_rate":
            naive_wrong_decisions / num_trials,

        "agent_error_rate":
            agent_wrong_decisions / num_trials
    }



def run_state_sweep(
    state,
    true_likelihoods,
    alphas,
    equity_simulations=50000,
    num_trials=100000
):
    user_cards = state["user_cards"]
    community_cards = state["community_cards"]

    # Calculate expensive ground truth once for this state
    ground_truth = precompute_ground_truth(
        user_cards,
        community_cards,
        true_likelihoods,
        simulations=equity_simulations
    )

    # Generate exactly the same scenarios for every alpha
    scenarios = generate_scenarios(
        num_trials=num_trials
    )

    state_results = []

    for alpha in alphas:

        agent_likelihoods = generate_misspecified_likelihoods(
            true_likelihoods,
            alpha
        )

        model_rmse = likelihood_rmse(
            true_likelihoods,
            agent_likelihoods
        )

        precomputed = precompute_agent_equity(
            user_cards,
            community_cards,
            ground_truth,
            agent_likelihoods,
            simulations=equity_simulations
        )

        experiment = run_experiment(
            scenarios,
            precomputed
        )

        state_results.append({
            "state": state["name"],
            "alpha": alpha,
            "likelihood_rmse": model_rmse,

            "naive_equity":
                ground_truth["naive_equity"],

            "agent_bet_equity":
                precomputed["agent_bet_equity"],

            "true_bet_equity":
                ground_truth["true_bet_equity"],

            **experiment
        })

    return state_results















'''def run_experiment(
    user_cards,
    community_cards,
    precomputed,
    true_likelihoods,
    num_trials
):
    total_naive_regret = 0
    total_agent_regret = 0

    naive_wrong_decisions = 0
    agent_wrong_decisions = 0

    for _ in range(num_trials):
        pot = 100
        opponent_bet = random.randrange(10, 401)

        result = run_fast_trial(
            user_cards,
            community_cards,
            precomputed,
            pot,
            opponent_bet,
            true_likelihoods
        )

        total_naive_regret += result["naive_regret"]
        total_agent_regret += result["agent_regret"]

        if result["naive_decision"] != result["optimal_decision"]:
            naive_wrong_decisions += 1

        if result["agent_decision"] != result["optimal_decision"]:
            agent_wrong_decisions += 1

    return {
        "naive_mean_regret":
            total_naive_regret / num_trials,

        "agent_mean_regret":
            total_agent_regret / num_trials,

        "naive_error_rate":
            naive_wrong_decisions / num_trials,

        "agent_error_rate":
            agent_wrong_decisions / num_trials
    }
'''
