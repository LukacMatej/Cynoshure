from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Tree, Label, Button, ContentSwitcher, Input
from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual import on
import subprocess
import json
import os

class Options(dict):
    """A simple dictionary subclass to hold SSH options."""
    def __init__(self, filepath="options.json"):
        super().__init__()
        self.filepath = filepath
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    super().update(json.load(f))
            except json.JSONDecodeError:
                pass
        self.setdefault("host", "N/A")
        self.setdefault("user", "N/A")
        self.setdefault("x11", False)
        self.setdefault("jump_host", "N/A")
        self.setdefault("port_forward", "N/A")

    def save(self):
        with open(self.filepath, "w") as f:
            json.dump(self, f, indent=4)

class HistoryStore(list):
    """A list subclass to manage connection history."""
    def __init__(self, filepath="history.json"):
        super().__init__()
        self.filepath = filepath
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    self.extend(json.load(f))
            except json.JSONDecodeError:
                pass

    def save(self):
        with open(self.filepath, "w") as f:
            json.dump(self, f, indent=4)

    def add_entry(self, entry):
        for existing in self:
            if existing.get("target") == entry.get("target"):
                return False
        self.append(entry)
        self.save()
        return True

    def remove_entry(self, target):
        for existing in self:
            if existing.get("target") == target:
                self.remove(existing)
                self.save()
                return True
        return False

class SessionStore(list):
    """A list subclass to manage saved sessions (favorites)."""
    def __init__(self, filepath="sessions.json"):
        super().__init__()
        self.filepath = filepath
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    self.extend(json.load(f))
            except json.JSONDecodeError:
                pass

    def save(self):
        with open(self.filepath, "w") as f:
            json.dump(self, f, indent=4)

    def add_entry(self, entry):
        for existing in self:
            if existing.get("target") == entry.get("target"):
                return False
        self.append(entry)
        self.save()
        return True
    
    def remove_entry(self, target):
        for existing in self:
            if existing.get("target") == target:
                self.remove(existing)
                self.save()
                return True
        return False

class PanelInput(Input):
    """Custom input that yields focus to the left panel when pressing left at the start."""
    def action_cursor_left(self) -> None:
        if self.cursor_position == 0:
            self.app.focus_left_panel()
        else:
            super().action_cursor_left()


class SSHManagerTree(Tree):
    """Custom tree that jumps to ssh-config when pressing down at the bottom."""
    def action_cursor_down(self) -> None:
        old_line = self.cursor_line
        super().action_cursor_down()
        if self.cursor_line == old_line:
            self.app.query_one("#ssh-config").focus()

class SSHConfigTree(Tree):
    """Custom tree that jumps to ssh-manager when pressing up at the top."""
    def action_cursor_up(self) -> None:
        old_line = self.cursor_line
        super().action_cursor_up()
        if self.cursor_line == old_line:
            self.app.query_one("#ssh-manager").focus()

class Cynoshure(App):
    """SSH Manager with an interactive Tree sidebar."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle Dark Mode"),
    ]

    CSS = """
    Screen {
        layout: horizontal;
    }
    #sidebar {
        width: 35%;
        border-right: solid;
    }
    #ssh-manager {
        height: auto;
        max-height: 70%;
    }
    #main-area {
        width: 65%;
        padding: 2;
        align: center middle;
    }
    .hidden {
        display: none;
    }
    Button {
        margin-top: 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Horizontal():
            with Vertical(id="sidebar"):
                yield SSHManagerTree("🛠️ SSH Manager", id="ssh-manager")
                yield SSHConfigTree("⚙️ SSH Configurations", id="ssh-config")
            # The right panel
            with Vertical(id="main-area"):
                with ContentSwitcher(initial="empty-view", id="main-switcher"):
                    with Vertical(id="empty-view"):
                        yield Label("Select an item from the tree to see details...")
                    with Vertical(id="quick-connect-view"):
                        yield Label("[bold cyan]Quick Connect[/bold cyan]\n\nEnter the host address to connect:")
                        yield PanelInput(placeholder="e.g. user@192.168.1.50 or 10.0.0.5", id="quick-connect-input")
                        with Horizontal():
                            yield Button("Connect", id="btn-quick-connect", variant="success")
                            yield Button("Favorite", id="btn-quick-favorite", variant="primary")
                    with Vertical(id="connection-view"):
                        yield Label("", id="info-label")
                        with Horizontal():
                            yield Button("Connect via SSH", id="btn-connect", variant="success")
                            yield Button("Delete", id="btn-quick-delete", variant="error")
                    with Vertical(id="config-view"):
                        yield Label("", id="config-label")
                        yield PanelInput(placeholder="Enter new value...", id="config-input")
                        with Horizontal():
                            yield Button("Save", id="btn-save")
                            yield Button("Default", id="btn-default", variant="warning")
                
        yield Footer()

    def focus_right_panel(self) -> None:
        """Move focus to the first focusable widget in the right panel."""
        switcher = self.query_one("#main-switcher", ContentSwitcher)
        if switcher.current:
            current_view = self.query_one(f"#{switcher.current}")
            for widget in current_view.walk_children():
                if isinstance(widget, Input):
                    widget.focus()
                    return
            for widget in current_view.walk_children():
                if isinstance(widget, Button):
                    widget.focus()
                    return

    def focus_left_panel(self) -> None:
        """Move focus back to the currently active or default tree."""
        switcher = self.query_one("#main-switcher", ContentSwitcher)
        if switcher.current == "config-view":
            self.query_one("#ssh-config").focus()
        else:
            self.query_one("#ssh-manager").focus()

    def on_key(self, event: Key) -> None:
        if event.key == "left" and isinstance(self.focused, Button):
            self.focus_left_panel()

    def action_switch_panel(self) -> None:
        """Toggle focus between the left tree and the right panel."""
        if isinstance(self.focused, Tree):
            self.focus_right_panel()
        else:
            self.focus_left_panel()

    def on_mount(self) -> None:
        """Called when the app starts. We populate the tree here."""
        self.options = Options()
        self.history = HistoryStore()
        self.sessions = SessionStore()
        tree = self.query_one("#ssh-manager", Tree)
        tree_options = self.query_one("#ssh-config", Tree)
        tree.root.expand()
        tree_options.root.expand()

        # SSH Connections Section
        connections = tree.root.add("🔗 SSH Connections", expand=True)
        connections.add_leaf("⚡ Quick Connect", {"quick_connect": True})
        # 1. Create the 'Sessions' (Favorites) branch
        self.sessions_node = connections.add("⭐ Sessions", expand=True)
        for item in self.sessions:
            self.sessions_node.add_leaf(
                f"⭐ {item['target']}", 
                {
                    "target": item["target"], 
                    "host": item.get("host", "N/A"), 
                    "user": item.get("user", "N/A"), 
                    "x11": item.get("x11", False),
                    "jump_host": item.get("jump_host", "N/A"),
                    "port_forward": item.get("port_forward", "N/A")
                }
            )

        # 2. Create the 'History' branch
        self.history_node = connections.add("🕒 History")
        for item in self.history:
            self.add_history_to_tree(item)

        # SSH Configurations Section
        configs = tree_options.root.add("⚙️ SSH Configurations", expand=True)
        key_configs = configs.add("🔑 Key Configurations")
        key_configs.add_leaf("🔑 Path to Key", {"config_key": "key_path"})
        settings = configs.add("🌍 SSH Settings")
        settings.add_leaf("👤 Username", {"config_key": "user"})
        settings.add_leaf("✅ X11 Forwarding", {"config_key": "x11"})
        settings.add_leaf("🦘 Jump Host", {"config_key": "jump_host"})
        settings.add_leaf("🔌 Port Forwarding", {"config_key": "port_forward"})

    def add_history_to_tree(self, item: dict) -> None:
        node = self.history_node.add(item["target"])
        node.add_leaf("🚀 Connect", {
            "history_action": "connect",
            "target": item["target"],
            "host": item.get("host", "N/A"),
            "user": item.get("user", "N/A"),
            "x11": item.get("x11", False),
            "jump_host": item.get("jump_host", "N/A"),
            "port_forward": item.get("port_forward", "N/A")
        })
        node.add_leaf("⭐ Favorite", {
            "history_action": "favorite",
            "target": item["target"],
            "host": item.get("host", "N/A"),
            "user": item.get("user", "N/A"),
            "x11": item.get("x11", False),
            "jump_host": item.get("jump_host", "N/A"),
            "port_forward": item.get("port_forward", "N/A")
        })
        node.add_leaf("❌ Delete", {
            "history_action": "delete",
            "target": item["target"]
        })

    def record_history(self, host: str, user: str, x11: bool, target: str, jump_host: str = "N/A", port_forward: str = "N/A") -> None:
        entry = {
            "target": target,
            "host": host,
            "user": user,
            "x11": x11,
            "jump_host": jump_host,
            "port_forward": port_forward
        }
        if self.history.add_entry(entry):
            self.add_history_to_tree(entry)

    def add_session(self, host: str, user: str, x11: bool, target: str, jump_host: str = "N/A", port_forward: str = "N/A") -> None:
        entry = {
            "target": target,
            "host": host,
            "user": user,
            "x11": x11,
            "jump_host": jump_host,
            "port_forward": port_forward
        }
        if self.sessions.add_entry(entry):
            self.sessions_node.add_leaf(f"⭐ {target}", {"target": target, "host": host, "user": user, "x11": x11, "jump_host": jump_host, "port_forward": port_forward})

    def _run_ssh(self, host: str, user: str, x11: bool, jump_host: str = "N/A", port_forward: str = "N/A") -> None:
        """Helper method to construct and run the SSH command."""
        key_path = self.options.get("key_path")
        if host and host != "N/A":
            cmd = ["ssh"]
            if x11:
                cmd.append("-X")
            if jump_host and jump_host != "N/A":
                cmd.extend(["-J", jump_host])
            if port_forward and port_forward != "N/A":
                cmd.extend(["-L", port_forward])
            if key_path and str(key_path).strip() and str(key_path).strip() != "N/A":
                cmd.extend(["-i", str(key_path).strip()])

            target = f"{user}@{host}" if user and user != "N/A" else host
            cmd.append(target)
            
            self.record_history(host, user, x11, target, jump_host, port_forward)

            # Suspend the Textual App to yield terminal control to SSH
            with self.suspend():
                print(f"\n🚀 Connecting to {target}...\n")
                subprocess.run(cmd)
                input("\nPress Enter to return to Cynoshure...")

    @on(Tree.NodeSelected)
    def handle_node_selection(self, event: Tree.NodeSelected) -> None:
        """Fired when the user presses Enter or clicks a tree node."""
        switcher = self.query_one("#main-switcher", ContentSwitcher)

        # Only update the right panel if it's a server (a leaf), not a folder
        if not event.node.children:
            # Retrieve the dictionary we attached to the node in on_mount
            data = event.node.data or {}
            
            if event.control.id == "ssh-manager":
                if data.get("quick_connect"):
                    switcher.current = "quick-connect-view"
                elif data.get("history_action") == "connect":
                    user_val = data.get('user', 'N/A')
                    host_val = data.get('host', 'N/A')
                    x11_val = data.get('x11', False)
                    jump_val = data.get('jump_host', 'N/A')
                    port_val = data.get('port_forward', 'N/A')
                    self._run_ssh(host_val, user_val, x11_val, jump_val, port_val)
                elif data.get("history_action") == "delete":
                    self.history.remove_entry(data.get("target"))
                    if event.node.parent:
                        event.node.parent.remove()
                    switcher.current = "empty-view"
                elif data.get("history_action") == "favorite":
                    user_val = data.get('user', 'N/A')
                    host_val = data.get('host', 'N/A')
                    x11_val = data.get('x11', False)
                    jump_val = data.get('jump_host', 'N/A')
                    port_val = data.get('port_forward', 'N/A')
                    target_val = data.get('target')
                    self.add_session(host_val, user_val, x11_val, target_val, jump_val, port_val)
                else:
                    info_label = self.query_one("#info-label", Label)
                    
                    # Fallback to the global settings if the selected leaf doesn't specify its own
                    user_val = data.get('user') if 'user' in data else self.options.get('user', 'N/A')
                    host_val = data.get('host') if 'host' in data else self.options.get('host', 'N/A')
                    x11_val = data.get('x11') if 'x11' in data else self.options.get('x11', False)
                    jump_val = data.get('jump_host') if 'jump_host' in data else self.options.get('jump_host', 'N/A')
                    port_val = data.get('port_forward') if 'port_forward' in data else self.options.get('port_forward', 'N/A')

                    # Save the resolved config for the connect button to use
                    self.current_connection = {
                        "target": data.get("target", str(event.node.label).replace("⭐ ", "")),
                        "host": host_val,
                        "user": user_val,
                        "x11": x11_val,
                        "jump_host": jump_val,
                        "port_forward": port_val
                    }
                    self.current_connection_node = event.node

                    info_label.update(
                        f"[bold cyan]Selected Server:[/bold cyan] {event.node.label}\n\n"
                        f"👤 [bold]User:[/bold] {user_val}\n"
                        f"🖥️  [bold]Host:[/bold] {host_val}\n"
                        f"🪟 [bold]X11 Forwarding:[/bold] {'Enabled' if x11_val else 'Disabled'}\n"
                        f"🦘 [bold]Jump Host:[/bold] {jump_val}\n"
                        f"🔌 [bold]Port Forward:[/bold] {port_val}"
                    )
                    switcher.current = "connection-view"
            elif event.control.id == "ssh-config":
                self.current_config_key = data.get("config_key")
                self.current_config_node = event.node
                config_label = self.query_one("#config-label", Label)
                config_label.update(
                    f"[bold magenta]Configuration:[/bold magenta] {event.node.label}\n\n"
                    f"🔧 Adjust the settings for {event.node.label} here.\n\n"
                    f"Current global value: {self.options.get(self.current_config_key, 'N/A')}"
                )
                self.query_one("#config-input", Input).value = str(self.options.get(self.current_config_key, ""))
                switcher.current = "config-view"
        else:
            switcher.current = "empty-view"
            
        # The tree automatically toggles expansion on click, so we don't need to code that!

    @on(Button.Pressed, "#btn-save")
    def save_configuration(self, event: Button.Pressed) -> None:
        """Save the input value to the global options."""
        if hasattr(self, 'current_config_key') and self.current_config_key:
            new_value = self.query_one("#config-input", Input).value
            
            # Special handling for boolean config values like x11
            if self.current_config_key == "x11":
                self.options[self.current_config_key] = new_value.lower() in ("true", "1", "yes", "y")
            else:
                self.options[self.current_config_key] = new_value
                
            self.options.save()

            config_label = self.query_one("#config-label", Label)
            config_label.update(
                f"[bold magenta]Configuration:[/bold magenta] {self.current_config_node.label}\n\n"
                f"🔧 Adjust the settings for {self.current_config_node.label} here.\n\n"
                f"Current global value: {self.options.get(self.current_config_key, 'N/A')}"
            )

    @on(Button.Pressed, "#btn-default")
    def default_configuration(self, event: Button.Pressed) -> None:
        """Reset the option to its default state, preventing it from being used in SSH connections."""
        if hasattr(self, 'current_config_key') and self.current_config_key:
            if self.current_config_key == "x11":
                self.options[self.current_config_key] = False
            else:
                self.options[self.current_config_key] = "N/A"
                
            self.options.save()

            config_label = self.query_one("#config-label", Label)
            config_label.update(
                f"[bold magenta]Configuration:[/bold magenta] {self.current_config_node.label}\n\n"
                f"🔧 Adjust the settings for {self.current_config_node.label} here.\n\n"
                f"Current global value: {self.options.get(self.current_config_key, 'N/A')}"
            )
            self.query_one("#config-input", Input).value = str(self.options.get(self.current_config_key, ""))

    @on(Button.Pressed, "#btn-connect")
    def connect_to_ssh(self, event: Button.Pressed) -> None:
        """Execute the SSH connection using the configured settings."""
        if hasattr(self, 'current_connection'):
            host = self.current_connection.get("host")
            user = self.current_connection.get("user")
            x11 = self.current_connection.get("x11")
            jump_host = self.current_connection.get("jump_host", "N/A")
            port_forward = self.current_connection.get("port_forward", "N/A")
            self._run_ssh(host, user, x11, jump_host, port_forward)

    @on(Button.Pressed, "#btn-quick-connect")
    def quick_connect_to_ssh(self, event: Button.Pressed) -> None:
        """Execute a quick SSH connection from the input field."""
        target = self.query_one("#quick-connect-input", Input).value.strip()
        if not target:
            return

        x11 = self.options.get("x11", False)
        jump_host = self.options.get("jump_host", "N/A")
        port_forward = self.options.get("port_forward", "N/A")
        
        user_val = "N/A"
        host_val = target
        if "@" in target:
            user_val, host_val = target.split("@", 1)
        self._run_ssh(host_val, user_val, x11, jump_host, port_forward)

    @on(Button.Pressed, "#btn-quick-favorite")
    def quick_favorite_connection(self, event: Button.Pressed) -> None:
        """Add the current quick connect target to Sessions."""
        target = self.query_one("#quick-connect-input", Input).value.strip()
        if not target:
            return

        x11 = self.options.get("x11", False)
        jump_host = self.options.get("jump_host", "N/A")
        port_forward = self.options.get("port_forward", "N/A")
        
        user_val = "N/A"
        host_val = target
        if "@" in target:
            user_val, host_val = target.split("@", 1)
            
        self.add_session(host_val, user_val, x11, target, jump_host, port_forward)
        self.query_one("#quick-connect-input", Input).value = ""

    @on(Button.Pressed, "#btn-quick-delete")
    def delete_favorite_connection(self, event: Button.Pressed) -> None:
        """Delete the selected session."""
        if hasattr(self, 'current_connection') and hasattr(self, 'current_connection_node'):
            target = self.current_connection.get("target")
            if target:
                self.sessions.remove_entry(target)
                self.current_connection_node.remove()
                self.query_one("#main-switcher", ContentSwitcher).current = "empty-view"

if __name__ == "__main__":
    app = Cynoshure()
    app.run()