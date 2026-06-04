from textual.widgets import Tree

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
