COMPLAINT_TYPE_OPTIONS = [
    ("primary", "Первичная жалоба"),
    ("repeat", "Повторная жалоба"),
]

__all__ = [
    "COMPLAINT_TYPE_OPTIONS",
    "REACTION_OPTIONS",
    "BOOLEAN_FIELD_LABELS",
    "STATE_FLAGS",
    "DEFAULT_INPUT",
    "DEFAULT_RULES",
]

REACTION_OPTIONS = [
    ("contact", "Нарушитель открыл дверь и вступил в контакт"),
    ("ignore", "Нарушитель не открыл дверь после 3 попыток"),
    ("aggression", "Нарушитель угрожает или проявляет агрессию"),
]

BOOLEAN_FIELD_LABELS = [
    ("vip_status", "Нарушитель имеет статус VIP"),
    ("complainant_insists", "Жалобщик настаивает на немедленных действиях"),
    ("settlement_success", "Шум урегулирован, жалобщик подтвердил тишину"),
    ("repeated_ignore", "После предупреждения дверь снова не открыли"),
    ("refused_to_reduce_noise", "Нарушитель отказался убавить звук"),
    ("refuses_to_leave", "Нарушитель отказывается покидать номер"),
]

STATE_FLAGS = [
    "warning_done",
    "door_warning_done",
    "priority_raised",
    "enhanced_settlement_done",
    "police_called",
    "eviction_escalation_started",
    "settlement_confirmed",
    "settlement_failed",
    "vip_protocol_applied",
    "eviction_completed",
    "morning_compliment_sent",
    "vip_manager_notified",
    "security_supervisor_notified",
    "guest_relocation_offered",
    "complainant_compensation_offered",
    "aggression_contained",
    "access_restricted",
    "monitoring_started",
    "case_closed",
]

DEFAULT_INPUT = {
    "complaint_type": "primary",
    "violator_reaction": "contact",
    "vip_status": False,
    "complainant_insists": False,
    "settlement_success": False,
    "repeated_ignore": False,
    "refused_to_reduce_noise": False,
    "refuses_to_leave": False,
}

DEFAULT_RULES = [
    {
        "id": "R1",
        "name": "Первичная жалоба - контакт, не VIP",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "primary"},
                {"var": "violator_reaction", "eq": "contact"},
                {"var": "vip_status", "eq": False},
            ]
        },
        "then": {
            "actions": [
                "Сделать устное предупреждение",
                "Внести запись в журнал",
                "Попросить нарушителя подтвердить снижение громкости",
            ],
            "set_flags": {
                "warning_done": True,
            },
            "final": False,
        },
    },
    {
        "id": "R2",
        "name": "Первичная жалоба - контакт, VIP",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "primary"},
                {"var": "violator_reaction", "eq": "contact"},
                {"var": "vip_status", "eq": True},
            ]
        },
        "then": {
            "actions": [
                "Передать контакт дежурному менеджеру по VIP-гостям",
                "Сделать персональное вежливое предупреждение без упоминания санкций",
                "Предложить VIP-гостю тихую альтернативу: приватную зону или переселение в номер выше классом",
                "Предложить жалобщику комплимент от отеля",
            ],
            "set_flags": {
                "warning_done": True,
                "vip_manager_notified": True,
                "guest_relocation_offered": True,
                "complainant_compensation_offered": True,
            },
            "final": False,
        },
    },
    {
        "id": "R3",
        "name": "Первичная жалоба - игнор, не VIP",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "primary"},
                {"var": "violator_reaction", "eq": "ignore"},
                {"var": "vip_status", "eq": False},
            ]
        },
        "then": {
            "actions": [
                "Отправить охрану под дверь",
                "Зачитать предупреждение через дверь",
                "Зафиксировать инцидент в журнале",
            ],
            "set_flags": {
                "door_warning_done": True,
            },
            "final": False,
        },
    },
    {
        "id": "R4",
        "name": "Первичная жалоба - игнор, VIP",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "primary"},
                {"var": "violator_reaction", "eq": "ignore"},
                {"var": "vip_status", "eq": True},
            ]
        },
        "then": {
            "actions": [
                "Подключить дежурного менеджера по VIP-гостям",
                "Попробовать связаться с VIP-гостем по внутреннему телефону",
                "Поставить охрану в режим ожидания без силового контакта",
                "Предложить жалобщику временное переселение в тихий номер",
            ],
            "set_flags": {
                "door_warning_done": True,
                "vip_manager_notified": True,
                "guest_relocation_offered": True,
                "complainant_compensation_offered": True,
            },
            "final": False,
        },
    },
    {
        "id": "R5",
        "name": "Первичная жалоба - агрессия, VIP",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "primary"},
                {"var": "violator_reaction", "eq": "aggression"},
                {"var": "settlement_success", "eq": False},
                {"var": "vip_status", "eq": True},
            ]
        },
        "then": {
            "actions": [
                "Вызвать наряд полиции",
                "Отвести персонал и гостей от зоны конфликта",
                "Немедленно подключить генерального менеджера или дежурного директора",
                "Отозвать охрану от силового контакта и оставить только периметр безопасности",
                "Предложить VIP-гостю изолированное размещение в президентском люксе",
                "Предложить жалобщику 50% скидку на текущее проживание",
                "Подарить жалобщику бутылку вина",
            ],
            "set_flags": {
                "police_called": True,
                "vip_protocol_applied": True,
                "vip_manager_notified": True,
                "aggression_contained": True,
                "guest_relocation_offered": True,
                "complainant_compensation_offered": True,
                "case_closed": True,
            },
            "final": True,
            "final_decision": "VIP-протокол при первичной агрессии",
        },
    },
    {
        "id": "R6",
        "name": "Первичная жалоба - агрессия, не VIP",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "primary"},
                {"var": "violator_reaction", "eq": "aggression"},
                {"var": "settlement_success", "eq": False},
                {"var": "vip_status", "eq": False},
            ]
        },
        "then": {
            "actions": [
                "Вызвать наряд полиции",
                "Вызвать старшего смены охраны",
                "Отвести персонал и гостей от зоны конфликта",
                "Заблокировать нарушителю доступ к услугам бара и общим зонам до решения менеджера",
                "Подготовить пакет документов для возможного выселения",
            ],
            "set_flags": {
                "police_called": True,
                "security_supervisor_notified": True,
                "aggression_contained": True,
                "access_restricted": True,
                "eviction_escalation_started": True,
            },
            "final": False,
        },
    },
    {
        "id": "R7",
        "name": "Повторная жалоба - агрессия, VIP",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "repeat"},
                {"var": "violator_reaction", "eq": "aggression"},
                {"var": "settlement_success", "eq": False},
                {"var": "vip_status", "eq": True},
            ]
        },
        "then": {
            "actions": [
                "Вызвать наряд полиции",
                "Немедленно подключить генерального менеджера или дежурного директора",
                "Изолировать зону конфликта без попытки выселения VIP-гостя",
                "Предложить VIP-гостю президентский люкс или отдельную приватную зону",
                "Предложить жалобщику 50% скидку на текущее проживание и переселение в тихий номер",
            ],
            "set_flags": {
                "police_called": True,
                "vip_protocol_applied": True,
                "vip_manager_notified": True,
                "aggression_contained": True,
                "guest_relocation_offered": True,
                "complainant_compensation_offered": True,
                "case_closed": True,
            },
            "final": True,
            "final_decision": "VIP-протокол при повторной агрессии",
        },
    },
    {
        "id": "R8",
        "name": "Повторная жалоба - агрессия, не VIP",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "repeat"},
                {"var": "violator_reaction", "eq": "aggression"},
                {"var": "settlement_success", "eq": False},
                {"var": "vip_status", "eq": False},
            ]
        },
        "then": {
            "actions": [
                "Повысить приоритет до критического",
                "Вызвать наряд полиции",
                "Вызвать старшего смены охраны",
                "Изолировать нарушителя от других гостей",
                "Подготовить номер к блокировке доступа после решения менеджера",
                "Подготовить пакет документов для выселения",
            ],
            "set_flags": {
                "priority_raised": True,
                "police_called": True,
                "security_supervisor_notified": True,
                "aggression_contained": True,
                "access_restricted": True,
                "eviction_escalation_started": True,
            },
            "final": False,
        },
    },
    {
        "id": "R9",
        "name": "Повторная жалоба без агрессии - VIP",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "repeat"},
                {
                    "any": [
                        {"var": "violator_reaction", "eq": "contact"},
                        {"var": "violator_reaction", "eq": "ignore"},
                    ]
                },
                {"var": "vip_status", "eq": True},
            ]
        },
        "then": {
            "actions": [
                "Повысить приоритет",
                "Подключить дежурного менеджера по VIP-гостям",
                "Предложить VIP-гостю переселение в номер выше классом или приватную зону",
                "Предложить жалобщику компенсацию и тихий номер",
            ],
            "set_flags": {
                "priority_raised": True,
                "enhanced_settlement_done": True,
                "vip_manager_notified": True,
                "guest_relocation_offered": True,
                "complainant_compensation_offered": True,
            },
            "final": False,
        },
    },
    {
        "id": "R10",
        "name": "Повторная жалоба без агрессии - не VIP",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "repeat"},
                {
                    "any": [
                        {"var": "violator_reaction", "eq": "contact"},
                        {"var": "violator_reaction", "eq": "ignore"},
                    ]
                },
                {"var": "vip_status", "eq": False},
            ]
        },
        "then": {
            "actions": [
                "Повысить приоритет",
                "Отправить менеджера и охрану",
                "Предложить нарушителю переселение в другой номер",
                "Предложить жалобщику компенсацию",
            ],
            "set_flags": {
                "priority_raised": True,
                "enhanced_settlement_done": True,
                "guest_relocation_offered": True,
                "complainant_compensation_offered": True,
            },
            "final": False,
        },
    },
    {
        "id": "R11",
        "name": "Успешное урегулирование после первичного контакта - VIP",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "primary"},
                {"var": "warning_done", "eq": True},
                {"var": "violator_reaction", "eq": "contact"},
                {"var": "settlement_success", "eq": True},
                {"var": "vip_status", "eq": True},
            ]
        },
        "then": {
            "actions": [
                "Зафиксировать подтверждение тишины",
                "Отправить жалобщику персональный комплимент от менеджера",
                "Передать кейс менеджеру по VIP-гостям для утреннего follow-up",
            ],
            "set_flags": {
                "settlement_confirmed": True,
                "morning_compliment_sent": True,
                "vip_manager_notified": True,
                "case_closed": True,
            },
            "final": True,
            "final_decision": "VIP-урегулирование после первичного предупреждения",
        },
    },
    {
        "id": "R12",
        "name": "Успешное урегулирование после первичного контакта - не VIP",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "primary"},
                {"var": "warning_done", "eq": True},
                {"var": "violator_reaction", "eq": "contact"},
                {"var": "settlement_success", "eq": True},
                {"var": "vip_status", "eq": False},
            ]
        },
        "then": {
            "actions": [
                "Зафиксировать подтверждение тишины",
                "Отправить жалобщику комплимент утром",
            ],
            "set_flags": {
                "settlement_confirmed": True,
                "morning_compliment_sent": True,
                "case_closed": True,
            },
            "final": True,
            "final_decision": "Урегулирование после первичного предупреждения",
        },
    },
    {
        "id": "R13",
        "name": "Успешное урегулирование после повторной жалобы - VIP",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "repeat"},
                {"var": "enhanced_settlement_done", "eq": True},
                {"var": "violator_reaction", "eq": "contact"},
                {"var": "settlement_success", "eq": True},
                {"var": "vip_status", "eq": True},
            ]
        },
        "then": {
            "actions": [
                "Зафиксировать подтверждение тишины",
                "Отправить жалобщику персональный комплимент от менеджера",
                "Оставить VIP-гостю мягкое напоминание о правилах тишины",
                "Передать кейс менеджеру по VIP-гостям для утреннего follow-up",
            ],
            "set_flags": {
                "settlement_confirmed": True,
                "morning_compliment_sent": True,
                "vip_manager_notified": True,
                "case_closed": True,
            },
            "final": True,
            "final_decision": "VIP-урегулирование после повторной жалобы",
        },
    },
    {
        "id": "R14",
        "name": "Успешное урегулирование после повторной жалобы - не VIP",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "repeat"},
                {"var": "enhanced_settlement_done", "eq": True},
                {"var": "violator_reaction", "eq": "contact"},
                {"var": "settlement_success", "eq": True},
                {"var": "vip_status", "eq": False},
            ]
        },
        "then": {
            "actions": [
                "Отправить жалобщику комплимент утром",
                "Внести в карточку нарушителя пометку 'шум, урегулировано'",
            ],
            "set_flags": {
                "settlement_confirmed": True,
                "morning_compliment_sent": True,
                "case_closed": True,
            },
            "final": True,
            "final_decision": "Успешное урегулирование после повторной жалобы",
        },
    },
    {
        "id": "R15",
        "name": "Отказ снизить шум после контакта - VIP",
        "if": {
            "all": [
                {"var": "violator_reaction", "eq": "contact"},
                {"var": "refused_to_reduce_noise", "eq": True},
                {"var": "settlement_success", "eq": False},
                {"var": "vip_status", "eq": True},
            ]
        },
        "then": {
            "actions": [
                "Подключить дежурного менеджера по VIP-гостям",
                "Предложить VIP-гостю президентский люкс или приватную зону для продолжения вечера",
                "Предложить жалобщику 50% скидку на текущее проживание",
                "Подарить жалобщику бутылку вина",
            ],
            "set_flags": {
                "settlement_failed": True,
                "vip_protocol_applied": True,
                "vip_manager_notified": True,
                "guest_relocation_offered": True,
                "complainant_compensation_offered": True,
                "case_closed": True,
            },
            "final": True,
            "final_decision": "VIP-протокол после отказа снизить шум",
        },
    },
    {
        "id": "R16",
        "name": "Отказ снизить шум после контакта - не VIP, жесткая эскалация",
        "if": {
            "all": [
                {"var": "violator_reaction", "eq": "contact"},
                {"var": "refused_to_reduce_noise", "eq": True},
                {"var": "settlement_success", "eq": False},
                {
                    "any": [
                        {"var": "complainant_insists", "eq": True},
                        {"var": "refuses_to_leave", "eq": True},
                    ]
                },
                {"var": "vip_status", "eq": False},
            ]
        },
        "then": {
            "actions": [
                "Вызвать охрану",
                "Вызвать наряд полиции",
                "Предупредить нарушителя о подготовке выселения",
                "Предложить жалобщику компенсацию",
            ],
            "set_flags": {
                "police_called": True,
                "settlement_failed": True,
                "complainant_compensation_offered": True,
                "eviction_escalation_started": True,
            },
            "final": False,
        },
    },
    {
        "id": "R17",
        "name": "Отказ снизить шум после контакта - не VIP, мягкая эскалация",
        "if": {
            "all": [
                {"var": "violator_reaction", "eq": "contact"},
                {"var": "refused_to_reduce_noise", "eq": True},
                {"var": "settlement_success", "eq": False},
                {"var": "complainant_insists", "eq": False},
                {"var": "refuses_to_leave", "eq": False},
                {"var": "vip_status", "eq": False},
            ]
        },
        "then": {
            "actions": [
                "Зафиксировать отказ снизить шум",
                "Направить менеджера на повторный контакт",
                "Поставить охрану на контроль этажа",
                "Предложить жалобщику компенсацию",
            ],
            "set_flags": {
                "settlement_failed": True,
                "security_supervisor_notified": True,
                "complainant_compensation_offered": True,
                "monitoring_started": True,
                "case_closed": True,
            },
            "final": True,
            "final_decision": "Мягкая эскалация после отказа снизить шум",
        },
    },
    {
        "id": "R18",
        "name": "Повторный игнор после предупреждения - VIP",
        "if": {
            "all": [
                {"var": "door_warning_done", "eq": True},
                {"var": "repeated_ignore", "eq": True},
                {"var": "settlement_success", "eq": False},
                {"var": "vip_status", "eq": True},
            ]
        },
        "then": {
            "actions": [
                "Подключить генерального менеджера или дежурного директора",
                "Отозвать охрану от силового контакта",
                "Предложить VIP-гостю президентский люкс или приватную зону",
                "Предложить жалобщику 50% скидку на текущее проживание",
                "Подарить жалобщику бутылку вина",
            ],
            "set_flags": {
                "vip_protocol_applied": True,
                "vip_manager_notified": True,
                "guest_relocation_offered": True,
                "complainant_compensation_offered": True,
                "case_closed": True,
            },
            "final": True,
            "final_decision": "VIP-протокол после повторного игнора",
        },
    },
    {
        "id": "R19",
        "name": "Повторный игнор после предупреждения - не VIP, жесткая эскалация",
        "if": {
            "all": [
                {"var": "door_warning_done", "eq": True},
                {"var": "repeated_ignore", "eq": True},
                {"var": "settlement_success", "eq": False},
                {
                    "any": [
                        {"var": "complainant_insists", "eq": True},
                        {"var": "refuses_to_leave", "eq": True},
                    ]
                },
                {"var": "vip_status", "eq": False},
            ]
        },
        "then": {
            "actions": [
                "Вызвать наряд полиции",
                "Вызвать старшего смены охраны",
                "Предупредить нарушителя о подготовке выселения через дверь",
                "Предложить жалобщику компенсацию",
            ],
            "set_flags": {
                "police_called": True,
                "security_supervisor_notified": True,
                "complainant_compensation_offered": True,
                "eviction_escalation_started": True,
            },
            "final": False,
        },
    },
    {
        "id": "R20",
        "name": "Повторный игнор после предупреждения - не VIP, контроль этажа",
        "if": {
            "all": [
                {"var": "door_warning_done", "eq": True},
                {"var": "repeated_ignore", "eq": True},
                {"var": "settlement_success", "eq": False},
                {"var": "complainant_insists", "eq": False},
                {"var": "refuses_to_leave", "eq": False},
                {"var": "vip_status", "eq": False},
            ]
        },
        "then": {
            "actions": [
                "Зафиксировать повторный игнор",
                "Оставить охрану на контроле этажа",
                "Передать кейс старшему смены",
                "Предложить жалобщику компенсацию",
            ],
            "set_flags": {
                "security_supervisor_notified": True,
                "complainant_compensation_offered": True,
                "monitoring_started": True,
                "case_closed": True,
            },
            "final": True,
            "final_decision": "Контроль этажа после повторного игнора",
        },
    },
    {
        "id": "R21",
        "name": "Повторная жалоба с повторным игнором - VIP",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "repeat"},
                {"var": "enhanced_settlement_done", "eq": True},
                {"var": "violator_reaction", "eq": "ignore"},
                {"var": "repeated_ignore", "eq": True},
                {"var": "settlement_success", "eq": False},
                {"var": "vip_status", "eq": True},
            ]
        },
        "then": {
            "actions": [
                "Подключить генерального менеджера или дежурного директора",
                "Отозвать охрану от силового контакта",
                "Продолжить связь с VIP-гостем через персонального менеджера",
                "Предложить VIP-гостю президентский люкс или приватную зону",
                "Предложить жалобщику 50% скидку на текущее проживание",
                "Подарить жалобщику бутылку вина",
            ],
            "set_flags": {
                "vip_protocol_applied": True,
                "vip_manager_notified": True,
                "guest_relocation_offered": True,
                "complainant_compensation_offered": True,
                "case_closed": True,
            },
            "final": True,
            "final_decision": "VIP-протокол при повторной жалобе с повторным игнором",
        },
    },
    {
        "id": "R22",
        "name": "Повторная жалоба с повторным игнором - не VIP, жесткая эскалация",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "repeat"},
                {"var": "enhanced_settlement_done", "eq": True},
                {"var": "violator_reaction", "eq": "ignore"},
                {"var": "repeated_ignore", "eq": True},
                {"var": "settlement_success", "eq": False},
                {
                    "any": [
                        {"var": "complainant_insists", "eq": True},
                        {"var": "refuses_to_leave", "eq": True},
                    ]
                },
                {"var": "vip_status", "eq": False},
            ]
        },
        "then": {
            "actions": [
                "Вызвать наряд полиции",
                "Вызвать старшего смены охраны",
                "Предупредить нарушителя о подготовке выселения через дверь",
                "Предложить жалобщику компенсацию",
            ],
            "set_flags": {
                "police_called": True,
                "security_supervisor_notified": True,
                "complainant_compensation_offered": True,
                "eviction_escalation_started": True,
            },
            "final": False,
        },
    },
    {
        "id": "R23",
        "name": "Повторная жалоба с повторным игнором - не VIP, контроль этажа",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "repeat"},
                {"var": "enhanced_settlement_done", "eq": True},
                {"var": "violator_reaction", "eq": "ignore"},
                {"var": "repeated_ignore", "eq": True},
                {"var": "settlement_success", "eq": False},
                {"var": "complainant_insists", "eq": False},
                {"var": "refuses_to_leave", "eq": False},
                {"var": "vip_status", "eq": False},
            ]
        },
        "then": {
            "actions": [
                "Зафиксировать повторный игнор после повторной жалобы",
                "Оставить охрану на контроле этажа",
                "Передать кейс старшему смены",
                "Подтвердить жалобщику предложение компенсации",
            ],
            "set_flags": {
                "security_supervisor_notified": True,
                "complainant_compensation_offered": True,
                "monitoring_started": True,
                "case_closed": True,
            },
            "final": True,
            "final_decision": "Контроль этажа после повторной жалобы с повторным игнором",
        },
    },
    {
        "id": "R24",
        "name": "Принудительное выселение не VIP",
        "if": {
            "all": [
                {"var": "eviction_escalation_started", "eq": True},
                {"var": "settlement_success", "eq": False},
                {"var": "refuses_to_leave", "eq": True},
                {"var": "vip_status", "eq": False},
            ]
        },
        "then": {
            "actions": [
                "Принудительно выселить нарушителя",
                "Внести нарушителя в федеральный черный список сети",
                "Компенсировать 1 ночь всем пострадавшим гостям на этаже",
            ],
            "set_flags": {
                "eviction_completed": True,
                "case_closed": True,
            },
            "final": True,
            "final_decision": "Принудительное выселение не-VIP",
        },
    },
    {
        "id": "R25",
        "name": "Жесткая эскалация не VIP без принудительного выселения",
        "if": {
            "all": [
                {"var": "eviction_escalation_started", "eq": True},
                {"var": "settlement_success", "eq": False},
                {"var": "refuses_to_leave", "eq": False},
                {"var": "vip_status", "eq": False},
            ]
        },
        "then": {
            "actions": [
                "Оставить нарушителя под контролем охраны до решения полиции или менеджера",
                "Передать кейс управляющему смены",
                "Предложить пострадавшим гостям компенсацию",
            ],
            "set_flags": {
                "monitoring_started": True,
                "complainant_compensation_offered": True,
                "case_closed": True,
            },
            "final": True,
            "final_decision": "Жесткая эскалация без принудительного выселения",
        },
    },
    {
        "id": "R26",
        "name": "Мониторинг после первичного контакта - VIP",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "primary"},
                {"var": "warning_done", "eq": True},
                {"var": "violator_reaction", "eq": "contact"},
                {"var": "settlement_success", "eq": False},
                {"var": "refused_to_reduce_noise", "eq": False},
                {"var": "vip_status", "eq": True},
            ]
        },
        "then": {
            "actions": [
                "Оставить VIP-кейс на контроле дежурного менеджера",
                "Проверить тишину повторным звонком жалобщику",
                "Сохранить предложенный комплимент жалобщику",
            ],
            "set_flags": {
                "monitoring_started": True,
                "vip_manager_notified": True,
                "case_closed": True,
            },
            "final": True,
            "final_decision": "VIP-предупреждение и мониторинг",
        },
    },
    {
        "id": "R27",
        "name": "Мониторинг после первичного контакта - не VIP",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "primary"},
                {"var": "warning_done", "eq": True},
                {"var": "violator_reaction", "eq": "contact"},
                {"var": "settlement_success", "eq": False},
                {"var": "refused_to_reduce_noise", "eq": False},
                {"var": "vip_status", "eq": False},
            ]
        },
        "then": {
            "actions": [
                "Оставить предупреждение на контроле администратора",
                "Проверить тишину повторным звонком жалобщику",
            ],
            "set_flags": {
                "monitoring_started": True,
                "case_closed": True,
            },
            "final": True,
            "final_decision": "Предупреждение и мониторинг",
        },
    },
    {
        "id": "R28",
        "name": "Мониторинг после первичного игнора - VIP",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "primary"},
                {"var": "door_warning_done", "eq": True},
                {"var": "violator_reaction", "eq": "ignore"},
                {"var": "repeated_ignore", "eq": False},
                {"var": "vip_status", "eq": True},
            ]
        },
        "then": {
            "actions": [
                "Оставить VIP-кейс на контроле дежурного менеджера",
                "Продолжить попытку связи с VIP-гостем без силового контакта",
                "Проверить состояние жалобщика и предложить тихий номер",
            ],
            "set_flags": {
                "monitoring_started": True,
                "vip_manager_notified": True,
                "case_closed": True,
            },
            "final": True,
            "final_decision": "VIP-мониторинг после первичного игнора",
        },
    },
    {
        "id": "R29",
        "name": "Мониторинг после первичного игнора - не VIP",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "primary"},
                {"var": "door_warning_done", "eq": True},
                {"var": "violator_reaction", "eq": "ignore"},
                {"var": "repeated_ignore", "eq": False},
                {"var": "vip_status", "eq": False},
            ]
        },
        "then": {
            "actions": [
                "Оставить охрану на контроле этажа",
                "Проверить тишину повторным звонком жалобщику",
            ],
            "set_flags": {
                "monitoring_started": True,
                "case_closed": True,
            },
            "final": True,
            "final_decision": "Контроль после предупреждения через дверь",
        },
    },
    {
        "id": "R30",
        "name": "Мониторинг после повторной жалобы с контактом - VIP",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "repeat"},
                {"var": "enhanced_settlement_done", "eq": True},
                {"var": "violator_reaction", "eq": "contact"},
                {"var": "settlement_success", "eq": False},
                {"var": "refused_to_reduce_noise", "eq": False},
                {"var": "vip_status", "eq": True},
            ]
        },
        "then": {
            "actions": [
                "Оставить VIP-кейс на контроле дежурного менеджера",
                "Подтвердить доступность тихого номера для жалобщика",
                "Проверить тишину повторным звонком жалобщику",
            ],
            "set_flags": {
                "monitoring_started": True,
                "vip_manager_notified": True,
                "case_closed": True,
            },
            "final": True,
            "final_decision": "VIP-мониторинг после повторной жалобы",
        },
    },
    {
        "id": "R31",
        "name": "Мониторинг после повторной жалобы с контактом - не VIP",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "repeat"},
                {"var": "enhanced_settlement_done", "eq": True},
                {"var": "violator_reaction", "eq": "contact"},
                {"var": "settlement_success", "eq": False},
                {"var": "refused_to_reduce_noise", "eq": False},
                {"var": "vip_status", "eq": False},
            ]
        },
        "then": {
            "actions": [
                "Оставить кейс на контроле администратора",
                "Проверить тишину повторным звонком жалобщику",
                "Сохранить предложение компенсации жалобщику",
            ],
            "set_flags": {
                "monitoring_started": True,
                "case_closed": True,
            },
            "final": True,
            "final_decision": "Мониторинг после повторной жалобы",
        },
    },
    {
        "id": "R32",
        "name": "Мониторинг после повторной жалобы с игнором - VIP",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "repeat"},
                {"var": "enhanced_settlement_done", "eq": True},
                {"var": "violator_reaction", "eq": "ignore"},
                {"var": "repeated_ignore", "eq": False},
                {"var": "vip_status", "eq": True},
            ]
        },
        "then": {
            "actions": [
                "Оставить VIP-кейс на контроле дежурного менеджера",
                "Продолжить связь с VIP-гостем через персонального менеджера",
                "Подтвердить жалобщику компенсацию и возможность переселения",
            ],
            "set_flags": {
                "monitoring_started": True,
                "vip_manager_notified": True,
                "case_closed": True,
            },
            "final": True,
            "final_decision": "VIP-мониторинг после повторной жалобы с игнором",
        },
    },
    {
        "id": "R33",
        "name": "Мониторинг после повторной жалобы с игнором - не VIP",
        "if": {
            "all": [
                {"var": "complaint_type", "eq": "repeat"},
                {"var": "enhanced_settlement_done", "eq": True},
                {"var": "violator_reaction", "eq": "ignore"},
                {"var": "repeated_ignore", "eq": False},
                {"var": "vip_status", "eq": False},
            ]
        },
        "then": {
            "actions": [
                "Оставить охрану на контроле этажа",
                "Передать кейс управляющему смены",
                "Подтвердить жалобщику предложение компенсации",
            ],
            "set_flags": {
                "monitoring_started": True,
                "security_supervisor_notified": True,
                "case_closed": True,
            },
            "final": True,
            "final_decision": "Контроль после повторной жалобы с игнором",
        },
    },
]
