# backend.py

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority):
        self.pid = pid                       # Process ID
        self.arrival_time = arrival_time     # Arrival time of the process
        self.burst_time = burst_time         # Burst time required for execution
        self.priority = priority             # Priority of the process
        self.remaining_time = burst_time     # Remaining burst time initially set to burst time
        self.start_time = None               # Start time of execution (initialized later)
        self.completion_time = None          # Completion time of execution (initialized later)

def load_processes(file_path):
    """Load processes from a text file."""
    try:
        processes = []
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) == 4:
                    pid, arrival_time, burst_time, priority = map(int, parts)
                    processes.append(Process(pid, arrival_time, burst_time, priority))
                else:
                    raise ValueError(f"Format error in line: '{line.strip()}'")
        return processes
    except FileNotFoundError:
        raise RuntimeError("File not found.")
    except ValueError as ve:
        raise RuntimeError(f"Error parsing file: {ve}")
    except Exception as e:
        raise RuntimeError(f"Failed to load file: {e}")

def fcfs(processes):
    """First Come, First Served (FCFS) Scheduling Algorithm"""
    processes.sort(key=lambda x: x.arrival_time)
    time = 0
    for process in processes:
        if time < process.arrival_time:
            time = process.arrival_time
        process.start_time = time
        time += process.burst_time
        process.completion_time = time
    return processes

def sjf(processes):
    """Shortest Job First (SJF) Scheduling Algorithm"""
    time = 0
    completed_processes = []
    remaining_processes = processes[:]
    
    while remaining_processes:
        ready_queue = [p for p in remaining_processes if p.arrival_time <= time]
        if ready_queue:
            shortest_job = min(ready_queue, key=lambda x: x.burst_time)
            shortest_job_index = remaining_processes.index(shortest_job)
            process = remaining_processes.pop(shortest_job_index)
            process.start_time = time
            time += process.burst_time
            process.completion_time = time
            completed_processes.append(process)
        else:
            time += 1
    
    return completed_processes

def round_robin(processes, time_quantum):
    """Round Robin Scheduling Algorithm"""
    queue = processes[:]
    time = 0
    intervals = {process.pid: [] for process in processes}

    while queue:
        current_process = queue.pop(0)
        if current_process.arrival_time <= time:
            if current_process.remaining_time == current_process.burst_time:
                current_process.start_time = time if current_process.start_time is None else current_process.start_time
            
            if current_process.remaining_time <= time_quantum:
                intervals[current_process.pid].append((time, current_process.remaining_time))
                time += current_process.remaining_time
                current_process.remaining_time = 0
                current_process.completion_time = time
            else:
                intervals[current_process.pid].append((time, time_quantum))
                time += time_quantum
                current_process.remaining_time -= time_quantum
                queue.append(current_process)
        else:
            queue.append(current_process)
            time += 1

    return processes, intervals

def priority_scheduling(processes):
    """Priority Scheduling Algorithm"""
    time = 0
    completed_processes = []
    remaining_processes = processes[:]
    
    while remaining_processes:
        ready_queue = [p for p in remaining_processes if p.arrival_time <= time]
        if ready_queue:
            highest_priority = min(ready_queue, key=lambda x: x.priority)
            highest_priority_index = remaining_processes.index(highest_priority)
            process = remaining_processes.pop(highest_priority_index)
            if process.start_time is None:
                process.start_time = time
            time += process.burst_time
            process.completion_time = time
            completed_processes.append(process)
        else:
            time += 1
    
    return completed_processes

def multilevel_queue(processes, time_quantum_high=2, time_quantum_low=4):
    """Multilevel Queue Scheduling Algorithm with time quantum for high-priority queue"""
    high_priority_queue = [p for p in processes if p.priority < 5]
    low_priority_queue = [p for p in processes if p.priority >= 5]

    scheduled_processes = []

    # High-priority queue runs Round Robin with specified time quantum
    queue = high_priority_queue[:]
    time = 0
    while queue:
        current_process = queue.pop(0)
        if current_process.arrival_time <= time:
            if current_process.remaining_time == current_process.burst_time:
                current_process.start_time = time if current_process.start_time is None else current_process.start_time
            
            if current_process.remaining_time <= time_quantum_high:
                time += current_process.remaining_time
                current_process.remaining_time = 0
                current_process.completion_time = time
                scheduled_processes.append(current_process)
            else:
                time += time_quantum_high
                current_process.remaining_time -= time_quantum_high
                low_priority_queue.append(current_process)  # Move to low-priority queue if not finished
        else:
            queue.append(current_process)
            time += 1

    # Low-priority queue runs Round Robin with specified time quantum
    queue = low_priority_queue[:]
    while queue:
        current_process = queue.pop(0)
        if current_process.arrival_time <= time:
            if current_process.remaining_time == current_process.burst_time:
                current_process.start_time = time if current_process.start_time is None else current_process.start_time
            
            if current_process.remaining_time <= time_quantum_low:
                time += current_process.remaining_time
                current_process.remaining_time = 0
                current_process.completion_time = time
                scheduled_processes.append(current_process)
            else:
                time += time_quantum_low
                current_process.remaining_time -= time_quantum_low
                queue.append(current_process)
        else:
            queue.append(current_process)
            time += 1

    return scheduled_processes

def calculate_metrics(processes):
    """Calculate and return average turnaround time and average waiting time"""
    if not processes:
        return 0, 0  # Avoid division by zero
    total_turnaround_time = 0
    total_waiting_time = 0
    for process in processes:
        turnaround_time = process.completion_time - process.arrival_time
        waiting_time = turnaround_time - process.burst_time
        total_turnaround_time += turnaround_time
        total_waiting_time += waiting_time
    avg_turnaround_time = total_turnaround_time / len(processes)
    avg_waiting_time = total_waiting_time / len(processes)
    return avg_turnaround_time, avg_waiting_time

