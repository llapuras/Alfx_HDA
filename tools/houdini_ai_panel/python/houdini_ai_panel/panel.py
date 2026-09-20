"""PySide UI for the Houdini AI Assistant Python Panel."""

from __future__ import annotations

import re
import traceback

from . import context as scene_context
from .client import OpenAIChatClient
from .executor import run_hou_python
from .qt import QtCore, QtGui, QtWidgets, Signal, Slot


CODE_BLOCK_RE = re.compile(r"```(?:python|py)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)


def _html_escape(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
    )


class ChatWorker(QtCore.QObject):
    finished = Signal(str)
    failed = Signal(str)

    def __init__(self, message, context, history, parent=None):
        super(ChatWorker, self).__init__(parent)
        self.message = message
        self.context = context
        self.history = history

    @Slot()
    def run(self):
        try:
            reply = OpenAIChatClient().complete(self.message, self.context, self.history)
            self.finished.emit(reply)
        except Exception:
            self.failed.emit(traceback.format_exc())


class HoudiniAIPanel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(HoudiniAIPanel, self).__init__(parent)
        self.history = []
        self.pending_message = None
        self.current_thread = None
        self.current_worker = None

        self.setObjectName("houdini_ai_assistant_panel")
        self._build_ui()
        self.refresh_context()

    def _build_ui(self):
        self.chat_view = QtWidgets.QTextBrowser()
        self.chat_view.setOpenExternalLinks(True)

        self.context_view = QtWidgets.QPlainTextEdit()
        self.context_view.setReadOnly(True)
        self.context_view.setMaximumHeight(150)

        self.input_edit = QtWidgets.QPlainTextEdit()
        self.input_edit.setPlaceholderText("Ask about the current Houdini scene...")
        self.input_edit.setMaximumHeight(95)

        self.send_button = QtWidgets.QPushButton("Send")
        self.refresh_button = QtWidgets.QPushButton("Refresh Context")
        self.clear_button = QtWidgets.QPushButton("Clear")

        self.code_preview = QtWidgets.QPlainTextEdit()
        self.code_preview.setPlaceholderText("Python/HOM code from the assistant appears here before execution.")
        self.code_preview.setMinimumHeight(150)

        self.execute_button = QtWidgets.QPushButton("Execute Previewed Code")
        self.execute_button.setEnabled(False)
        self.execute_button.setToolTip("Runs only the code shown above, after creating a hip backup.")

        top_buttons = QtWidgets.QHBoxLayout()
        top_buttons.addWidget(self.refresh_button)
        top_buttons.addWidget(self.clear_button)
        top_buttons.addStretch(1)

        send_row = QtWidgets.QHBoxLayout()
        send_row.addWidget(self.input_edit, 1)
        send_row.addWidget(self.send_button)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(top_buttons)
        layout.addWidget(QtWidgets.QLabel("Context"))
        layout.addWidget(self.context_view)
        layout.addWidget(QtWidgets.QLabel("Chat"))
        layout.addWidget(self.chat_view, 1)
        layout.addLayout(send_row)
        layout.addWidget(QtWidgets.QLabel("Execution Preview"))
        layout.addWidget(self.code_preview)
        layout.addWidget(self.execute_button)

        self.send_button.clicked.connect(self.send_message)
        self.refresh_button.clicked.connect(self.refresh_context)
        self.clear_button.clicked.connect(self.clear_chat)
        self.execute_button.clicked.connect(self.confirm_and_execute)
        self.code_preview.textChanged.connect(self._update_execute_state)

        font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        self.context_view.setFont(font)
        self.code_preview.setFont(font)

    def append_chat(self, speaker, text):
        color = "#75a7ff" if speaker == "You" else "#b7f0c0"
        self.chat_view.append(
            '<p><b style="color:%s">%s</b><br>%s</p>' % (color, speaker, _html_escape(text))
        )

    def refresh_context(self):
        self.latest_context = scene_context.collect_prompt_context()
        import json

        self.context_view.setPlainText(json.dumps(self.latest_context, ensure_ascii=False, indent=2))

    def clear_chat(self):
        self.history = []
        self.chat_view.clear()
        self.code_preview.clear()

    def send_message(self):
        message = self.input_edit.toPlainText().strip()
        if not message or self.current_thread is not None:
            return

        self.refresh_context()
        self.input_edit.clear()
        self.pending_message = message
        self.append_chat("You", message)
        self.send_button.setEnabled(False)
        self.send_button.setText("Working...")

        self.current_thread = QtCore.QThread(self)
        self.current_worker = ChatWorker(message, self.latest_context, list(self.history))
        self.current_worker.moveToThread(self.current_thread)
        self.current_thread.started.connect(self.current_worker.run)
        self.current_worker.finished.connect(self._on_reply)
        self.current_worker.failed.connect(self._on_error)
        self.current_worker.finished.connect(self.current_thread.quit)
        self.current_worker.failed.connect(self.current_thread.quit)
        self.current_thread.finished.connect(self.current_worker.deleteLater)
        self.current_thread.finished.connect(self.current_thread.deleteLater)
        self.current_thread.finished.connect(self._thread_finished)
        self.current_thread.start()

    @Slot(str)
    def _on_reply(self, reply):
        self.append_chat("Assistant", reply)
        self.history.append({"role": "user", "content": self.pending_message or ""})
        self.history.append({"role": "assistant", "content": reply})
        self.pending_message = None
        self._set_code_from_reply(reply)

    @Slot(str)
    def _on_error(self, error):
        self.pending_message = None
        self.append_chat("Error", error)

    @Slot()
    def _thread_finished(self):
        self.current_thread = None
        self.current_worker = None
        self.send_button.setEnabled(True)
        self.send_button.setText("Send")

    def _set_code_from_reply(self, reply):
        match = CODE_BLOCK_RE.search(reply)
        if match:
            self.code_preview.setPlainText(match.group(1).strip())

    def _update_execute_state(self):
        self.execute_button.setEnabled(bool(self.code_preview.toPlainText().strip()))

    def confirm_and_execute(self):
        code = self.code_preview.toPlainText().strip()
        if not code:
            return

        result = QtWidgets.QMessageBox.question(
            self,
            "Execute Houdini Python",
            "This will save a hip backup, then run the previewed Python code in the current scene.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No,
        )
        if result != QtWidgets.QMessageBox.Yes:
            return

        exec_result = run_hou_python(code)
        if exec_result["ok"]:
            self.append_chat("System", "Executed successfully. Backup: %s" % exec_result["backup_path"])
            self.refresh_context()
        else:
            self.append_chat(
                "System",
                "Execution failed.\nBackup: %s\n\n%s"
                % (exec_result.get("backup_path"), exec_result.get("error")),
            )


def create_interface_root():
    return HoudiniAIPanel()
