# ExpertSystemLab

Экспертная система для обработки жалоб на шум в отеле.

Проект моделирует работу администратора, охраны и менеджмента отеля при первичных и повторных жалобах на шум. Система принимает понятные входные факты о текущей ситуации, применяет набор правил и возвращает список действий, сработавшие правила, итоговое решение и краткое объяснение.

## Возможности

- Обработка первичных и повторных жалоб.
- Разные сценарии для обычных гостей и VIP-гостей.
- Защита от некорректных комбинаций входных фактов.
- Два режима выполнения:
  - локальная машина вывода;
  - LLM / Ollama.
- Финальные решения по успешному урегулированию, мониторингу, VIP-протоколу и выселению не-VIP.
- Копируемые поля результата в интерфейсе.
- Настройка Ollama через `.env`.

## Главное правило бизнес-логики

VIP-гость не выселяется и не попадает в черный список. Во всех жестких VIP-сценариях система переводит кейс в VIP-протокол. Принудительное выселение возможно только для не-VIP.

## Структура проекта

| Файл | Назначение |
|---|---|
| `expert_system.py` | Точка входа в приложение. |
| `interface.py` | Tkinter-интерфейс: ввод фактов, выбор режима, вывод результата. |
| `rules.py` | Единая модель данных и набор правил `DEFAULT_RULES`. |
| `inference_engine.py` | Локальная машина вывода, которая применяет правила без LLM. |
| `llm_client.py` | Клиент для обращения к Ollama-совместимому API. |
| `prompts.py` | Строгие промпты для режима LLM. |
| `.env.example` | Пример настройки окружения. |

## Настройка окружения

Создайте локальный `.env` на основе `.env.example`:

```env
OLLAMA_URL=http://localhost:11434/api/chat
OLLAMA_MODEL=llama3.2
OLLAMA_API_KEY=
```

`OLLAMA_API_KEY` можно оставить пустым для обычного локального Ollama. Реальный `.env` не нужно коммитить: он игнорируется через `.gitignore`.

## Запуск

Установите зависимости:

```powershell
pip install requests
```

Запустите приложение:

```powershell
python expert_system.py
```

Для режима LLM должен быть запущен Ollama или совместимый API:

```powershell
ollama serve
```

## Как работает машина вывода

Машина вывода берет `DEFAULT_RULES` и входные факты из интерфейса. Промежуточные флаги не передаются во входе и не имеют стартовых значений. Они появляются во внутреннем состоянии только после применения `set_flags`.

Сначала система проверяет конфликты во входе, затем идет по правилам сверху вниз.

Если правило подходит, система:

- добавляет ID правила в `triggered_rules`;
- добавляет действия в `actions` без дублей;
- применяет `set_flags`;
- начинает проверку правил заново;
- останавливается, когда срабатывает правило с `final = true`.

Машина вывода не использует внешние знания и не интерпретирует смысл правил. Она строго сравнивает значения переменных и применяет описанные действия.

## Переменные

| Переменная | Тип | Возможные значения | Описание | Ограничения |
|---|---|---|---|---|
| `complaint_type` | Вход | `"primary"`, `"repeat"` | Тип жалобы: первичная или повторная. | Обязательное поле. |
| `violator_reaction` | Вход | `"contact"`, `"ignore"`, `"aggression"` | Реакция нарушителя. | Обязательное поле. |
| `vip_status` | Вход | `true`, `false` | Нарушитель имеет VIP-статус. | При `true` выселение и черный список запрещены. |
| `complainant_insists` | Вход | `true`, `false` | Жалобщик настаивает на немедленных действиях. | Усиливает эскалационные сценарии. |
| `settlement_success` | Вход | `true`, `false` | Шум урегулирован, жалобщик подтвердил тишину. | Допустимо только при `violator_reaction == "contact"`. Нельзя вместе с `refused_to_reduce_noise`, `repeated_ignore`, `refuses_to_leave`. |
| `repeated_ignore` | Вход | `true`, `false` | После предупреждения нарушитель снова игнорирует контакт. | Допустимо только при `violator_reaction == "ignore"`. |
| `refused_to_reduce_noise` | Вход | `true`, `false` | Нарушитель вступил в контакт, но отказался снизить шум. | Допустимо только при `violator_reaction == "contact"`. Нельзя вместе с `settlement_success`. |
| `refuses_to_leave` | Вход | `true`, `false` | Нарушитель отказывается покидать номер. | Допустимо только при агрессии, отказе снизить шум или повторном игноре. Нельзя вместе с `settlement_success`. |
| `warning_done` | Промежуточное | отсутствует, `true` | Выполнено устное предупреждение. | Не входит во вход. Выставляется правилами через `set_flags`. |
| `door_warning_done` | Промежуточное | отсутствует, `true` | Предупреждение зачитано через дверь. | Не входит во вход. Выставляется правилами при игноре. |
| `priority_raised` | Промежуточное | отсутствует, `true` | Приоритет кейса повышен. | Не входит во вход. Выставляется при повторных жалобах или критической эскалации. |
| `enhanced_settlement_done` | Промежуточное | отсутствует, `true` | Запущено усиленное урегулирование. | Не входит во вход. Выставляется при повторной жалобе без агрессии. |
| `police_called` | Промежуточное | отсутствует, `true` | Вызван наряд полиции. | Не входит во вход. Не должен появляться при `settlement_success == true`. |
| `eviction_escalation_started` | Промежуточное | отсутствует, `true` | Начата эскалация к возможному выселению. | Не входит во вход. Только для не-VIP. |
| `settlement_confirmed` | Промежуточное | отсутствует, `true` | Успешное урегулирование подтверждено. | Не входит во вход. Выставляется финальными правилами успеха. |
| `settlement_failed` | Промежуточное | отсутствует, `true` | Урегулирование провалилось. | Не входит во вход. Не должно выставляться вместе с `settlement_success == true`. |
| `vip_protocol_applied` | Промежуточное | отсутствует, `true` | Применен VIP-протокол. | Не входит во вход. Только для VIP-веток. |
| `eviction_completed` | Промежуточное | отсутствует, `true` | Выселение завершено. | Не входит во вход. Только для `vip_status == false`. |
| `morning_compliment_sent` | Промежуточное | отсутствует, `true` | Жалобщику запланирован или отправлен утренний комплимент. | Не входит во вход. Выставляется при успешном урегулировании. |
| `vip_manager_notified` | Промежуточное | отсутствует, `true` | Подключен менеджер по VIP-гостям. | Не входит во вход. Обычно только VIP-ветки. |
| `security_supervisor_notified` | Промежуточное | отсутствует, `true` | Подключен старший смены охраны. | Не входит во вход. Обычно не-VIP эскалации. |
| `guest_relocation_offered` | Промежуточное | отсутствует, `true` | Предложено переселение или альтернативное размещение. | Не входит во вход. Может быть для VIP и не-VIP. |
| `complainant_compensation_offered` | Промежуточное | отсутствует, `true` | Жалобщику предложена компенсация. | Не входит во вход. Часто при повторных жалобах и эскалациях. |
| `aggression_contained` | Промежуточное | отсутствует, `true` | Агрессивный сценарий локализован. | Не входит во вход. Выставляется при агрессии. |
| `access_restricted` | Промежуточное | отсутствует, `true` | Нарушителю ограничен доступ к услугам или зонам. | Не входит во вход. Только для не-VIP агрессии. |
| `monitoring_started` | Промежуточное | отсутствует, `true` | Кейс оставлен на контроле. | Не входит во вход. Выставляется финальными правилами мониторинга. |
| `case_closed` | Промежуточное | отсутствует, `true` | Кейс закрыт финальным решением. | Не входит во вход. Выставляется большинством финальных правил. |
| `triggered_rules` | Выход | список `id` правил | Какие правила реально сработали. | Только фактически примененные правила. |
| `actions` | Выход | список строк | Итоговый список действий. | Без дублей, в порядке применения правил. |
| `final` | Выход | `true`, `false` | Найдено ли финальное решение. | `true` только если сработало правило с `final = true`. |
| `final_decision` | Выход | строка или `null` | Название итогового решения. | Строка только при `final == true`, иначе `null`. |
| `missing_data` | Выход | список строк | Недостающие данные. | Обычно пустой, так как интерфейс передает все входные факты. |
| `conflict_detected` | Выход | `true`, `false` | Обнаружено противоречие во входе. | Например, `settlement_success=true` вместе с `refused_to_reduce_noise=true`. |
| `explanation` | Выход | строка | Краткое объяснение цепочки. | На русском, без домыслов. |

## Правила

| ID | Сценарий | Основные условия | Ключевые действия | Флаги | Финал |
|---|---|---|---|---|---|
| `R1` | Первичная жалоба, контакт, не-VIP | `primary`, `contact`, `vip_status=false` | Устное предупреждение, запись в журнал, подтверждение снижения громкости | `warning_done` | Нет |
| `R2` | Первичная жалоба, контакт, VIP | `primary`, `contact`, `vip_status=true` | VIP-менеджер, мягкое предупреждение, альтернатива VIP-гостю, комплимент жалобщику | `warning_done`, `vip_manager_notified`, `guest_relocation_offered`, `complainant_compensation_offered` | Нет |
| `R3` | Первичная жалоба, игнор, не-VIP | `primary`, `ignore`, `vip_status=false` | Охрана под дверь, предупреждение через дверь, журнал | `door_warning_done` | Нет |
| `R4` | Первичная жалоба, игнор, VIP | `primary`, `ignore`, `vip_status=true` | VIP-менеджер, звонок VIP-гостю, охрана без силового контакта, тихий номер жалобщику | `door_warning_done`, `vip_manager_notified`, `guest_relocation_offered`, `complainant_compensation_offered` | Нет |
| `R5` | Первичная агрессия, VIP | `primary`, `aggression`, `settlement_success=false`, `vip_status=true` | Полиция, изоляция зоны, директор/GM, VIP-размещение, компенсация жалобщику | `police_called`, `vip_protocol_applied`, `vip_manager_notified`, `aggression_contained`, `guest_relocation_offered`, `complainant_compensation_offered`, `case_closed` | `VIP-протокол при первичной агрессии` |
| `R6` | Первичная агрессия, не-VIP | `primary`, `aggression`, `settlement_success=false`, `vip_status=false` | Полиция, старший охраны, изоляция зоны, ограничение доступа, документы к выселению | `police_called`, `security_supervisor_notified`, `aggression_contained`, `access_restricted`, `eviction_escalation_started` | Нет |
| `R7` | Повторная агрессия, VIP | `repeat`, `aggression`, `settlement_success=false`, `vip_status=true` | Полиция, директор/GM, изоляция без выселения, VIP-размещение, компенсация жалобщику | `police_called`, `vip_protocol_applied`, `vip_manager_notified`, `aggression_contained`, `guest_relocation_offered`, `complainant_compensation_offered`, `case_closed` | `VIP-протокол при повторной агрессии` |
| `R8` | Повторная агрессия, не-VIP | `repeat`, `aggression`, `settlement_success=false`, `vip_status=false` | Критический приоритет, полиция, охрана, изоляция, подготовка к выселению | `priority_raised`, `police_called`, `security_supervisor_notified`, `aggression_contained`, `access_restricted`, `eviction_escalation_started` | Нет |
| `R9` | Повторная жалоба без агрессии, VIP | `repeat`, `contact/ignore`, `vip_status=true` | Повысить приоритет, VIP-менеджер, переселение/приватная зона, компенсация | `priority_raised`, `enhanced_settlement_done`, `vip_manager_notified`, `guest_relocation_offered`, `complainant_compensation_offered` | Нет |
| `R10` | Повторная жалоба без агрессии, не-VIP | `repeat`, `contact/ignore`, `vip_status=false` | Повысить приоритет, менеджер и охрана, переселение, компенсация | `priority_raised`, `enhanced_settlement_done`, `guest_relocation_offered`, `complainant_compensation_offered` | Нет |
| `R11` | Успешное первичное урегулирование, VIP | `primary`, `warning_done`, `contact`, `settlement_success=true`, `vip_status=true` | Подтвердить тишину, персональный комплимент, follow-up VIP-менеджера | `settlement_confirmed`, `morning_compliment_sent`, `vip_manager_notified`, `case_closed` | `VIP-урегулирование после первичного предупреждения` |
| `R12` | Успешное первичное урегулирование, не-VIP | `primary`, `warning_done`, `contact`, `settlement_success=true`, `vip_status=false` | Подтвердить тишину, комплимент утром | `settlement_confirmed`, `morning_compliment_sent`, `case_closed` | `Урегулирование после первичного предупреждения` |
| `R13` | Успешное повторное урегулирование, VIP | `repeat`, `enhanced_settlement_done`, `contact`, `settlement_success=true`, `vip_status=true` | Подтвердить тишину, персональный комплимент, мягкое напоминание VIP, follow-up | `settlement_confirmed`, `morning_compliment_sent`, `vip_manager_notified`, `case_closed` | `VIP-урегулирование после повторной жалобы` |
| `R14` | Успешное повторное урегулирование, не-VIP | `repeat`, `enhanced_settlement_done`, `contact`, `settlement_success=true`, `vip_status=false` | Комплимент утром, пометка в карточке нарушителя | `settlement_confirmed`, `morning_compliment_sent`, `case_closed` | `Успешное урегулирование после повторной жалобы` |
| `R15` | Отказ снизить шум, VIP | `contact`, `refused_to_reduce_noise=true`, `settlement_success=false`, `vip_status=true` | VIP-менеджер, президентский люкс/приватная зона, скидка, вино | `settlement_failed`, `vip_protocol_applied`, `vip_manager_notified`, `guest_relocation_offered`, `complainant_compensation_offered`, `case_closed` | `VIP-протокол после отказа снизить шум` |
| `R16` | Отказ снизить шум, не-VIP, жесткая эскалация | `contact`, `refused_to_reduce_noise=true`, `settlement_success=false`, `complainant_insists/refuses_to_leave`, `vip_status=false` | Охрана, полиция, предупреждение о выселении, компенсация | `police_called`, `settlement_failed`, `complainant_compensation_offered`, `eviction_escalation_started` | Нет |
| `R17` | Отказ снизить шум, не-VIP, мягкая эскалация | `contact`, `refused_to_reduce_noise=true`, `settlement_success=false`, без настаивания и отказа уйти, `vip_status=false` | Зафиксировать отказ, повторный контакт менеджера, контроль охраны, компенсация | `settlement_failed`, `security_supervisor_notified`, `complainant_compensation_offered`, `monitoring_started`, `case_closed` | `Мягкая эскалация после отказа снизить шум` |
| `R18` | Повторный игнор после предупреждения, VIP | `door_warning_done`, `repeated_ignore=true`, `settlement_success=false`, `vip_status=true` | GM/директор, отозвать охрану, VIP-зона/люкс, скидка, вино | `vip_protocol_applied`, `vip_manager_notified`, `guest_relocation_offered`, `complainant_compensation_offered`, `case_closed` | `VIP-протокол после повторного игнора` |
| `R19` | Повторный игнор, не-VIP, жесткая эскалация | `door_warning_done`, `repeated_ignore=true`, `settlement_success=false`, `complainant_insists/refuses_to_leave`, `vip_status=false` | Полиция, старший охраны, предупреждение о выселении, компенсация | `police_called`, `security_supervisor_notified`, `complainant_compensation_offered`, `eviction_escalation_started` | Нет |
| `R20` | Повторный игнор, не-VIP, контроль этажа | `door_warning_done`, `repeated_ignore=true`, `settlement_success=false`, без настаивания и отказа уйти, `vip_status=false` | Зафиксировать игнор, охрана на контроле, старший смены, компенсация | `security_supervisor_notified`, `complainant_compensation_offered`, `monitoring_started`, `case_closed` | `Контроль этажа после повторного игнора` |
| `R21` | Повторная жалоба с повторным игнором, VIP | `repeat`, `enhanced_settlement_done`, `ignore`, `repeated_ignore=true`, `settlement_success=false`, `vip_status=true` | GM/директор, отозвать охрану, связь через персонального менеджера, VIP-зона/люкс, скидка, вино | `vip_protocol_applied`, `vip_manager_notified`, `guest_relocation_offered`, `complainant_compensation_offered`, `case_closed` | `VIP-протокол при повторной жалобе с повторным игнором` |
| `R22` | Повторная жалоба с повторным игнором, не-VIP, жесткая эскалация | `repeat`, `enhanced_settlement_done`, `ignore`, `repeated_ignore=true`, `settlement_success=false`, `complainant_insists/refuses_to_leave`, `vip_status=false` | Полиция, старший охраны, предупреждение о выселении, компенсация | `police_called`, `security_supervisor_notified`, `complainant_compensation_offered`, `eviction_escalation_started` | Нет |
| `R23` | Повторная жалоба с повторным игнором, не-VIP, контроль | `repeat`, `enhanced_settlement_done`, `ignore`, `repeated_ignore=true`, `settlement_success=false`, без настаивания и отказа уйти, `vip_status=false` | Зафиксировать игнор, охрана на этаже, старший смены, компенсация | `security_supervisor_notified`, `complainant_compensation_offered`, `monitoring_started`, `case_closed` | `Контроль этажа после повторной жалобы с повторным игнором` |
| `R24` | Принудительное выселение не-VIP | `eviction_escalation_started=true`, `settlement_success=false`, `refuses_to_leave=true`, `vip_status=false` | Выселить, черный список, компенсация этажа | `eviction_completed`, `case_closed` | `Принудительное выселение не-VIP` |
| `R25` | Жесткая эскалация без выселения | `eviction_escalation_started=true`, `settlement_success=false`, `refuses_to_leave=false`, `vip_status=false` | Контроль охраны, передать управляющему, компенсация | `monitoring_started`, `complainant_compensation_offered`, `case_closed` | `Жесткая эскалация без принудительного выселения` |
| `R26` | Мониторинг после первичного контакта, VIP | `primary`, `warning_done`, `contact`, `settlement_success=false`, `refused_to_reduce_noise=false`, `vip_status=true` | VIP-контроль, звонок жалобщику, сохранить комплимент | `monitoring_started`, `vip_manager_notified`, `case_closed` | `VIP-предупреждение и мониторинг` |
| `R27` | Мониторинг после первичного контакта, не-VIP | `primary`, `warning_done`, `contact`, `settlement_success=false`, `refused_to_reduce_noise=false`, `vip_status=false` | Контроль администратора, звонок жалобщику | `monitoring_started`, `case_closed` | `Предупреждение и мониторинг` |
| `R28` | Мониторинг после первичного игнора, VIP | `primary`, `door_warning_done`, `ignore`, `repeated_ignore=false`, `vip_status=true` | VIP-контроль, связь без силового контакта, тихий номер жалобщику | `monitoring_started`, `vip_manager_notified`, `case_closed` | `VIP-мониторинг после первичного игнора` |
| `R29` | Мониторинг после первичного игнора, не-VIP | `primary`, `door_warning_done`, `ignore`, `repeated_ignore=false`, `vip_status=false` | Охрана на этаже, звонок жалобщику | `monitoring_started`, `case_closed` | `Контроль после предупреждения через дверь` |
| `R30` | Мониторинг после повторной жалобы с контактом, VIP | `repeat`, `enhanced_settlement_done`, `contact`, `settlement_success=false`, `refused_to_reduce_noise=false`, `vip_status=true` | VIP-контроль, тихий номер жалобщику, звонок | `monitoring_started`, `vip_manager_notified`, `case_closed` | `VIP-мониторинг после повторной жалобы` |
| `R31` | Мониторинг после повторной жалобы с контактом, не-VIP | `repeat`, `enhanced_settlement_done`, `contact`, `settlement_success=false`, `refused_to_reduce_noise=false`, `vip_status=false` | Контроль администратора, звонок, сохранить компенсацию | `monitoring_started`, `case_closed` | `Мониторинг после повторной жалобы` |
| `R32` | Мониторинг после повторной жалобы с игнором, VIP | `repeat`, `enhanced_settlement_done`, `ignore`, `repeated_ignore=false`, `vip_status=true` | VIP-контроль, связь через персонального менеджера, компенсация/переселение жалобщику | `monitoring_started`, `vip_manager_notified`, `case_closed` | `VIP-мониторинг после повторной жалобы с игнором` |
| `R33` | Мониторинг после повторной жалобы с игнором, не-VIP | `repeat`, `enhanced_settlement_done`, `ignore`, `repeated_ignore=false`, `vip_status=false` | Охрана на этаже, управляющий смены, компенсация | `monitoring_started`, `security_supervisor_notified`, `case_closed` | `Контроль после повторной жалобы с игнором` |
