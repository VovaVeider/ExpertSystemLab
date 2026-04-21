import json


def run_inference(rules, input_data):
    state_flag_names = collect_state_flag_names(rules)
    state = {
        key: value
        for key, value in input_data.items()
        if key not in state_flag_names
    }
    triggered_rules = []
    actions = []
    applied_rule_ids = set()
    final = False
    final_decision = None

    conflict_messages = detect_conflicts(state)
    if conflict_messages:
        return {
            "triggered_rules": [],
            "actions": [],
            "final": False,
            "final_decision": None,
            "missing_data": [],
            "conflict_detected": True,
            "explanation": "; ".join(conflict_messages),
        }

    changed = True
    while changed and not final:
        changed = False

        for rule in rules:
            rule_id = rule.get("id")
            if not rule_id or rule_id in applied_rule_ids:
                continue

            condition = rule.get("if", {})
            if not condition_matches(condition, state):
                continue

            applied_rule_ids.add(rule_id)
            triggered_rules.append(rule_id)

            then = rule.get("then", {})
            for action in then.get("actions", []):
                if action not in actions:
                    actions.append(action)

            state.update(then.get("set_flags", {}))
            changed = True

            if then.get("final") is True:
                final = True
                final_decision = then.get("final_decision")

            break

    return {
        "triggered_rules": triggered_rules,
        "actions": actions,
        "final": final,
        "final_decision": final_decision if final else None,
        "missing_data": find_missing_data(
            rules,
            state,
            applied_rule_ids,
            final,
            state_flag_names,
        ),
        "conflict_detected": False,
        "explanation": build_explanation(triggered_rules, final, final_decision),
    }


def run_inference_json(rules, input_data):
    return json.dumps(run_inference(rules, input_data), ensure_ascii=False, indent=2)


def condition_matches(condition, state):
    if "all" in condition:
        return all(condition_matches(item, state) for item in condition["all"])

    if "any" in condition:
        return any(condition_matches(item, state) for item in condition["any"])

    if "var" in condition and "eq" in condition:
        return state.get(condition["var"]) == condition["eq"]

    return False


def collect_state_flag_names(rules):
    state_flag_names = set()
    for rule in rules:
        set_flags = rule.get("then", {}).get("set_flags", {})
        state_flag_names.update(set_flags.keys())
    return state_flag_names


def detect_conflicts(state):
    conflicts = []
    reaction = state.get("violator_reaction")

    if state.get("settlement_success") and reaction != "contact":
        conflicts.append("Успешное урегулирование возможно только при реакции 'contact'")

    if state.get("settlement_success") and state.get("refused_to_reduce_noise"):
        conflicts.append("Нельзя одновременно указать успешное урегулирование и отказ снизить шум")

    if state.get("settlement_success") and state.get("repeated_ignore"):
        conflicts.append("Нельзя одновременно указать успешное урегулирование и повторный игнор")

    if state.get("settlement_success") and state.get("refuses_to_leave"):
        conflicts.append("Нельзя одновременно указать успешное урегулирование и отказ покидать номер")

    if state.get("repeated_ignore") and reaction != "ignore":
        conflicts.append("Повторный игнор допустим только при реакции 'ignore'")

    if state.get("refused_to_reduce_noise") and reaction != "contact":
        conflicts.append("Отказ снизить шум допустим только при реакции 'contact'")

    if state.get("refuses_to_leave") and not (
        reaction == "aggression"
        or state.get("refused_to_reduce_noise")
        or state.get("repeated_ignore")
    ):
        conflicts.append(
            "Отказ покидать номер допустим только при агрессии, отказе снизить шум или повторном игноре"
        )

    return conflicts


def find_missing_data(rules, state, applied_rule_ids, final, state_flag_names):
    if final:
        return []

    missing_data = []
    for rule in rules:
        if rule.get("id") in applied_rule_ids:
            continue
        collect_missing_vars(rule.get("if", {}), state, missing_data, state_flag_names)

    return missing_data


def collect_missing_vars(condition, state, missing_data, state_flag_names):
    if "all" in condition:
        for item in condition["all"]:
            collect_missing_vars(item, state, missing_data, state_flag_names)
        return

    if "any" in condition:
        for item in condition["any"]:
            collect_missing_vars(item, state, missing_data, state_flag_names)
        return

    var_name = condition.get("var")
    if var_name in state_flag_names:
        return
    if var_name and var_name not in state and var_name not in missing_data:
        missing_data.append(var_name)


def build_explanation(triggered_rules, final, final_decision):
    if not triggered_rules:
        return "Ни одно правило не сработало."

    rule_chain = ", ".join(triggered_rules)
    if final:
        return f"Сработали правила: {rule_chain}. Итоговое решение: {final_decision}."

    return f"Сработали правила: {rule_chain}. Финальное правило не найдено."
