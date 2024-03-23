import tkinter as tk
from typing import Tuple
import customtkinter as ctk
import ijson as ij
from customtkinter import *
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
import json
import re
import tkintermapview as tkmap
import gc


FontManager.load_font("fonts/OpenSans.ttf")

ctk.set_default_color_theme("dark-blue")

class Application(CTk):
    def __init__(self):
        super().__init__()

        self.default_font = CTkFont(family="Open Sans", size=20)
        self.title("Log in")
        self.resizable(False, False)

        with open("key.key", "rb") as key_file:
            self.key = key_file.read()
        self.password_strength = 0
        
        self.log_in_frame = CTkFrame(master=self, corner_radius=0)
        self.registration_frame = CTkFrame(master=self, corner_radius=0)
        self.map_frame = CTkFrame(master=self, corner_radius=0)

        # Images
        self.closed_eye_image = CTkImage(light_image=Image.open("images/closed_eye.png"), size=(26, 26))
        self.opened_eye_image = CTkImage(light_image=Image.open("images/opened_eye.png"), size=(26, 26))

        # Log in page
        self.login_input_box = CTkEntry(self.log_in_frame, placeholder_text="Login (nickname)", border_color="black",
                                        corner_radius=28, width=280, height=56, font=self.default_font)
        self.password_input_box = CTkEntry(self.log_in_frame, placeholder_text="Password", border_color="black",
                                           corner_radius=28, width=280, height=56, font=self.default_font, show="*")
        
        self.show_password_button = CTkButton(self.password_input_box, width=10, height=10, corner_radius=5, text="",
                                              image=self.closed_eye_image, fg_color="transparent", hover=False)
        self.show_password_button.place(relx=0.94, rely=0.5, anchor="e")
        self.show_password_button.bind("<ButtonPress-1>", self.show_hide_password)
        self.show_password_button.bind("<ButtonRelease-1>", self.show_hide_password)

        self.log_in_button = CTkButton(self.log_in_frame, text="Log in", width=280, height=56, corner_radius=28,
                                        font=self.default_font, command=self.log_in_button_click)
        self.no_account_button = CTkButton(self.log_in_frame, text="No account?", width=280, height=56, corner_radius=28,
                                        font=self.default_font, command=self.go_to_registration)
        
        self.login_input_box.pack(pady=10)
        self.password_input_box.pack()
        self.log_in_button.pack(pady=10)
        self.no_account_button.pack()
        
        # Registration page
        self.back_button_image = CTkImage(light_image=Image.open("images/back_arrow.png"), size=(20, 20))
        self.back_button = CTkButton(self.registration_frame, text="", font=self.default_font, width=20, height=20,
        image=self.back_button_image, fg_color="transparent", hover_color="#DAD9D8", command=self.go_to_log_in)
        self.back_button.pack(anchor="ne")

        CTkLabel(self.registration_frame, width=280, anchor="w", text="Email", padx=30).pack()
        self.email_input_box = CTkEntry(self.registration_frame, placeholder_text="email@gmail.com", border_color="black",
                                        corner_radius=28, width=280, height=56, font=self.default_font)
        self.email_input_box.pack(pady=(0, 10))

        CTkLabel(self.registration_frame, width=280, anchor="w", text="Nickname", padx=30).pack()
        self.nickname_input_box = CTkEntry(self.registration_frame, placeholder_text="nickname", border_color="black",
                                           corner_radius=28, width=280, height=56, font=self.default_font)
        self.nickname_input_box.pack(pady=(0,10))
        self.nickname_input_box.bind("<Key>", self.prevent_space)
        
        CTkLabel(self.registration_frame, width=280, anchor="w", text="Password", padx=30).pack()
        self.new_password_input_box = CTkEntry(self.registration_frame, border_color="black",
                                               corner_radius=28, width=280, height=56, font=self.default_font, show="*")
        self.new_password_input_box.pack(pady=(0,10))
        self.new_password_input_box.bind("<KeyRelease>", self.new_password_text_change)
        self.new_password_input_box.bind("<Key>", self.prevent_space)

        self.show_password_button = CTkButton(self.new_password_input_box, width=10, height=10, corner_radius=5, text="",
                                              image=self.closed_eye_image, fg_color="transparent", hover=False)
        self.show_password_button.place(relx=0.94, rely=0.5, anchor="e")
        self.show_password_button.bind("<ButtonPress-1>", self.show_hide_password)
        self.show_password_button.bind("<ButtonRelease-1>", self.show_hide_password)
        
        CTkLabel(self.registration_frame, width=280, anchor="w", text="Repeat password", padx=30).pack()
        self.repeat_password_input_box = CTkEntry(self.registration_frame, border_color="black",
                                                  corner_radius=28, width=280, height=56, font=self.default_font, show="*")
        self.repeat_password_input_box.pack()
        self.show_password_button = CTkButton(self.repeat_password_input_box, width=10, height=10, corner_radius=5, text="",
                                              image=self.closed_eye_image, fg_color="transparent", hover=False)
        self.show_password_button.place(relx=0.94, rely=0.5, anchor="e")
        self.show_password_button.bind("<ButtonPress-1>", self.show_hide_password)
        self.show_password_button.bind("<ButtonRelease-1>", self.show_hide_password)
        
        
        self.password_safety_progress_bar = CTkProgressBar(self.registration_frame, width=250, height=10, corner_radius=10,
                                                           progress_color="#8B0000")
        self.password_safety_progress_bar.pack(pady=15)
        self.password_safety_progress_bar.set(0.0)        

        self.sign_up_button = CTkButton(self.registration_frame, text="Sign up", font=self.default_font, width=280, height=56,
                                        corner_radius=28, command=self.sign_up_button_click)
        self.sign_up_button.pack()

        # Map page
        self.user_information_label = CTkLabel(self.map_frame)
        self.back_button = CTkButton(self.map_frame, text="", font=self.default_font, width=20, height=20,
        image=self.back_button_image, fg_color="transparent", hover_color="#DAD9D8", command=self.go_to_log_in)
        
        self.user_information_label.pack(anchor="w", padx=20)
        self.back_button.pack(anchor="e", padx=20)
        

        self.log_in_frame.pack(fill=BOTH, expand=True, ipadx=20, ipady=20)

    def show_hide_image(self, marker):
        marker.hide_image(not marker.image_hidden)

    def go_to_registration(self):
        self.title("Sign up")
        self.log_in_frame.pack_forget()
        self.registration_frame.pack(fill=BOTH, expand=True, ipadx=20, ipady=20)
        self.is_password_visible = False

    def go_to_log_in(self):
        self.title("Log in")
        if self.map_frame.winfo_ismapped():
            self.map.destroy()
            self.map_frame.pack_forget()
            gc.collect()
        else:
            self.registration_frame.pack_forget()

        self.log_in_frame.pack(fill=BOTH, expand=True, ipadx=20, ipady=20)
        self.is_password_visible = False

    def go_to_map(self, user_information:str):

        self.map = tkmap.TkinterMapView(self.map_frame, width=800, height=800) #, use_database_only=True, database_path="map_tiles.db"
        self.map.set_address("Запоріжжя, Україна", marker=True, text="Запоріжжя")        
        self.map.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga")
        self.map.set_zoom(14)
        self.map.max_zoom = 15
        self.map.min_zoom = 10

        self.oak_marker = self.map.set_marker(47.87119, 34.99924, text="700-річний дуб", image_zoom_visibility=(12, 15),
                                       image=ImageTk.PhotoImage(Image.open("images/oak.jpg").resize((320, 240))), command=self.show_hide_image)
        self.power_station_marker = self.map.set_marker(47.8685, 35.0889, text="Дніпровська ГЕС", image_zoom_visibility=(12, 15),
                                       image=ImageTk.PhotoImage(Image.open("images/power_station.jpg").resize((320, 240))), command=self.show_hide_image)
        
        self.oak_marker.hide_image(True)
        self.power_station_marker.hide_image(True)
        self.map.pack()

        self.log_in_button.configure(text="Log in")
        self.title("Zaporizhia sights")
        self.user_information_label.configure(text=user_information)
        self.log_in_frame.pack_forget()
        self.map_frame.pack(fill=BOTH, expand=True)

    def show_hide_password(self, event):
        button = event.widget.master
        input_box = button.master
        if event.type == "4":
            button.configure(image=self.opened_eye_image)
            input_box.configure(show="")
        elif event.type == "5":
            button.configure(image=self.closed_eye_image)
            input_box.configure(show="*")

    def sign_up_button_click(self):
        for child in self.registration_frame.winfo_children():
            if isinstance(child, CTkEntry):
                child.configure(border_color="black")

        is_error = False

        if not bool(re.match(r"[^@]+(@gmail.com|@yahoo.com|ukr.net)\Z", self.email_input_box.get())):
            is_error = True
            self.email_input_box.configure(border_color="red")
        if self.nickname_input_box.get() == "":
            is_error = True
            self.nickname_input_box.configure(border_color="red")
        if self.new_password_input_box.get() != self.repeat_password_input_box.get():
            is_error = True
            self.repeat_password_input_box.configure(border_color="red")
        if self.password_strength < 25:
            is_error = True
            self.new_password_input_box.configure(border_color="red")
        

        if is_error: return

        coder = Fernet(self.key)

        new_user = {
            "email": coder.encrypt(self.email_input_box.get().encode()).decode(),
            "nickname": coder.encrypt(self.nickname_input_box.get().encode()).decode(),
            "password": coder.encrypt(self.new_password_input_box.get().encode()).decode()
        }
        
        with open("users.json", "r+") as users_file:
            users_data = json.load(users_file)

            for user in users_data["users"]:
                if coder.decrypt(user["nickname"]).decode() == self.nickname_input_box.get() or coder.decrypt(user["email"]).decode() == self.email_input_box.get():
                    self.sign_up_button.configure(text="User already exists!")
                    self.after(1000, self.return_text_and_change_page)
                    return
        
            users_data["users"].append(new_user)
            users_file.seek(0)

            json.dump(users_data, users_file, indent=4)
        
        self.sign_up_button.configure(text="Success!")
        self.after(1000, self.return_text_and_change_page)

    def return_text_and_change_page(self):
        self.sign_up_button.configure(text="Sign up")
        self.go_to_log_in()

    def log_in_button_click(self):

        coder = Fernet(self.key)

        with open("users.json", "r") as users_file:
            users_data = ij.items(users_file, "users.item")
            for user in users_data:
                if coder.decrypt(user["nickname"]).decode() == self.login_input_box.get() and coder.decrypt(user["password"]).decode() == self.password_input_box.get():
                    self.log_in_button.configure(text="Authorized")
                    self.after(1000, lambda: self.go_to_map(f"{coder.decrypt(user["nickname"]).decode()}({coder.decrypt(user["email"]).decode()})"))
                    return
        self.log_in_button.configure(text="Wrong credentials")
        self.after(1000, lambda: self.log_in_button.configure(text="Log in"))

    def new_password_text_change(self, event):
        password_strength = 0
        if event.char == " ":
            return "break"
        if len(self.new_password_input_box.get()) >= 8:
            password_strength += 25
            if bool(re.search(r"\d", self.new_password_input_box.get())):
                password_strength += 25
            if bool(re.search(r"(\W|\_)", self.new_password_input_box.get())):
                password_strength += 25
            if bool(re.search(r"[A-Z]", self.new_password_input_box.get())):
                password_strength += 25
        
        color = "#8B0000"
        if  25 < password_strength <= 50:
            color = "#FF4500"
        elif 50 < password_strength <= 75:
            color = "#90EE90"
        elif password_strength > 75:
            color = "#006400"

        self.password_strength = password_strength
        self.password_safety_progress_bar.configure(progress_color=color)
        self.password_safety_progress_bar.set(password_strength/100)
    
    def prevent_space(self, event):
        if event.char == " ":
            return "break"


app = Application()
app.mainloop()