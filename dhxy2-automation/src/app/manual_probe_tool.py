from __future__ import annotations

import json
import time
import tkinter as tk
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from tkinter import ttk

from PIL import Image, ImageTk

from src.app.window_binding import resolve_window_session
from src.executor import Win32SendInputGateway
from src.platform import PyWin32WindowGateway


def _utc_stamp() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%S%fZ")


def _slug(value: str) -> str:
    cleaned = [char.lower() if char.isalnum() else "-" for char in value.strip()]
    return "".join(cleaned).strip("-") or "manual-probe"


@dataclass(frozen=True)
class ManualProbeArtifacts:
    run_id: str
    handle: int
    client_x: int
    client_y: int
    screen_x: int
    screen_y: int
    before_path: str
    after_path: str
    before_hash: str
    after_hash: str
    frame_changed: bool
    delay_seconds: float
    label: str
    button_ref: str
    status: str = "pending_review"
    notes: str = ""


@dataclass(frozen=True)
class ButtonCalibrationEntry:
    group: str
    name: str
    button_ref: str
    label: str
    x: int
    y: int
    status: str
    notes: str

    @property
    def category(self) -> str:
        if self.group == "battle_command_bar":
            return "character_battle"
        if self.group == "pet_battle_command_bar":
            return "pet_battle"
        return "nonbattle"

    @property
    def section_label(self) -> str:
        if self.category == "character_battle":
            return "角色战斗指令"
        if self.category == "pet_battle":
            return "宠物战斗指令"
        return "非战斗界面"


class ManualCoordinateProbeService:
    def __init__(self, project_root: Path) -> None:
        self._project_root = Path(project_root)
        self._gateway = PyWin32WindowGateway()
        self._input_gateway = Win32SendInputGateway()

    def run_probe(
        self,
        client_x: int,
        client_y: int,
        label: str,
        button_ref: str,
        delay_seconds: float,
    ) -> ManualProbeArtifacts:
        session = resolve_window_session(
            self._project_root / "configs" / "accounts" / "instance-1.json",
            gateway=self._gateway,
        )
        session.focus()
        time.sleep(0.15)

        info = session.snapshot()
        before = session.capture_client()
        screen_x = info.client_rect.left + int(client_x)
        screen_y = info.client_rect.top + int(client_y)
        self._input_gateway.click_screen(screen_x, screen_y)
        time.sleep(max(0.0, float(delay_seconds)))
        after = session.capture_client()

        probe_dir = self._project_root / "runs" / "artifacts" / "probes" / "manual-coordinate-ui"
        probe_dir.mkdir(parents=True, exist_ok=True)
        run_id = _utc_stamp()
        safe_label = _slug(label or "manual-probe")
        before_path = probe_dir / f"{run_id}-{safe_label}-before.png"
        after_path = probe_dir / f"{run_id}-{safe_label}-after.png"
        before.image.save(before_path)
        after.image.save(after_path)

        artifacts = ManualProbeArtifacts(
            run_id=run_id,
            handle=info.handle,
            client_x=int(client_x),
            client_y=int(client_y),
            screen_x=screen_x,
            screen_y=screen_y,
            before_path=str(before_path),
            after_path=str(after_path),
            before_hash=before.frame_hash,
            after_hash=after.frame_hash,
            frame_changed=before.frame_hash != after.frame_hash,
            delay_seconds=float(delay_seconds),
            label=label,
            button_ref=button_ref,
        )
        self._write_record(artifacts)
        return artifacts

    def save_feedback(
        self,
        run_id: str,
        status: str,
        notes: str,
    ) -> Path:
        record_path = self.record_path_for(run_id)
        payload = json.loads(record_path.read_text(encoding="utf-8-sig"))
        payload["status"] = status
        payload["notes"] = notes
        payload["reviewed_at"] = _utc_stamp()
        record_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return record_path

    def record_path_for(self, run_id: str) -> Path:
        return self._project_root / "runs" / "artifacts" / "probes" / "manual-coordinate-ui" / f"{run_id}.json"

    def _write_record(self, artifacts: ManualProbeArtifacts) -> Path:
        record_path = self.record_path_for(artifacts.run_id)
        record_path.write_text(json.dumps(asdict(artifacts), ensure_ascii=False, indent=2), encoding="utf-8")
        return record_path


class ButtonCalibrationStore:
    def __init__(self, project_root: Path) -> None:
        self._path = Path(project_root) / "configs" / "ui" / "button-calibration.json"

    @property
    def path(self) -> Path:
        return self._path

    def load_entries(self) -> list[ButtonCalibrationEntry]:
        payload = json.loads(self._path.read_text(encoding="utf-8-sig"))
        entries: list[ButtonCalibrationEntry] = []
        for group_name, group_payload in payload.items():
            if group_name == "version":
                continue
            for button_name, button_payload in group_payload.get("buttons", {}).items():
                point = button_payload.get("point", [0, 0])
                entries.append(
                    ButtonCalibrationEntry(
                        group=group_name,
                        name=button_name,
                        button_ref=f"{group_name}.{button_name}",
                        label=str(button_payload.get("label", button_name)),
                        x=int(point[0]),
                        y=int(point[1]),
                        status=str(button_payload.get("status", "unknown")),
                        notes=str(button_payload.get("notes", "")),
                    )
                )
        entries.sort(key=lambda item: (item.category, item.group, item.y, item.x, item.label))
        return entries

    def load_entry(self, button_ref: str) -> ButtonCalibrationEntry:
        for entry in self.load_entries():
            if entry.button_ref == button_ref:
                return entry
        raise KeyError(f"unknown button_ref={button_ref}")

    def update_entry(
        self,
        button_ref: str,
        *,
        x: int,
        y: int,
        status: str,
        label: str | None = None,
    ) -> ButtonCalibrationEntry:
        payload = json.loads(self._path.read_text(encoding="utf-8-sig"))
        group_name, button_name = button_ref.split(".", 1)
        try:
            button_payload = payload[group_name]["buttons"][button_name]
        except KeyError as exc:
            raise KeyError(f"unknown button_ref={button_ref}") from exc

        button_payload["point"] = [int(x), int(y)]
        button_payload["status"] = str(status)
        if label is not None:
            cleaned_label = label.strip()
            if cleaned_label:
                button_payload["label"] = cleaned_label

        self._path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return self.load_entry(button_ref)


class ManualCoordinateProbeApp:
    STATUS_OPTIONS = ("confirmed", "candidate", "pending", "uncertain", "missed", "blocked")

    def __init__(
        self,
        root: tk.Tk,
        probe_service: ManualCoordinateProbeService,
        calibration_store: ButtonCalibrationStore,
    ) -> None:
        self._root = root
        self._probe_service = probe_service
        self._calibration_store = calibration_store
        self._last_run_id = ""
        self._selected_button_ref = ""

        self._entries_by_ref: dict[str, ButtonCalibrationEntry] = {}
        self._refs_by_category: dict[str, list[str]] = {
            "character_battle": [],
            "pet_battle": [],
            "nonbattle": [],
        }
        self._listboxes: dict[str, tk.Listbox] = {}

        self._button_ref_var = tk.StringVar(value="")
        self._button_name_var = tk.StringVar(value="")
        self._x_var = tk.StringVar(value="")
        self._y_var = tk.StringVar(value="")
        self._label_var = tk.StringVar(value="")
        self._delay_var = tk.StringVar(value="0.8")
        self._status_var = tk.StringVar(value="candidate")
        self._result_var = tk.StringVar(value="就绪")
        self._before_path_var = tk.StringVar(value="")
        self._after_path_var = tk.StringVar(value="")
        self._record_path_var = tk.StringVar(value="")
        self._config_path_var = tk.StringVar(value=str(self._calibration_store.path))
        self._summary_var = tk.StringVar(value="")

        self._notes_widget: tk.Text | None = None
        self._log_widget: tk.Text | None = None
        self._before_preview_label: ttk.Label | None = None
        self._after_preview_label: ttk.Label | None = None
        self._before_preview_image: ImageTk.PhotoImage | None = None
        self._after_preview_image: ImageTk.PhotoImage | None = None

        self._root.title("大话西游2 手工坐标探针")
        self._root.geometry("1280x780")
        self._root.minsize(1100, 700)

        self._build()
        self._append_log("INFO", f"工具已启动，配置文件：{self._calibration_store.path}")
        self._reload_entries()

    def _build(self) -> None:
        outer = ttk.Frame(self._root, padding=12)
        outer.pack(fill=tk.BOTH, expand=True)
        outer.columnconfigure(1, weight=1)
        outer.rowconfigure(2, weight=1)

        header = ttk.Frame(outer)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        header.columnconfigure(1, weight=1)
        ttk.Label(header, text="大话西游2 手工坐标探针", font=("Microsoft YaHei UI", 18, "bold")).grid(
            row=0,
            column=0,
            sticky="w",
        )
        ttk.Label(
            header,
            text="用于校准按钮坐标、执行一次点击、保存截图和人工判定结果。",
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Label(header, textvariable=self._summary_var).grid(row=0, column=1, sticky="e")

        toolbar = ttk.Frame(outer)
        toolbar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        ttk.Button(toolbar, text="刷新配置", command=self._reload_entries).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="保存坐标/状态", command=self._save_calibration).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(toolbar, text="点击并截图", command=self._run_probe).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(toolbar, text="保存判定", command=self._save_feedback).pack(side=tk.LEFT, padx=(8, 0))

        left_panel = ttk.Frame(outer)
        left_panel.grid(row=2, column=0, sticky="nsw", padx=(0, 16))
        left_panel.columnconfigure(0, weight=1)
        self._build_button_lists(left_panel)

        right_panel = ttk.Frame(outer)
        right_panel.grid(row=2, column=1, sticky="nsew")
        right_panel.columnconfigure(1, weight=1)
        right_panel.columnconfigure(2, weight=1)
        right_panel.rowconfigure(8, weight=1)
        right_panel.rowconfigure(9, weight=1)
        self._build_detail_panel(right_panel)

    def _build_button_lists(self, parent: ttk.Frame) -> None:
        specs = (
            ("character_battle", "角色战斗指令", 10),
            ("pet_battle", "宠物战斗指令", 6),
            ("nonbattle", "非战斗界面", 18),
        )
        for index, (category, title, height) in enumerate(specs):
            frame = ttk.LabelFrame(parent, text=title, padding=8)
            frame.grid(row=index, column=0, sticky="nsew", pady=(0 if index == 0 else 12, 0))
            listbox = tk.Listbox(frame, width=42, height=height)
            listbox.pack(fill=tk.BOTH, expand=True)
            listbox.bind("<<ListboxSelect>>", lambda _event, current=category: self._on_select_entry(current))
            self._listboxes[category] = listbox

    def _build_detail_panel(self, parent: ttk.Frame) -> None:
        self._add_readonly_entry(parent, 0, "配置文件", self._config_path_var)
        self._add_readonly_entry(parent, 1, "按钮引用", self._button_ref_var)
        self._add_readonly_entry(parent, 2, "分组/按钮", self._button_name_var)
        self._add_entry(parent, 3, "显示名称", self._label_var)
        self._add_entry(parent, 4, "Client X", self._x_var)
        self._add_entry(parent, 5, "Client Y", self._y_var)
        self._add_entry(parent, 6, "Delay", self._delay_var)

        ttk.Label(parent, text="有效状态").grid(row=7, column=0, sticky="w", pady=(6, 0))
        ttk.Combobox(
            parent,
            textvariable=self._status_var,
            values=self.STATUS_OPTIONS,
            state="readonly",
        ).grid(row=7, column=1, sticky="ew", pady=(6, 0))

        ttk.Label(parent, text="人工判定备注").grid(row=8, column=0, sticky="nw", pady=(8, 0))
        notes = tk.Text(parent, height=8, wrap=tk.WORD)
        notes.grid(row=8, column=1, sticky="nsew", pady=(8, 0))
        self._notes_widget = notes

        preview_frame = ttk.LabelFrame(parent, text="截图预览", padding=8)
        preview_frame.grid(row=8, column=2, rowspan=4, sticky="nsew", padx=(16, 0), pady=(8, 0))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.columnconfigure(1, weight=1)
        preview_frame.rowconfigure(1, weight=1)

        ttk.Label(preview_frame, text="Before").grid(row=0, column=0, sticky="w")
        ttk.Label(preview_frame, text="After").grid(row=0, column=1, sticky="w")
        self._before_preview_label = ttk.Label(preview_frame, text="暂无图片", anchor="center")
        self._before_preview_label.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        self._after_preview_label = ttk.Label(preview_frame, text="暂无图片", anchor="center")
        self._after_preview_label.grid(row=1, column=1, sticky="nsew")

        self._add_readonly_entry(parent, 9, "Before Image", self._before_path_var)
        self._add_readonly_entry(parent, 10, "After Image", self._after_path_var)
        self._add_readonly_entry(parent, 11, "Record", self._record_path_var)
        ttk.Label(
            parent,
            textvariable=self._result_var,
            foreground="#0a5",
            wraplength=720,
            justify=tk.LEFT,
        ).grid(row=12, column=0, columnspan=2, sticky="w", pady=(12, 0))

        log_frame = ttk.LabelFrame(parent, text="运行日志", padding=8)
        log_frame.grid(row=13, column=0, columnspan=3, sticky="nsew", pady=(16, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        log_widget = tk.Text(log_frame, height=12, wrap=tk.WORD, state="disabled")
        log_widget.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=log_widget.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        log_widget.configure(yscrollcommand=scrollbar.set)
        self._log_widget = log_widget

    def _add_entry(self, parent: ttk.Frame, row: int, label: str, variable: tk.StringVar) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=(6, 0))

    def _add_readonly_entry(self, parent: ttk.Frame, row: int, label: str, variable: tk.StringVar) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(parent, textvariable=variable, state="readonly").grid(row=row, column=1, sticky="ew", pady=(6, 0))

    def _reload_entries(self) -> None:
        entries = self._calibration_store.load_entries()
        self._entries_by_ref = {entry.button_ref: entry for entry in entries}
        for category in self._refs_by_category:
            self._refs_by_category[category] = [entry.button_ref for entry in entries if entry.category == category]
        for category, listbox in self._listboxes.items():
            self._populate_listbox(listbox, self._refs_by_category[category])

        self._summary_var.set(
            "角色战斗 "
            f"{len(self._refs_by_category['character_battle'])} | "
            f"宠物战斗 {len(self._refs_by_category['pet_battle'])} | "
            f"非战斗 {len(self._refs_by_category['nonbattle'])}"
        )
        self._append_log(
            "INFO",
            "已刷新校准配置："
            f"character_battle={len(self._refs_by_category['character_battle'])} "
            f"pet_battle={len(self._refs_by_category['pet_battle'])} "
            f"nonbattle={len(self._refs_by_category['nonbattle'])}",
        )

        if self._selected_button_ref in self._entries_by_ref:
            self._load_entry(self._entries_by_ref[self._selected_button_ref])
        elif entries:
            self._load_entry(entries[0])

    def _populate_listbox(self, listbox: tk.Listbox, refs: list[str]) -> None:
        listbox.delete(0, tk.END)
        for button_ref in refs:
            entry = self._entries_by_ref[button_ref]
            listbox.insert(tk.END, f"[{entry.status:<9}] {entry.label} ({entry.x}, {entry.y})")

    def _on_select_entry(self, category: str) -> None:
        source_listbox = self._listboxes[category]
        selected = source_listbox.curselection()
        if not selected:
            return

        for other_category, listbox in self._listboxes.items():
            if other_category != category:
                listbox.selection_clear(0, tk.END)

        refs = self._refs_by_category[category]
        self._load_entry(self._entries_by_ref[refs[selected[0]]])

    def _load_entry(self, entry: ButtonCalibrationEntry) -> None:
        self._selected_button_ref = entry.button_ref
        self._button_ref_var.set(entry.button_ref)
        self._button_name_var.set(f"{entry.section_label} / {entry.name}")
        self._x_var.set(str(entry.x))
        self._y_var.set(str(entry.y))
        self._label_var.set(entry.label)
        self._status_var.set(entry.status)
        if self._notes_widget is not None:
            self._notes_widget.delete("1.0", tk.END)
            if entry.notes:
                self._notes_widget.insert("1.0", entry.notes)
        self._result_var.set(f"已加载 {entry.button_ref}")
        self._append_log(
            "INFO",
            f"已选择 {entry.button_ref} label={entry.label} point=({entry.x}, {entry.y}) status={entry.status}",
        )

    def _selected_notes(self) -> str:
        if self._notes_widget is None:
            return ""
        return self._notes_widget.get("1.0", tk.END).strip()

    def _save_calibration(self) -> None:
        if not self._selected_button_ref:
            self._result_var.set("未选择按钮")
            self._append_log("WARN", "保存校准已跳过：未选择按钮")
            return

        try:
            saved = self._calibration_store.update_entry(
                self._selected_button_ref,
                x=int(self._x_var.get().strip()),
                y=int(self._y_var.get().strip()),
                status=self._status_var.get().strip(),
                label=self._label_var.get().strip(),
            )
        except Exception as exc:
            self._result_var.set(f"保存校准失败：{exc}")
            self._append_log("ERROR", f"保存校准失败：{exc}")
            return

        self._reload_entries()
        self._load_entry(saved)
        self._result_var.set(f"已保存 {saved.button_ref} -> ({saved.x}, {saved.y}) status={saved.status}")
        self._append_log("INFO", f"已保存校准：{saved.button_ref}")

    def _run_probe(self) -> None:
        try:
            artifacts = self._probe_service.run_probe(
                client_x=int(self._x_var.get().strip()),
                client_y=int(self._y_var.get().strip()),
                label=self._label_var.get().strip() or self._selected_button_ref or "manual-probe",
                button_ref=self._button_ref_var.get().strip(),
                delay_seconds=float(self._delay_var.get().strip() or "0.8"),
            )
        except Exception as exc:
            self._result_var.set(f"探针执行失败：{exc}")
            self._append_log("ERROR", f"探针执行失败：{exc}")
            return

        self._last_run_id = artifacts.run_id
        self._before_path_var.set(artifacts.before_path)
        self._after_path_var.set(artifacts.after_path)
        self._record_path_var.set(str(self._probe_service.record_path_for(artifacts.run_id)))
        self._update_image_previews(artifacts.before_path, artifacts.after_path)
        self._result_var.set(
            f"已生成 run={artifacts.run_id} frame_changed={artifacts.frame_changed} "
            f"screen=({artifacts.screen_x}, {artifacts.screen_y})"
        )
        self._append_log(
            "INFO",
            f"探针完成：run={artifacts.run_id} before={Path(artifacts.before_path).name} after={Path(artifacts.after_path).name}",
        )

    def _save_feedback(self) -> None:
        if not self._last_run_id:
            self._result_var.set("没有可保存的探针记录")
            self._append_log("WARN", "保存判定已跳过：当前没有探针记录")
            return

        try:
            record_path = self._probe_service.save_feedback(
                run_id=self._last_run_id,
                status=self._status_var.get().strip(),
                notes=self._selected_notes(),
            )
        except Exception as exc:
            self._result_var.set(f"保存判定失败：{exc}")
            self._append_log("ERROR", f"保存判定失败：{exc}")
            return

        self._record_path_var.set(str(record_path))
        self._result_var.set(f"已保存判定：{record_path.name}")
        self._append_log("INFO", f"已保存判定：run={self._last_run_id} status={self._status_var.get().strip()}")

    def _update_image_previews(self, before_path: str, after_path: str) -> None:
        self._before_preview_image = self._load_preview_image(before_path)
        self._after_preview_image = self._load_preview_image(after_path)
        self._set_preview(self._before_preview_label, self._before_preview_image, before_path)
        self._set_preview(self._after_preview_label, self._after_preview_image, after_path)

    def _load_preview_image(self, image_path: str) -> ImageTk.PhotoImage | None:
        path = Path(image_path)
        if not path.is_file():
            return None
        image = Image.open(path)
        image.thumbnail((320, 220))
        return ImageTk.PhotoImage(image)

    def _set_preview(
        self,
        label: ttk.Label | None,
        image: ImageTk.PhotoImage | None,
        image_path: str,
    ) -> None:
        if label is None:
            return
        if image is None:
            label.configure(image="", text="暂无图片")
            return
        label.configure(image=image, text=Path(image_path).name)

    def _append_log(self, level: str, message: str) -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{stamp}] {level}: {message}\n"
        if self._log_widget is None:
            return
        self._log_widget.configure(state="normal")
        self._log_widget.insert(tk.END, line)
        self._log_widget.see(tk.END)
        self._log_widget.configure(state="disabled")


def launch_manual_coordinate_probe(project_root: Path) -> None:
    root = tk.Tk()
    app = ManualCoordinateProbeApp(
        root=root,
        probe_service=ManualCoordinateProbeService(project_root),
        calibration_store=ButtonCalibrationStore(project_root),
    )
    _ = app
    root.mainloop()
