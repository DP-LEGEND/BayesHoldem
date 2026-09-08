def call_decision(equity, pot, opponent_bet):
    reqd_equity = opponent_bet/(pot+2*opponent_bet)
    if equity >= reqd_equity:
        decision = "CALL"

    else:
        decision = "FOLD"

    return {
        "decision": decision,
        "equity": equity,
        "required_equity": reqd_equity,
        "equity_edge": equity - reqd_equity,
        "call_ev": equity * (pot + 2*opponent_bet) - opponent_bet
    }



def compare_decision_models(
    uniform_equity,
    bayesian_equity,
    pot,
    opponent_bet
):
    naive = call_decision(
        uniform_equity,
        pot,
        opponent_bet
    )

    bayesian = call_decision(
        bayesian_equity,
        pot,
        opponent_bet
    )

    return {
        "naive": naive,
        "bayesian": bayesian,
        "decision_changed": naive["decision"] != bayesian["decision"],
        "equity_difference": bayesian_equity - uniform_equity
    }