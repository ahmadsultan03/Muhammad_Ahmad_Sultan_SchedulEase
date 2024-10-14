import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Backend import *

class SchedulingSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Process Scheduling Simulator")
        self.processes = []  # To store loaded processes
        self.processes_loaded = False  # Flag to track whether processes are loaded
        self.frame = None
        self.status_label = None
        self.processes_tree = None  # Treeview to display processes as a table
        self.metrics_text = None
        self.time_quantum_entry = None
        self.canvas = None  # To store the canvas widget
        
        self.create_widgets()

    def create_widgets(self):
        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.processes_label = ttk.Label(self.frame, text="Processes:")
        self.processes_label.grid(row=0, column=0, sticky=tk.W)

        # Create a Treeview widget to display processes as a table
        self.processes_tree = ttk.Treeview(self.frame, columns=("PID", "Arrival Time", "Burst Time", "Priority"), show="headings", height=10)
        self.processes_tree.heading("PID", text="PID")
        self.processes_tree.heading("Arrival Time", text="Arrival Time")
        self.processes_tree.heading("Burst Time", text="Burst Time")
        self.processes_tree.heading("Priority", text="Priority")
        self.processes_tree.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self.load_button = ttk.Button(self.frame, text="Load Processes", command=self.load_processes)
        self.load_button.grid(row=2, column=0, pady=5)

        # Buttons for scheduling algorithms (FCFS, SJF, RR, Priority)
        self.run_fcfs_button = ttk.Button(self.frame, text="Run FCFS Scheduling", command=lambda: self.run_algorithm(fcfs, "FCFS Scheduling"))
        self.run_fcfs_button.grid(row=3, column=0, pady=5)

        self.run_sjf_button = ttk.Button(self.frame, text="Run SJF Scheduling", command=lambda: self.run_algorithm(sjf, "SJF Scheduling"))
        self.run_sjf_button.grid(row=3, column=1, pady=5)

        self.run_rr_button = ttk.Button(self.frame, text="Run RR Scheduling", command=lambda: self.run_algorithm(round_robin, "Round Robin Scheduling"))
        self.run_rr_button.grid(row=4, column=0, pady=5)

        self.run_priority_button = ttk.Button(self.frame, text="Run Priority Scheduling", command=lambda: self.run_algorithm(priority_scheduling, "Priority Scheduling"))
        self.run_priority_button.grid(row=4, column=1, pady=5)

        self.run_multilevel_button = ttk.Button(self.frame, text="Run Multilevel Queue Scheduling", command=lambda: self.run_algorithm(lambda processes: multilevel_queue(processes, int(self.time_quantum_entry.get())), "Multilevel Queue Scheduling"))
        self.run_multilevel_button.grid(row=5, column=0, pady=5, columnspan=2)

        self.time_quantum_label = ttk.Label(self.frame, text="Time Quantum:")
        self.time_quantum_label.grid(row=6, column=0, sticky=tk.E)

        self.time_quantum_entry = ttk.Entry(self.frame)
        self.time_quantum_entry.grid(row=6, column=1, sticky=tk.W)
        self.time_quantum_entry.insert(0, "2")

        self.metrics_label = ttk.Label(self.frame, text="Metrics:")
        self.metrics_label.grid(row=7, column=0, sticky=tk.W)

        self.metrics_text = tk.Text(self.frame, height=5, width=40)
        self.metrics_text.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self.status_label = ttk.Label(self.frame, text="")
        self.status_label.grid(row=2, column=1, pady=5)

        self.stack_button = ttk.Button(self.frame, text="Display Stack", command=self.display_stack)
        self.stack_button.grid(row=9, column=0, pady=5, columnspan=2)

    def reset_processes(self, processes):
        for process in processes:
            process.remaining_time = process.burst_time
            process.start_time = None
            process.completion_time = None

    def load_processes(self):
        if self.processes_loaded:
            messagebox.showinfo("Processes Already Loaded", "Processes are already loaded.")
            return
        
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            try:
                self.processes = load_processes(file_path)
                self.update_processes_treeview()
                self.status_label.config(text="Processes loaded successfully.")
                self.processes_loaded = True  # Update flag
            except RuntimeError as e:
                messagebox.showerror("Error", str(e))
                self.status_label.config(text="Error loading processes.")

    def update_processes_treeview(self):
        # Clear existing items in the treeview
        for item in self.processes_tree.get_children():
            self.processes_tree.delete(item)
        
        # Insert loaded processes into the treeview
        for process in self.processes:
            self.processes_tree.insert("", tk.END, values=(process.pid, process.arrival_time, process.burst_time, process.priority))

    def display_stack(self):
        stack_text = ""
        for process in self.processes:
            stack_text += f"PID: {process.pid}, Arrival: {process.arrival_time}, Burst: {process.burst_time}, Priority: {process.priority}\n"
        messagebox.showinfo("Loaded Processes Stack", stack_text)

    def run_algorithm(self, algorithm_func, title):
        if not self.processes_loaded:
            messagebox.showwarning("No Processes", "Please load processes first.")
            return
        
        try:
            # Reset processes to their initial state before running the algorithm
            self.reset_processes(self.processes)
            
            if algorithm_func == round_robin:
                time_quantum = int(self.time_quantum_entry.get())
                scheduled_processes, intervals = algorithm_func(self.processes, time_quantum)
            else:
                scheduled_processes = algorithm_func(self.processes.copy())  # Ensure processes list is copied
                intervals = None

            if not scheduled_processes:
                messagebox.showwarning("No Processes Scheduled", "No processes were scheduled.")
                return
            
            fig = self.generate_gantt_chart(scheduled_processes, intervals, title)
            self.open_gantt_chart_window(fig, title)

            # Display metrics only after chart is displayed
            self.display_metrics(scheduled_processes)

        except ValueError as ve:
            messagebox.showerror("Value Error", f"Invalid value: {ve}")
        except RuntimeError as re:
            messagebox.showerror("Runtime Error", f"Error: {re}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run {title}: {e}")

    def generate_gantt_chart(self, processes, intervals, title):
        fig, gnt = plt.subplots()
        gnt.set_xlabel('Time')
        gnt.set_ylabel('Processes')
        gnt.set_title(title)

        # Define colors for processes or intervals
        colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
        color_index = 0
        color_map = {}

        try:
            if intervals:
                for pid, interval_list in intervals.items():
                    color = colors[color_index % len(colors)]
                    color_map[pid] = color
                    for start, duration in interval_list:
                        gnt.broken_barh([(start, duration)], (pid * 10, 9), facecolors=(color), label=f'PID {pid}')
                    color_index += 1
            else:
                for process in processes:
                    if process.start_time is not None and process.completion_time is not None:
                        color = colors[color_index % len(colors)]
                        color_map[process.pid] = color
                        gnt.broken_barh([(process.start_time, process.burst_time)], (process.pid * 10, 9), facecolors=(color), label=f'PID {process.pid}')
                        color_index += 1

            # Add legend
            handles = [plt.Rectangle((0,0),1,1, color=color_map[pid]) for pid in sorted(color_map.keys())]
            labels = [f'PID {pid}' for pid in sorted(color_map.keys())]
            gnt.legend(handles, labels, loc='upper right', bbox_to_anchor=(1.15, 1))

        except Exception as e:
            print(f"Error in generate_gantt_chart: {e}")
            raise  # Reraise the exception to see the full traceback

        return fig


    def open_gantt_chart_window(self, fig, title):
        chart_window = Toplevel(self.root)
        chart_window.title(title)
        chart_canvas = FigureCanvasTkAgg(fig, master=chart_window)
        chart_canvas.draw()
        chart_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def display_metrics(self, processes):
        avg_turnaround_time, avg_waiting_time = calculate_metrics(processes)
        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.insert(tk.END, f"Average Turnaround Time: {avg_turnaround_time:.2f}\n")
        self.metrics_text.insert(tk.END, f"Average Waiting Time: {avg_waiting_time:.2f}\n")

# Main entry point of the application
if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulingSimulatorApp(root)
    root.mainloop()
