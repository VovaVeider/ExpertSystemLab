import json
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

from llm_client import OllamaClient, load_env_file
from prompts import DEFAULT_SYSTEM_PROMPT
from rules import DEFAULT_INPUT, DEFAULT_RULES, INPUT_FIELD_LABELS


class OllamaExpertGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Экспертная система по жалобам на шум")
        self.root.geometry("1180x820")

        self.input_vars = {}
        self.response_raw = ""
        self.client_info = load_env_file()

        self.build_header()
        self.build_main_panel()
        self.apply_defaults()

    def build_header(self):
        header = tk.Frame(self.root)
        header.pack(fill="x", padx=12, pady=(12, 6))

        title = tk.Label(
            header,
            text="Экспертная система: жалобы на шум в отеле",
            font=("Arial", 16, "bold"),
        )
        title.pack(anchor="w")

        subtitle_text = (
            f"Модель: {self.client_info.get('OLLAMA_MODEL', 'не указана')}   |   "
            f"URL: {self.client_info.get('OLLAMA_URL', 'не указан')}"
        )
        subtitle = tk.Label(header, text=subtitle_text, fg="#555555")
        subtitle.pack(anchor="w", pady=(4, 0))

        hint = tk.Label(
            header,
            text="Отметьте факты по ситуации и нажмите «Выполнить вывод». Правила и системный промпт скрыты внутри программы.",
            fg="#333333",
        )
        hint.pack(anchor="w", pady=(6, 0))

    def build_main_panel(self):
        main = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        main.pack(fill="both", expand=True, padx=12, pady=12)

        left = tk.Frame(main)
        right = tk.Frame(main)
        main.add(left, stretch="always")
        main.add(right, stretch="always")

        self.build_input_panel(left)
        self.build_output_panel(right)

    def build_input_panel(self, parent):
        panel = tk.LabelFrame(parent, text="Входные данные", padx=10, pady=10)
        panel.pack(fill="both", expand=True)

        grid = tk.Frame(panel)
        grid.pack(fill="x")

        for index, (key, label_text) in enumerate(INPUT_FIELD_LABELS):
            var = tk.BooleanVar(value=bool(DEFAULT_INPUT.get(key, False)))
            self.input_vars[key] = var
            checkbox = tk.Checkbutton(
                grid,
                text=label_text,
                variable=var,
                anchor="w",
                justify="left",
                command=self.update_input_preview,
            )
            row = index // 2
            column = index % 2
            checkbox.grid(row=row, column=column, sticky="w", padx=(0, 24), pady=6)

        buttons = tk.Frame(panel)
        buttons.pack(fill="x", pady=(14, 8))

        self.send_btn = tk.Button(
            buttons,
            text="Выполнить вывод",
            width=20,
            command=self.send_request,
        )
        self.send_btn.pack(side="left")

        reset_btn = tk.Button(
            buttons,
            text="Сбросить форму",
            width=16,
            command=self.reset_form,
        )
        reset_btn.pack(side="left", padx=8)

        fill_case_btn = tk.Button(
            buttons,
            text="Пример: первичная жалоба",
            width=24,
            command=self.fill_example_case,
        )
        fill_case_btn.pack(side="left")

        self.status_label = tk.Label(panel, text="Готово", anchor="w")
        self.status_label.pack(fill="x", pady=(4, 0))

        debug_frame = tk.LabelFrame(panel, text="Сформированный JSON входа", padx=8, pady=8)
        debug_frame.pack(fill="both", expand=True, pady=(10, 0))

        self.input_preview = scrolledtext.ScrolledText(debug_frame, wrap=tk.WORD, height=12)
        self.input_preview.pack(fill="both", expand=True)
        self._make_text_copyable_readonly(self.input_preview)

    def build_output_panel(self, parent):
        panel = tk.LabelFrame(parent, text="Результат вывода", padx=10, pady=10)
        panel.pack(fill="both", expand=True)

        top = tk.Frame(panel)
        top.pack(fill="x", pady=(0, 10))
        top.grid_columnconfigure(1, weight=1)
        top.grid_rowconfigure(1, weight=1)

        tk.Label(top, text="Финальный результат:", font=("Arial", 11, "bold")).grid(
            row=0, column=0, sticky="w"
        )

        self.final_status_value = tk.Entry(top, font=("Arial", 12, "bold"))
        self.final_status_value.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self._make_entry_copyable_readonly(self.final_status_value)

        tk.Label(top, text="Итоговое решение:", font=("Arial", 11, "bold")).grid(
            row=1, column=0, sticky="nw", pady=(6, 0)
        )

        self.final_decision_value = scrolledtext.ScrolledText(top, wrap=tk.WORD, height=4)
        self.final_decision_value.grid(row=1, column=1, sticky="nsew", padx=(8, 0), pady=(6, 0))
        self._make_text_copyable_readonly(self.final_decision_value)

        copy_btn = tk.Button(top, text="Копировать всё", command=self.copy_all_results)
        copy_btn.grid(row=0, column=2, rowspan=2, padx=(12, 0), sticky="ne")

        lists_frame = tk.Frame(panel)
        lists_frame.pack(fill="both", expand=True)
        lists_frame.grid_columnconfigure(0, weight=1)
        lists_frame.grid_columnconfigure(1, weight=1)

        self.triggered_rules_text = self._create_text_block(lists_frame, "Сработавшие правила", 0, 0)
        self.actions_text = self._create_text_block(lists_frame, "Действия", 0, 1)
        self.missing_data_text = self._create_text_block(lists_frame, "Недостающие данные", 1, 0)
        self.explanation_text = self._create_text_block(lists_frame, "Пояснение", 1, 1)

        raw_frame = tk.LabelFrame(panel, text="Сырой ответ модели (JSON)", padx=8, pady=8)
        raw_frame.pack(fill="both", expand=True, pady=(10, 0))
        self.raw_response_text = scrolledtext.ScrolledText(raw_frame, wrap=tk.WORD, height=10)
        self.raw_response_text.pack(fill="both", expand=True)
        self._make_text_copyable_readonly(self.raw_response_text)

    def _create_text_block(self, parent, title, row, column):
        frame = tk.LabelFrame(parent, text=title, padx=8, pady=8)
        frame.grid(row=row, column=column, sticky="nsew", padx=4, pady=4)
        parent.grid_rowconfigure(row, weight=1)

        text_widget = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=8)
        text_widget.pack(fill="both", expand=True)
        self._make_text_copyable_readonly(text_widget)
        return text_widget

    @staticmethod
    def _make_text_copyable_readonly(widget):
        widget.bind("<Key>", lambda event: "break")
        widget.bind("<Control-v>", lambda event: "break")
        widget.bind("<Button-3>", lambda event: "break")

    @staticmethod
    def _make_entry_copyable_readonly(widget):
        widget.bind("<Key>", lambda event: "break")
        widget.bind("<Control-v>", lambda event: "break")
        widget.bind("<Button-3>", lambda event: "break")

    def apply_defaults(self):
        self.update_input_preview()
        self.clear_output()

    def set_status(self, text):
        self.status_label.config(text=text)

    def collect_input_data(self):
        data = dict(DEFAULT_INPUT)
        for key, var in self.input_vars.items():
            data[key] = bool(var.get())

        for flag_key in [
            "rule1_done", "rule2_done", "rule3_done", "rule4_done", "rule5_done",
            "rule6_done", "rule6_vip_done", "rule6_non_vip_done", "rule7_done",
            "rule8_done", "rule9_done", "rule10_done",
        ]:
            data[flag_key] = False
        return data

    def update_input_preview(self):
        payload = self.collect_input_data()
        self._set_text(self.input_preview, json.dumps(payload, ensure_ascii=False, indent=2))

    def reset_form(self):
        for key, _ in INPUT_FIELD_LABELS:
            self.input_vars[key].set(bool(DEFAULT_INPUT.get(key, False)))
        self.update_input_preview()
        self.clear_output()
        self.set_status("Форма сброшена")

    def fill_example_case(self):
        for key in self.input_vars:
            self.input_vars[key].set(False)
        self.input_vars["noise_complaint"].set(True)
        self.input_vars["primary_complaint"].set(True)
        self.input_vars["contact_reaction"].set(True)
        self.update_input_preview()
        self.clear_output()
        self.set_status("Подставлен пример первичной жалобы")

    def send_request(self):
        self.update_input_preview()
        input_data = self.collect_input_data()
        self.send_btn.config(state="disabled")
        self.set_status("Отправка запроса...")

        thread = threading.Thread(
            target=self._send_request_worker,
            args=(input_data,),
            daemon=True,
        )
        thread.start()

    def _send_request_worker(self, input_data):
        try:
            client = OllamaClient()
            content = client.send_expert_request(DEFAULT_RULES, input_data, DEFAULT_SYSTEM_PROMPT)
            self.root.after(0, self.show_response, content)
        except Exception as e:
            self.root.after(0, self.show_error, str(e))

    def show_response(self, content):
        self.response_raw = content
        parsed = self._parse_response_json(content)
        if parsed is None:
            self.show_error("Модель вернула ответ, но он не распознан как JSON")
            return

        self.render_output(parsed)
        self.send_btn.config(state="normal")
        self.set_status("Ответ получен")

    def show_error(self, error_text):
        self.send_btn.config(state="normal")
        self.set_status("Ошибка")
        messagebox.showerror("Ошибка запроса", error_text)

    def clear_output(self):
        self._set_entry_text(self.final_status_value, "—")
        self._set_text(self.final_decision_value, "—")

        for widget in [
            self.triggered_rules_text,
            self.actions_text,
            self.missing_data_text,
            self.explanation_text,
            self.raw_response_text,
        ]:
            self._set_text(widget, "")

    def render_output(self, parsed):
        self.clear_output()

        final = parsed.get("final", False)
        final_text = "Да" if final else "Нет"
        if parsed.get("conflict_detected"):
            final_text += " | Обнаружено противоречие"
        self._set_entry_text(self.final_status_value, final_text)

        decision = parsed.get("final_decision") or "Пока финального решения нет"
        self._set_text(self.final_decision_value, str(decision))

        self._set_text_list(self.triggered_rules_text, parsed.get("triggered_rules", []), empty_text="Нет")
        self._set_text_list(self.actions_text, parsed.get("actions", []), empty_text="Нет действий")
        self._set_text_list(self.missing_data_text, parsed.get("missing_data", []), empty_text="Недостающих данных нет")
        self._set_text(self.explanation_text, parsed.get("explanation", ""))
        self._set_text(self.raw_response_text, json.dumps(parsed, ensure_ascii=False, indent=2))

    @staticmethod
    def _set_entry_text(widget, text):
        widget.config(state="normal")
        widget.delete(0, tk.END)
        widget.insert(0, text or "—")
        widget.config(state="readonly")

    @staticmethod
    def _set_text(widget, text):
        widget.delete("1.0", tk.END)
        widget.insert("1.0", text or "—")

    def _set_text_list(self, widget, items, empty_text="—"):
        if not items:
            text = empty_text
        else:
            text = "\n".join(f"• {item}" for item in items)
        self._set_text(widget, text)

    def copy_all_results(self):
        text = (
            f"Финальный результат: {self.final_status_value.get()}\n\n"
            f"Итоговое решение:\n{self.final_decision_value.get('1.0', tk.END).strip()}\n\n"
            f"Сработавшие правила:\n{self.triggered_rules_text.get('1.0', tk.END).strip()}\n\n"
            f"Действия:\n{self.actions_text.get('1.0', tk.END).strip()}\n\n"
            f"Недостающие данные:\n{self.missing_data_text.get('1.0', tk.END).strip()}\n\n"
            f"Пояснение:\n{self.explanation_text.get('1.0', tk.END).strip()}\n\n"
            f"Сырой ответ модели:\n{self.raw_response_text.get('1.0', tk.END).strip()}"
        )
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.set_status("Результат скопирован")

    @staticmethod
    def _parse_response_json(raw):
        raw = (raw or "").strip()
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            start = raw.find("{")
            end = raw.rfind("}")
            if start == -1 or end == -1 or end <= start:
                return None
            try:
                return json.loads(raw[start:end + 1])
            except json.JSONDecodeError:
                return None