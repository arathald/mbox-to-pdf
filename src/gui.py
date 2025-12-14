"""
mbox-to-pdf: Convert Gmail Takeout mbox files to PDF

Main GUI application - 5-step wizard interface.
All business logic is in mbox_converter.py; this is presentation only.
"""

import os
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Callable, Dict, List, Optional

# Add parent directory to path for imports when running directly
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mbox_converter import convert_mbox_to_pdfs, parse_mbox, ConversionResult


class MboxToPdfApp:
    """Main application window with 5-step wizard flow."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("mbox-to-pdf Converter")
        self.root.geometry("700x500")
        self.root.minsize(600, 400)

        # Wizard state
        self.current_step = 1
        self.takeout_folder: Optional[Path] = None
        self.mbox_files: Dict[Path, tk.BooleanVar] = {}  # path -> selected
        self.mbox_counts: Dict[Path, int] = {}  # path -> email count
        self.grouping_strategy = tk.StringVar(value="month")
        self.output_folder: Optional[Path] = None
        self.conversion_result: Optional[ConversionResult] = None

        # Main container
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Show first step
        self.show_step_1()

    def clear_main_frame(self):
        """Clear all widgets from main frame."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def create_header(self, title: str, subtitle: str = ""):
        """Create step header with title and optional subtitle."""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        step_label = ttk.Label(
            header_frame,
            text=f"Step {self.current_step} of 5",
            font=("TkDefaultFont", 10),
            foreground="gray"
        )
        step_label.pack(anchor=tk.W)

        title_label = ttk.Label(
            header_frame,
            text=title,
            font=("TkDefaultFont", 16, "bold")
        )
        title_label.pack(anchor=tk.W)

        if subtitle:
            subtitle_label = ttk.Label(
                header_frame,
                text=subtitle,
                font=("TkDefaultFont", 10),
                foreground="gray"
            )
            subtitle_label.pack(anchor=tk.W, pady=(5, 0))

    def create_nav_buttons(
        self,
        back_callback: Optional[Callable] = None,
        next_callback: Optional[Callable] = None,
        next_text: str = "Next",
        next_enabled: bool = True
    ):
        """Create navigation buttons at bottom of step."""
        nav_frame = ttk.Frame(self.main_frame)
        nav_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(20, 0))

        if back_callback:
            back_btn = ttk.Button(nav_frame, text="Back", command=back_callback)
            back_btn.pack(side=tk.LEFT)

        if next_callback:
            next_btn = ttk.Button(
                nav_frame,
                text=next_text,
                command=next_callback,
                state=tk.NORMAL if next_enabled else tk.DISABLED
            )
            next_btn.pack(side=tk.RIGHT)
            self.next_button = next_btn

    # =========================================================================
    # Step 1: Folder Selection
    # =========================================================================

    def show_step_1(self):
        """Display folder selection step."""
        self.current_step = 1
        self.clear_main_frame()

        self.create_header(
            "Select Gmail Takeout Folder",
            "Choose the folder containing your Gmail Takeout export"
        )

        # Content area
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Folder selection
        folder_frame = ttk.Frame(content_frame)
        folder_frame.pack(fill=tk.X, pady=20)

        self.folder_var = tk.StringVar()
        folder_entry = ttk.Entry(
            folder_frame,
            textvariable=self.folder_var,
            state="readonly",
            width=50
        )
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        browse_btn = ttk.Button(
            folder_frame,
            text="Browse...",
            command=self.browse_folder
        )
        browse_btn.pack(side=tk.RIGHT)

        # Status area
        self.status_label = ttk.Label(content_frame, text="", foreground="gray")
        self.status_label.pack(anchor=tk.W, pady=10)

        # Navigation
        self.create_nav_buttons(
            next_callback=self.go_to_step_2,
            next_enabled=False
        )

    def browse_folder(self):
        """Open folder browser dialog."""
        folder = filedialog.askdirectory(
            title="Select Gmail Takeout Folder"
        )
        if folder:
            self.takeout_folder = Path(folder)
            self.folder_var.set(folder)
            self.scan_for_mbox_files()

    def scan_for_mbox_files(self):
        """Scan selected folder for .mbox files."""
        if not self.takeout_folder:
            return

        self.status_label.config(text="Scanning for .mbox files...")
        self.root.update()

        # Find all .mbox files
        mbox_files = list(self.takeout_folder.rglob("*.mbox"))

        if not mbox_files:
            self.status_label.config(
                text="No .mbox files found in this folder.",
                foreground="red"
            )
            self.next_button.config(state=tk.DISABLED)
            return

        # Initialize selection state (all selected by default)
        self.mbox_files = {f: tk.BooleanVar(value=True) for f in mbox_files}

        self.status_label.config(
            text=f"Found {len(mbox_files)} .mbox file(s)",
            foreground="green"
        )
        self.next_button.config(state=tk.NORMAL)

    def go_to_step_2(self):
        """Navigate to file selection step."""
        if not self.mbox_files:
            return
        self.show_step_2()

    # =========================================================================
    # Step 2: File Selection
    # =========================================================================

    def show_step_2(self):
        """Display file selection step with checkboxes."""
        self.current_step = 2
        self.clear_main_frame()

        self.create_header(
            "Select Files to Convert",
            "Uncheck any files you don't want to include"
        )

        # Scrollable file list
        list_frame = ttk.Frame(self.main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas with scrollbar
        canvas = tk.Canvas(list_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add checkboxes for each file
        for mbox_path, var in self.mbox_files.items():
            file_frame = ttk.Frame(scrollable_frame)
            file_frame.pack(fill=tk.X, pady=2)

            # Relative path for display
            try:
                display_path = mbox_path.relative_to(self.takeout_folder)
            except ValueError:
                display_path = mbox_path.name

            cb = ttk.Checkbutton(
                file_frame,
                text=str(display_path),
                variable=var
            )
            cb.pack(side=tk.LEFT)

            # Show email count if available
            if mbox_path in self.mbox_counts:
                count_label = ttk.Label(
                    file_frame,
                    text=f"({self.mbox_counts[mbox_path]} emails)",
                    foreground="gray"
                )
                count_label.pack(side=tk.LEFT, padx=(10, 0))

        # Navigation
        self.create_nav_buttons(
            back_callback=self.show_step_1,
            next_callback=self.go_to_step_3
        )

    def go_to_step_3(self):
        """Navigate to grouping selection step."""
        # Check at least one file is selected
        selected = [p for p, v in self.mbox_files.items() if v.get()]
        if not selected:
            messagebox.showwarning(
                "No Files Selected",
                "Please select at least one .mbox file to convert."
            )
            return
        self.show_step_3()

    # =========================================================================
    # Step 3: Grouping Strategy
    # =========================================================================

    def show_step_3(self):
        """Display grouping strategy selection."""
        self.current_step = 3
        self.clear_main_frame()

        self.create_header(
            "Choose Grouping Strategy",
            "How should emails be grouped into PDF files?"
        )

        # Content area
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=20)

        options = [
            ("month", "By Month", "One PDF per calendar month (e.g., 2008-01-January.pdf)"),
            ("quarter", "By Quarter", "One PDF per quarter (e.g., 2008-Q1.pdf)"),
            ("year", "By Year", "One PDF per year (e.g., 2008.pdf)")
        ]

        for value, label, description in options:
            option_frame = ttk.Frame(content_frame)
            option_frame.pack(fill=tk.X, pady=10)

            rb = ttk.Radiobutton(
                option_frame,
                text=label,
                value=value,
                variable=self.grouping_strategy
            )
            rb.pack(anchor=tk.W)

            desc_label = ttk.Label(
                option_frame,
                text=description,
                foreground="gray"
            )
            desc_label.pack(anchor=tk.W, padx=(25, 0))

        # Navigation
        self.create_nav_buttons(
            back_callback=self.show_step_2,
            next_callback=self.show_step_4
        )

    # =========================================================================
    # Step 4: Output Folder
    # =========================================================================

    def show_step_4(self):
        """Display output folder selection."""
        self.current_step = 4
        self.clear_main_frame()

        self.create_header(
            "Choose Output Folder",
            "Where should the PDF files be saved?"
        )

        # Content area
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Folder selection
        folder_frame = ttk.Frame(content_frame)
        folder_frame.pack(fill=tk.X, pady=20)

        self.output_var = tk.StringVar()
        if self.output_folder:
            self.output_var.set(str(self.output_folder))

        folder_entry = ttk.Entry(
            folder_frame,
            textvariable=self.output_var,
            state="readonly",
            width=50
        )
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        browse_btn = ttk.Button(
            folder_frame,
            text="Browse...",
            command=self.browse_output_folder
        )
        browse_btn.pack(side=tk.RIGHT)

        # Navigation
        self.create_nav_buttons(
            back_callback=self.show_step_3,
            next_callback=self.start_conversion,
            next_text="Convert",
            next_enabled=bool(self.output_folder)
        )

    def browse_output_folder(self):
        """Open output folder browser dialog."""
        folder = filedialog.askdirectory(
            title="Select Output Folder"
        )
        if folder:
            self.output_folder = Path(folder)
            self.output_var.set(folder)
            self.next_button.config(state=tk.NORMAL)

    # =========================================================================
    # Step 5: Conversion Progress
    # =========================================================================

    def start_conversion(self):
        """Start the conversion process."""
        if not self.output_folder:
            messagebox.showwarning(
                "No Output Folder",
                "Please select an output folder."
            )
            return

        self.show_step_5()

        # Run conversion in background thread
        thread = threading.Thread(target=self.run_conversion, daemon=True)
        thread.start()

    def show_step_5(self):
        """Display conversion progress."""
        self.current_step = 5
        self.clear_main_frame()

        self.create_header(
            "Converting...",
            "Please wait while your emails are converted to PDF"
        )

        # Progress area
        progress_frame = ttk.Frame(self.main_frame)
        progress_frame.pack(fill=tk.X, pady=20)

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode="determinate",
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X)

        self.progress_label = ttk.Label(
            progress_frame,
            text="Starting...",
            foreground="gray"
        )
        self.progress_label.pack(anchor=tk.W, pady=(10, 0))

        # Status text area
        self.status_text = tk.Text(
            self.main_frame,
            height=10,
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        self.status_text.pack(fill=tk.BOTH, expand=True, pady=10)

    def update_progress(self, current: int, total: int, message: str):
        """Update progress display (called from conversion thread)."""
        def update():
            self.progress_bar["value"] = current
            self.progress_label.config(text=message)
            self.append_status(message)

        self.root.after(0, update)

    def append_status(self, message: str):
        """Append message to status text area."""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)

    def run_conversion(self):
        """Run the actual conversion (in background thread)."""
        try:
            # Get selected files
            selected_files = [p for p, v in self.mbox_files.items() if v.get()]

            # Run conversion
            result = convert_mbox_to_pdfs(
                mbox_paths=selected_files,
                output_dir=self.output_folder,
                grouping_strategy=self.grouping_strategy.get(),
                progress_callback=self.update_progress
            )

            self.conversion_result = result

            # Show completion on main thread
            self.root.after(0, lambda: self.show_completion(result))

        except Exception as e:
            self.root.after(0, lambda: self.show_error(str(e)))

    def show_completion(self, result: ConversionResult):
        """Show conversion completion screen."""
        self.clear_main_frame()

        if result.success:
            self.create_header(
                "Conversion Complete!",
                f"Created {result.pdfs_created} PDF file(s) from {result.emails_processed} emails"
            )

            # Success message
            success_frame = ttk.Frame(self.main_frame)
            success_frame.pack(fill=tk.X, pady=20)

            ttk.Label(
                success_frame,
                text="Your emails have been converted to PDF.",
                font=("TkDefaultFont", 12)
            ).pack(anchor=tk.W)

            # Show created files
            if result.created_files:
                files_label = ttk.Label(
                    success_frame,
                    text="\nCreated files:",
                    font=("TkDefaultFont", 10, "bold")
                )
                files_label.pack(anchor=tk.W, pady=(20, 5))

                for file_path in result.created_files[:10]:  # Show first 10
                    ttk.Label(
                        success_frame,
                        text=f"  {Path(file_path).name}",
                        foreground="gray"
                    ).pack(anchor=tk.W)

                if len(result.created_files) > 10:
                    ttk.Label(
                        success_frame,
                        text=f"  ... and {len(result.created_files) - 10} more",
                        foreground="gray"
                    ).pack(anchor=tk.W)

        else:
            self.create_header(
                "Conversion Failed",
                "There were errors during conversion"
            )

        # Show errors if any
        if result.errors:
            errors_frame = ttk.Frame(self.main_frame)
            errors_frame.pack(fill=tk.BOTH, expand=True, pady=10)

            ttk.Label(
                errors_frame,
                text="Errors:",
                font=("TkDefaultFont", 10, "bold"),
                foreground="red"
            ).pack(anchor=tk.W)

            error_text = tk.Text(errors_frame, height=5, wrap=tk.WORD)
            error_text.pack(fill=tk.BOTH, expand=True)
            for error in result.errors:
                error_text.insert(tk.END, f"- {error}\n")
            error_text.config(state=tk.DISABLED)

        # Action buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(20, 0))

        if result.success and self.output_folder:
            open_btn = ttk.Button(
                button_frame,
                text="Open Output Folder",
                command=lambda: self.open_folder(self.output_folder)
            )
            open_btn.pack(side=tk.LEFT)

        close_btn = ttk.Button(
            button_frame,
            text="Close",
            command=self.root.quit
        )
        close_btn.pack(side=tk.RIGHT)

        new_btn = ttk.Button(
            button_frame,
            text="Convert Another",
            command=self.reset_wizard
        )
        new_btn.pack(side=tk.RIGHT, padx=(0, 10))

    def show_error(self, error_message: str):
        """Show error dialog."""
        messagebox.showerror("Conversion Error", error_message)
        self.show_step_4()  # Go back to allow retry

    def open_folder(self, folder: Path):
        """Open folder in system file manager."""
        if sys.platform == "darwin":
            subprocess.run(["open", str(folder)])
        elif sys.platform == "win32":
            subprocess.run(["explorer", str(folder)])
        else:
            subprocess.run(["xdg-open", str(folder)])

    def reset_wizard(self):
        """Reset wizard to start a new conversion."""
        self.takeout_folder = None
        self.mbox_files = {}
        self.mbox_counts = {}
        self.grouping_strategy.set("month")
        self.output_folder = None
        self.conversion_result = None
        self.show_step_1()


def main():
    """Application entry point."""
    root = tk.Tk()

    # Set app icon if available
    # root.iconbitmap("icon.ico")  # TODO: Add icon

    app = MboxToPdfApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
