import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import pyperclip
from password_manager import (
    generate_key_from_password,
    hash_master_password,
    verify_master_password,
    encrypt_text,
    decrypt_text,
    load_passwords,
    save_passwords_to_file,
    save_master_password,
    load_master_password
)

class PasswordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")

        self.master_password = None
        self.master_key = None

        self.check_master_password()

        if self.master_password:
            # Username
            tk.Label(root, text="Username:").grid(row=0, column=0, padx=10, pady=10)
            self.username_entry = tk.Entry(root)
            self.username_entry.grid(row=0, column=1, padx=10, pady=10)

            # Password
            tk.Label(root, text="Password:").grid(row=1, column=0, padx=10, pady=10)
            self.password_entry = tk.Entry(root, show='*')
            self.password_entry.grid(row=1, column=1, padx=10, pady=10)

            # Buttons
            self.save_button = tk.Button(root, text="Save", command=self.save_password)
            self.save_button.grid(row=2, column=0, columnspan=2, pady=10)

            self.view_button = tk.Button(root, text="View Saved Passwords", command=self.view_passwords)
            self.view_button.grid(row=3, column=0, columnspan=2, pady=10)

            self.passwords = load_passwords()
        else:
            messagebox.showerror("Error", "Failed to set master password. Exiting...")
            root.quit()

    def check_master_password(self):
        stored_master_password = load_master_password()
        if stored_master_password:
            # Prompt user for master password
            self.master_password = simpledialog.askstring("Master Password", "Enter your master password:", show='*')
            if verify_master_password(stored_master_password, self.master_password):
                self.master_key = generate_key_from_password(self.master_password)
            else:
                messagebox.showerror("Error", "Incorrect master password")
                self.root.quit()
        else:
            # No master password set, prompt to create one
            self.master_password = simpledialog.askstring("Master Password", "Create a master password:", show='*')
            confirm_password = simpledialog.askstring("Confirm Password", "Confirm your master password:", show='*')
            if self.master_password == confirm_password:
                hashed_master_password = hash_master_password(self.master_password)
                save_master_password(hashed_master_password)
                self.master_key = generate_key_from_password(self.master_password)
            else:
                messagebox.showerror("Error", "Passwords do not match")
                self.root.quit()

    def save_password(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username and password:
            encrypted_username = encrypt_text(username, self.master_key)
            encrypted_password = encrypt_text(password, self.master_key)
            self.passwords[encrypted_username] = encrypted_password
            save_passwords_to_file(self.passwords)
            messagebox.showinfo("Success", "Password saved successfully!")
        else:
            messagebox.showwarning("Input Error", "Please enter both username and password.")

    def view_passwords(self):
        view_window = tk.Toplevel(self.root)
        view_window.title("Saved Passwords")

        tree = ttk.Treeview(view_window, columns=("Username", "Password"), show='headings')
        tree.heading("Username", text="Username")
        tree.heading("Password", text="Password")
        tree.pack(fill=tk.BOTH, expand=True)

        for encrypted_username, encrypted_password in self.passwords.items():
            try:
                decrypted_username = decrypt_text(encrypted_username, self.master_key)
                decrypted_password = decrypt_text(encrypted_password, self.master_key)
                tree.insert("", "end", values=(decrypted_username, decrypted_password))
            except ValueError:
                tree.insert("", "end", values=("Decryption failed", "Decryption failed"))

        def on_tree_select(event):
            selected_item = tree.selection()[0]
            values = tree.item(selected_item, "values")
            pyperclip.copy(values[1])
            messagebox.showinfo("Success", f"Password for {values[0]} copied to clipboard!")

        tree.bind("<<TreeviewSelect>>", on_tree_select)

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()
