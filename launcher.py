import customtkinter
from tkinter import *
import psutil
import subprocess
import threading
import os
import psutil

class StatsFrame(customtkinter.CTkFrame):
    def __init__(self, master, title):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.title = title
        self.title = customtkinter.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=50, pady=(10, 0), sticky="ew")

        self.cpu_var = StringVar()
        self.cpu_label = customtkinter.CTkLabel(self, textvariable=self.cpu_var)
        self.cpu_label.grid(row=1, column=0)

        self.mem_var = StringVar()
        self.mem_label = customtkinter.CTkLabel(self, textvariable=self.mem_var)
        self.mem_label.grid(row=2, column=0)

        self.disk_var = StringVar()
        self.disk_label = customtkinter.CTkLabel(self, textvariable=self.disk_var)
        self.disk_label.grid(row=3, column=0)

    def update_cpu(self):
        cpu = psutil.cpu_percent()
        self.cpu_var.set(f"CPU: {cpu}%")

    def update_mem(self):
        mem = psutil.virtual_memory()[2]
        self.mem_var.set(f"Memory: {mem}%")
    
    def update_disk(self):
        disk = psutil.disk_usage('/')[3]
        self.disk_var.set(f"Disk: {disk}%")


class CommandLineFrame(customtkinter.CTkFrame):
    def __init__(self, master, title, proc):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.title = title
        self.title = customtkinter.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, columnspan=2, padx=50, sticky="nsew", pady=(10, 0))


        self.command_launcher = customtkinter.CTkTextbox(
            self, 
            width=1000,
            height=450)
        self.command_launcher.grid(row=1, column=0, sticky="w", padx=10, pady=10)

        self.launch_button = customtkinter.CTkButton(self, text="Launch Server", fg_color="green", hover_color="#00A36C", cursor="hand2", command=self.run_command)
        self.launch_button.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.stop_button = customtkinter.CTkButton(self, text="Stop Server", fg_color="red", hover_color="#C41E3A", cursor="hand2", command=self.stop_server)
        self.stop_button.grid(row=2, column=0, padx=10, pady=10, sticky="e")

        self.directory_input = customtkinter.CTkEntry(self, placeholder_text="D:\MinecraftServer - example path", width=300)
        self.directory_input.grid(row=2, column=0)

        self.proc = proc

    def run_command(self):
        directory = self.directory_input.get()
        file_name = "eula.txt"
        filepath = f'{directory}/{file_name}'
        self.running = True
        

        print(directory)
        with open(f'{filepath}', 'r') as file:
            eula_mod = file.read()
        
        # run a check to see if the text already exists
        if 'eula=true' not in eula_mod:
            # modify the file to agree to the eula
            
            eula_mod = eula_mod.replace('eula=false', 'eula=true')

            # open the file to write the mod into it
            with open(f"{filepath}", 'w') as file: # i could use r+ but it adds an extra e
                file.write(eula_mod)

        else:
            # dont make any change to the file, log to the console
            print("Text exists, skipping...")

        self.proc = subprocess.Popen(
            ["java", "-Xmx1024M", "-Xms1024M", "-jar", "server.jar"], #"nogui"
            stdout=subprocess.PIPE,
            cwd=directory
        )

        self.thread = threading.Thread(target=self.read_stdout, args=(directory,))
        self.thread.start()

    def stop_server(self):
        # Print message to indicate server is being stopped
        print("Stopping server!")
        
        # Set running variable to False
        self.running = False
        # Get process ID of server
        pid = self.find_process_id()
        # Check if valid process ID is found
        if pid:
            try:
                # Create a Process object with the process ID
                parent = psutil.Process(int(pid))
                # Get all child processes recursively
                children = parent.children(recursive=True)
                # Terminate each child process
                for child in children:
                    child.terminate()
                # Terminate the parent process
                parent.terminate()
            # Handle exception if process not found
            except psutil.NoSuchProcess:
                print("Process not found")
            
        
        # Print message if server process not found
        else:
            print("Server process not found")

    def find_process_id(self):
        # Iterate over all running processes
        for proc in psutil.process_iter(['pid', 'name']):
            
            # Check if process name is 'java.exe' and not the current process
            if proc.info['name'] == 'java.exe' and proc.info['pid'] != os.getpid():
                # Return the process ID
                return proc.info['pid']
        # Return None if no process is found
        return None
    
    def read_stdout(self, directory):
        while self.running:
            output = self.proc.stdout.readline()
            if output:
                output_text = output.decode()
                self.command_launcher.insert(END, output_text)
                #self.launch_button.configure(state=DISABLED)
                self.command_launcher.yview(END)
        
class SpeedTestFrame(customtkinter.CTkFrame):
    def __init__(self, master, title):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.title = title
        self.title = customtkinter.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=50,  pady=(10, 0), sticky="ew")


        self.speed_test = customtkinter.CTkTextbox(
            self, 
            width=400,
            height=100)
        self.speed_test.grid(row=1, column=0, sticky="w", padx=10, pady=10)

        #self.speed_button = customtkinter.CTkButton(self, text="Test Connection", command=self.run_command)
        #self.speed_button.grid(row=2, column=0, sticky="w")

        self.proc = None
        self.run_command()

    def run_command(self):
        # global proc - i would do this if there were no glasses to access global proc variable

        self.cmd = ["ping", "-t", "8.8.8.8"] # running the ping
        self.proc = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # start the process
        
        threading.Thread(target=self.read_stdout, args=(self.proc, self.speed_test)).start() # start the thread to read stdout

    def find_process_id(self):
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'java.exe' and proc.info['pid'] != os.getpid():
                return proc.info['pid']
        return None

    def read_stdout(self, proc, textbox):
        while True:
            output = self.proc.stdout.readline() # read line of output

            if output == '' and self.proc.poll() is not None: # check if process finished
                break
            
            if output: # if there is output
                self.speed_test.insert('end', output.decode('utf-8')) # insert it into the text box
                self.speed_test.yview(END)
            
        

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.proc = None
        self.title("Minecraft [Java] Server Launcher - minecraft_server.jar")
        self.geometry("800x757")
        self._set_appearance_mode("dark")
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        #self.grid_rowconfigure(0, weight=1)
        #self.grid_rowconfigure(1, weight=1)
        
        # frame one - CPU, MEM, DISK
        self.stats = StatsFrame(self, "Device Status")
        self.stats.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # frame two - command line frame
        self.commandlaunch = CommandLineFrame(self, "Minecraft Server Console", proc=self.proc)
        self.commandlaunch.grid(row=2, column=0, padx=10, pady=10, columnspan=2, sticky="nsew")

        # frame three - ping test
        self.speedtest = SpeedTestFrame(self, "Speed Test")
        self.speedtest.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")


        self.update_stats()
        
    def update_stats(self):
        self.stats.update_cpu()
        self.stats.update_mem()
        self.stats.update_disk()

        self.after(1000, self.update_stats)


if __name__ == "__main__":
    app = App()
    app.mainloop()