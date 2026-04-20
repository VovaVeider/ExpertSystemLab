DEFAULT_RULES = [
    {
        "id": "R1",
        "name": "Первичная жалоба — контакт",
        "description": "Первичная жалоба на шум, нарушитель открыл дверь и вступил в контакт.",
        "if": {
            "all": [
                {"var": "noise_complaint", "eq": True},
                {"var": "primary_complaint", "eq": True},
                {"var": "contact_reaction", "eq": True},
            ]
        },
        "then": {
            "actions": [
                "Сделать устное предупреждение",
                "Внести запись в журнал",
            ],
            "set_flags": ["rule1_done"],
            "next_rule": "R2",
            "final": False,
        },
    },
    {
        "id": "R2",
        "name": "Эскалация при повторной жалобе",
        "description": "После выполнения R1 поступила повторная жалоба на тот же номер за последний час.",
        "if": {
            "all": [
                {"var": "rule1_done", "eq": True},
                {"var": "repeat_complaint", "eq": True},
            ]
        },
        "then": {
            "actions": ["Повысить приоритет"],
            "set_flags": ["rule2_done"],
            "next_rule": "R5",
            "final": False,
        },
    },
    {
        "id": "R3",
        "name": "Первичная жалоба — игнор",
        "description": "Первичная жалоба на шум, нарушитель не открыл дверь после 3 попыток.",
        "if": {
            "all": [
                {"var": "noise_complaint", "eq": True},
                {"var": "primary_complaint", "eq": True},
                {"var": "ignore_reaction", "eq": True},
            ]
        },
        "then": {
            "actions": [
                "Отправить охрану под дверь",
                "Зачитать предупреждение через дверь",
                "Зафиксировать инцидент в журнале",
            ],
            "set_flags": ["rule3_done"],
            "next_rule": "R6",
            "final": False,
        },
    },
    {
        "id": "R4",
        "name": "Первичная жалоба — агрессия",
        "description": "Первичная жалоба на шум, нарушитель угрожает менеджеру или проявляет агрессию.",
        "if": {
            "all": [
                {"var": "noise_complaint", "eq": True},
                {"var": "primary_complaint", "eq": True},
                {"var": "aggressive_reaction", "eq": True},
            ]
        },
        "then": {
            "actions": ["Вызвать наряд полиции"],
            "set_flags": ["rule4_done"],
            "next_rule": "R8",
            "final": False,
        },
    },
    {
        "id": "R5",
        "name": "Повторная жалоба — контакт или мягкий игнор",
        "description": "Эскалация после повторной жалобы или повтор после первичного игнора.",
        "if": {
            "any": [
                {"all": [{"var": "rule2_done", "eq": True}]},
                {
                    "all": [
                        {"var": "rule3_done", "eq": True},
                        {"var": "repeat_complaint", "eq": True},
                    ]
                },
            ]
        },
        "then": {
            "actions": [
                "Отправить менеджера и охрану",
                "Предложить нарушителю переселение в другой номер",
                "Предложить жалобщику компенсацию",
            ],
            "set_flags": ["rule5_done"],
            "next_rule_options": ["R7", "R9"],
            "final": False,
        },
    },
    {
        "id": "R6",
        "name": "Игнор с нарастанием — развилка по статусу",
        "description": "После первичного игнора нарушитель снова не открыл дверь, а жалобщик настаивает на немедленных действиях.",
        "if": {
            "all": [
                {"var": "rule3_done", "eq": True},
                {"var": "repeated_ignore_after_warning", "eq": True},
                {"var": "complainant_insists", "eq": True},
            ]
        },
        "then": {
            "actions": ["Вызвать наряд полиции"],
            "set_flags": ["rule6_done"],
            "branching": [
                {
                    "if": {"all": [{"var": "vip_status", "eq": True}]},
                    "then": {
                        "actions": [
                            "Отозвать охрану",
                            "Предложить нарушителю апгрейд до президентского люкса",
                            "Предложить жалобщику 50% скидку на текущее проживание",
                            "Подарить жалобщику бутылку вина",
                        ],
                        "set_flags": ["rule6_vip_done"],
                        "final": True,
                        "final_decision": "VIP-протокол после игнора",
                    },
                },
                {
                    "if": {"all": [{"var": "vip_status", "eq": False}]},
                    "then": {
                        "actions": [],
                        "set_flags": ["rule6_non_vip_done"],
                        "next_rule": "R8",
                        "final": False,
                    },
                },
            ],
        },
    },
    {
        "id": "R7",
        "name": "Успешное урегулирование",
        "description": "После R5 нарушитель открыл дверь, согласился убавить звук, а жалобщик подтвердил тишину через 10 минут.",
        "if": {
            "all": [
                {"var": "rule5_done", "eq": True},
                {"var": "contact_reaction", "eq": True},
                {"var": "settlement_success", "eq": True},
            ]
        },
        "then": {
            "actions": [
                "Отправить жалобщику комплимент утром",
                "Внести в карточку нарушителя пометку 'шум, урегулировано'",
            ],
            "set_flags": ["rule7_done"],
            "final": True,
            "final_decision": "Успешное урегулирование",
        },
    },
    {
        "id": "R8",
        "name": "Принудительное выселение не-VIP",
        "description": "Выселение нарушителя не-VIP после агрессии, эскалации игнора или безуспешного урегулирования.",
        "if": {
            "all": [
                {
                    "any": [
                        {
                            "all": [
                                {"var": "rule4_done", "eq": True},
                                {"var": "vip_status", "eq": False},
                            ]
                        },
                        {"all": [{"var": "rule6_non_vip_done", "eq": True}]},
                        {
                            "all": [
                                {"var": "rule9_done", "eq": True},
                                {"var": "vip_status", "eq": False},
                            ]
                        },
                    ]
                },
                {"var": "refuses_to_leave", "eq": True},
                {"var": "police_report_created", "eq": True},
            ]
        },
        "then": {
            "actions": [
                "Принудительно выселить нарушителя",
                "Внести нарушителя в федеральный черный список сети",
                "Компенсировать 1 ночь всем пострадавшим гостям на этаже",
            ],
            "set_flags": ["rule8_done"],
            "final": True,
            "final_decision": "Принудительное выселение не-VIP",
        },
    },
    {
        "id": "R9",
        "name": "Безуспешное урегулирование — эскалация",
        "description": "После R5 нарушитель не открыл дверь после 3 попыток или отказался убавить звук, а жалобщик требует немедленных действий.",
        "if": {
            "all": [
                {"var": "rule5_done", "eq": True},
                {
                    "any": [
                        {"var": "ignore_reaction", "eq": True},
                        {"var": "refused_to_reduce_noise", "eq": True},
                    ]
                },
                {"var": "complainant_insists", "eq": True},
            ]
        },
        "then": {
            "actions": ["Вызвать охрану", "Вызвать наряд полиции"],
            "set_flags": ["rule9_done"],
            "next_rule": "R8",
            "final": False,
        },
    },
    {
        "id": "R10",
        "name": "VIP-протокол при первичной агрессии",
        "description": "После первичной агрессии нарушитель имеет статус VIP.",
        "if": {
            "all": [
                {"var": "rule4_done", "eq": True},
                {"var": "vip_status", "eq": True},
            ]
        },
        "then": {
            "actions": [
                "Отозвать охрану, если была вызвана",
                "Предложить нарушителю апгрейд до президентского люкса",
                "Предложить жалобщику 50% скидку на текущее проживание",
                "Подарить жалобщику бутылку вина",
            ],
            "set_flags": ["rule10_done"],
            "final": True,
            "final_decision": "VIP-протокол при первичной агрессии",
        },
    },
]

DEFAULT_INPUT = {
    "noise_complaint": True,
    "primary_complaint": True,
    "repeat_complaint": False,
    "contact_reaction": True,
    "ignore_reaction": False,
    "aggressive_reaction": False,
    "vip_status": False,
    "complainant_insists": False,
    "settlement_success": False,
    "repeated_ignore_after_warning": False,
    "refuses_to_leave": False,
    "police_report_created": False,
    "refused_to_reduce_noise": False,
    "rule1_done": False,
    "rule2_done": False,
    "rule3_done": False,
    "rule4_done": False,
    "rule5_done": False,
    "rule6_done": False,
    "rule6_vip_done": False,
    "rule6_non_vip_done": False,
    "rule7_done": False,
    "rule8_done": False,
    "rule9_done": False,
    "rule10_done": False,
}

INPUT_FIELD_LABELS = [
    ("noise_complaint", "Поступила жалоба на шум"),
    ("primary_complaint", "Жалоба первичная"),
    ("repeat_complaint", "Жалоба повторная"),
    ("contact_reaction", "Нарушитель открыл дверь и вступил в контакт"),
    ("ignore_reaction", "Нарушитель не открыл дверь после 3 попыток"),
    ("aggressive_reaction", "Нарушитель угрожает или проявляет агрессию"),
    ("vip_status", "Нарушитель имеет статус VIP"),
    ("complainant_insists", "Жалобщик настаивает на немедленных действиях"),
    ("settlement_success", "Шум урегулирован, жалобщик подтвердил тишину"),
    ("repeated_ignore_after_warning", "После нового предупреждения дверь снова не открыли"),
    ("refused_to_reduce_noise", "Нарушитель отказался убавить звук"),
    ("refuses_to_leave", "Нарушитель отказывается покидать номер"),
    ("police_report_created", "Полиция составила протокол"),
]
