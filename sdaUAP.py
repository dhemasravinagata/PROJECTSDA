import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from collections import deque

class InventoryManager:
    def _init_(self, root):
        self.root = root
        self.root.title("Sistem Manajemen Inventaris Gudang")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f0f0')

        self.conn = sqlite3.connect('inventory.db')
        self.create_table()

        self.stack = [] 
        self.queue = deque()
