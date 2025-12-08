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

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kode_barang TEXT UNIQUE,
                nama_barang TEXT NOT NULL,
                kategori TEXT,
                stok INTEGER NOT NULL,
                harga_beli REAL,
                harga_jual REAL
            )
        ''')
        self.conn.commit()

    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(pady=10, padx=20, fill='x')

        ttk.Label(header_frame, text="SISTEM MANAJEMEN INVENTARIS GUDANG", 
                 style='Header.TLabel').pack()

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)

        input_frame = ttk.LabelFrame(main_frame, text="Input Data Barang", padding=10)
        input_frame.grid(row=0, column=0, sticky='ew', padx=(0, 10))

        labels = ['Kode Barang:', 'Nama Barang:', 'Kategori:', 'Stok:', 
                 'Harga Beli:', 'Harga Jual:']
 
        self.entries = []  
        
        for i, label in enumerate(labels):
            ttk.Label(input_frame, text=label).grid(row=i, column=0, sticky='w', pady=5)
            entry = ttk.Entry(input_frame, width=25)
            entry.grid(row=i, column=1, sticky='ew', pady=5, padx=(5, 0))
            self.entries.append(entry) 

        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=len(labels), column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Tambah Barang", 
                  command=self.add_item).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Update Barang", 
                  command=self.update_item).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Hapus Barang", 
                  command=self.delete_item).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Form", 
                  command=self.clear_form).pack(side='left', padx=5)

        search_frame = ttk.Frame(input_frame)
        search_frame.grid(row=len(labels)+1, column=0, columnspan=2, pady=10, sticky='ew')

        ttk.Label(search_frame, text="Cari:").pack(side='left')
        self.search_entry = ttk.Entry(search_frame, width=20)
        self.search_entry.pack(side='left', padx=5)
        ttk.Button(search_frame, text="Cari", 
                  command=self.search_item).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Refresh", 
                  command=self.load_data).pack(side='left', padx=5)

        table_frame = ttk.LabelFrame(main_frame, text="Daftar Inventaris", padding=10)
        table_frame.grid(row=0, column=1, sticky='nsew')

        columns = ('ID', 'Kode', 'Nama', 'Kategori', 'Stok', 'Harga Beli', 'Harga Jual')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.tree.bind('<ButtonRelease-1>', self.on_item_select)  # Ganti untuk deteksi klik
   
    def add_item(self):
        try:
            item_data = [entry.get() for entry in self.entries]  
            self.stack.append(('add', item_data))  

            kode_barang = self.entries[0].get()
            nama_barang = self.entries[1].get()
            kategori = self.entries[2].get()
            
            if not kode_barang or not nama_barang:
                messagebox.showerror("Error", "Kode Barang dan Nama Barang harus diisi!")
                return
            
            stok = int(self.entries[3].get() or 0)
            harga_beli = float(self.entries[4].get() or 0)
            harga_jual = float(self.entries[5].get() or 0)
            
            cursor = self.conn.cursor()
            cursor.execute(''' 
                INSERT INTO inventory 
                (kode_barang, nama_barang, kategori, stok, harga_beli, harga_jual)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (kode_barang, nama_barang, kategori, stok, harga_beli, harga_jual))
            
            self.conn.commit()
            messagebox.showinfo("Sukses", "Barang berhasil ditambahkan!")
            self.clear_form()
            self.load_data()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Kode Barang sudah ada!")
        except ValueError:
            messagebox.showerror("Error", "Stok dan harga harus berupa angka!")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

    def update_item(self):
        if self.selected_item_id is None:
            messagebox.showerror("Error", "Pilih barang yang akan diupdate!")
            return

        kode_barang = self.entries[0].get()
        nama_barang = self.entries[1].get()
        kategori = self.entries[2].get()
        stok = int(self.entries[3].get() or 0)
        harga_beli = float(self.entries[4].get() or 0)
        harga_jual = float(self.entries[5].get() or 0)

        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE inventory SET 
                kode_barang=?, nama_barang=?, kategori=?, stok=?, harga_beli=?, harga_jual=?
                WHERE id=?
            ''', (kode_barang, nama_barang, kategori, stok, harga_beli, harga_jual, self.selected_item_id))

            self.conn.commit()
            messagebox.showinfo("Sukses", "Barang berhasil diupdate!")
            self.load_data()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

    def delete_item(self):
        if self.selected_item_id is None:
            messagebox.showerror("Error", "Pilih barang yang akan dihapus!")
            return

        if messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin menghapus barang ini?"):
            try:
                cursor = self.conn.cursor()
                cursor.execute('DELETE FROM inventory WHERE id=?', (self.selected_item_id,))
                self.conn.commit()
                messagebox.showinfo("Sukses", "Barang berhasil dihapus!")
                self.load_data()
                self.clear_form()
            except Exception as e:
                messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

    def clear_form(self):
        for entry in self.entries:
            entry.delete(0, tk.END)
        self.selected_item_id = None

    def load_data(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM inventory ORDER BY id DESC')
        rows = cursor.fetchall()
        self.update_treeview(rows)

    def update_treeview(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert('', 'end', values=row)

    def on_item_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item[0])['values']
            self.selected_item_id = item_values[0]  

            self.entries[0].delete(0, tk.END)
            self.entries[0].insert(0, item_values[1])

            self.entries[1].delete(0, tk.END)
            self.entries[1].insert(0, item_values[2])

            self.entries[2].delete(0, tk.END)
            self.entries[2].insert(0, item_values[3])

            self.entries[3].delete(0, tk.END)
            self.entries[3].insert(0, item_values[4])

            self.entries[4].delete(0, tk.END)
            self.entries[4].insert(0, item_values[5])

            self.entries[5].delete(0, tk.END)
            self.entries[5].insert(0, item_values[6])

    def search_item(self):
        search_term = self.search_entry.get()  
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM inventory 
            WHERE kode_barang LIKE ? OR nama_barang LIKE ? OR kategori LIKE ?
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))  
        rows = cursor.fetchall() 
        self.update_treeview(rows)
