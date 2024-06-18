import os
import random
import re
import subprocess
import threading
from tkinter import *

import customtkinter
import mcrcon
import psutil
import socket

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
        self.mem_var.set(f"Remember: {mem}%")
    
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
        self.command_launcher.grid(row=1, column=0, sticky="w", padx=10, pady=5)

        self.command_entry = customtkinter.CTkEntry(self, placeholder_text="Help", width=1000, height=30)
        self.command_entry.grid(row=2, column=0, sticky="w", padx=10, pady=10)
        self.command_entry.bind("<Return>", lambda e: self.send_command()) # pressing enter will send the command

        self.launch_button = customtkinter.CTkButton(self, text="Launch Server", fg_color="green", hover_color="#00A36C", cursor="hand2", command=self.run_command)
        self.launch_button.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        self.stop_button = customtkinter.CTkButton(self, text="Stop Server", fg_color="red", hover_color="#C41E3A", cursor="hand2", command=self.stop_server)
        self.stop_button.grid(row=3, column=0, padx=10, pady=10, sticky="e")

        self.directory_input = customtkinter.CTkEntry(self, placeholder_text=r"D:\MinecraftServer - example path", width=300)
        self.directory_input.grid(row=3, column=0)
        self.directory_input.bind("<Return>", lambda e: self.run_command())

        self.proc = proc

    def send_command(self):
        directory = self.directory_input.get()
        file = "server.properties"
        self.name = socket.gethostname()
        self.host = socket.gethostbyname(self.name)
        self.port = int(25575)

        try:
            with open(f"{directory}/{file}") as file:
                properties = file.read()
            
            # re.search() should allow us to finding a matching regex pattern in a string
            # "rcon.password=(.*)" is the regex pattern, r is the raw string literal avoids having to escape backslash
            # rcon.passwords= matches the literal text "rcon.password="
            # (.*) matches any character after the rcon.password= and captures them into a group The .* will match the chars()
            # group(1) returns the contents
            pattern = r"rcon.password=(.*)"
            match = re.search(pattern, properties)
            if match:
                password = match.group(1)

                # create and connect to the MCRcon server
                rcon = mcrcon.MCRcon(self.host, password)
                rcon.connect()

                # send and retrieve response
                command = self.command_entry.get()
                response = rcon.command(command)

                # update the command launcher with the response
                self.command_launcher.insert(END, f">:{command} - {response}\n\n")
                # clear the entry
                self.command_entry.delete(0, END)
            else:
                raise ValueError("Password not found in server.properties file.")
            
        except mcrcon.MCRconException as error:
            print(f"{error}")

    def run_command(self):
        directory = self.directory_input.get()
        file_name = "eula.txt"
        filepath = f'{directory}/{file_name}'
        self.running = True

        rcon_file = "server.properties"
        rcon_path = f'{directory}/{rcon_file}'
        rcon_pwd = random.randint(1000, 9999)

        print(rcon_pwd)

        with open(f'{rcon_path}', 'r') as rconpass:
            properties = rconpass.read()
        if "rcon.password=" in properties:
            random_pass = rcon_pwd
            properties = properties.replace("rcon.password=", f"rcon.password={random_pass}")
        elif "rcon.password=" not in properties:
            properties += "\nrcon.password=" + random_pass
        with open(f"{rcon_path}", "w") as file:
            file.write(properties)

        with open(f'{rcon_path}', 'r') as rcon:
            rcon_enable = rcon.read()
        
        # check to see if its modified or not
        if 'enable-rcon=true' not in rcon_enable:
            # change it
            rcon_enable = rcon_enable.replace('enable-rcon=false', 'enable-rcon=true')

            # open the file and make the changes
            with open(f'{rcon_path}', 'w') as rcon:
                rcon.write(rcon_enable)
                rcon.close()
        else:
            print("Already Enabled")


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
            ["java", "-Xmx1024M", "-Xms1024M", "-jar", "server.jar", 'nogui'], #"nogui"
            stdout=subprocess.PIPE,
            cwd=directory
        )
        self.thread = threading.Thread(target=self.read_stdout, args=(directory,))
        self.thread.setDaemon(True)
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
        
        self.thread = threading.Thread(target=self.read_stdout, args=(self.proc, self.speed_test)) # start the thread to read stdout
        self.thread.daemon = True
        self.thread.start()

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
        self.hostname = socket.gethostname()
        self.ipaddr = socket.gethostbyname(self.hostname)

        self.title(f"Minecraft [Java] Server Manager: [ Expected File Name: server.jar ] ~ [ Device Address: {self.ipaddr} ]")
        self.geometry("870x800")
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
