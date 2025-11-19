import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

class InventoryManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Manajemen Inventaris Gudang")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f0f0')
  
        self.conn = sqlite3.connect('inventory.db')
        self.create_table()

        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 16, 'bold'))
        
        self.create_widgets()
        self.load_data()
        
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
                harga_jual REAL,
                supplier TEXT,
                lokasi TEXT,
                tanggal_masuk TEXT,
                tanggal_update TEXT
            )
        ''')
        self.conn.commit()
    
    def create_widgets(self):
        header_frame = ttk.Frame(self.root)
        header_frame.pack(pady=10, padx=20, fill='x')
        
        ttk.Label(header_frame, text="SISTEM MANAJEMEN INVENTARIS GUDANG", 
                 style='Header.TLabel').pack()
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)

        input_frame = ttk.LabelFrame(main_frame, text="Input Data Barang", padding=10)
        input_frame.grid(row=0, column=0, sticky='ew', padx=(0, 10))
    
        labels = ['Kode Barang:', 'Nama Barang:', 'Kategori:', 'Stok:', 
                 'Harga Beli:', 'Harga Jual:', 'Supplier:', 'Lokasi:']
        self.entries = {}
        
        for i, label in enumerate(labels):
            ttk.Label(input_frame, text=label).grid(row=i, column=0, sticky='w', pady=5)
            entry = ttk.Entry(input_frame, width=25)
            entry.grid(row=i, column=1, sticky='ew', pady=5, padx=(5, 0))
            self.entries[label] = entry
    
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
 
        columns = ('ID', 'Kode', 'Nama', 'Kategori', 'Stok', 'Harga Beli', 'Harga Jual', 'Supplier', 'Lokasi')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
    
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
   
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.tree.bind('<Double-1>', self.on_item_select)
        
        report_frame = ttk.LabelFrame(main_frame, text="Laporan & Analisis", padding=10)
        report_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(10, 0))
        
        ttk.Button(report_frame, text="Export to Excel", 
                  command=self.export_to_excel).pack(side='left', padx=5)
        ttk.Button(report_frame, text="Stok Rendah (<10)", 
                  command=self.show_low_stock).pack(side='left', padx=5)
        ttk.Button(report_frame, text="Grafik Stok", 
                  command=self.show_stock_chart).pack(side='left', padx=5)
        ttk.Button(report_frame, text="Total Nilai Inventaris", 
                  command=self.show_total_value).pack(side='left', padx=5)
    
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)
    
    def add_item(self):
        try:
            kode_barang = self.entries['Kode Barang:'].get()
            nama_barang = self.entries['Nama Barang:'].get()
            kategori = self.entries['Kategori:'].get()
            
            if not kode_barang or not nama_barang:
                messagebox.showerror("Error", "Kode Barang dan Nama Barang harus diisi!")
                return
            
            stok = int(self.entries['Stok:'].get() or 0)
            harga_beli = float(self.entries['Harga Beli:'].get() or 0)
            harga_jual = float(self.entries['Harga Jual:'].get() or 0)
            supplier = self.entries['Supplier:'].get()
            lokasi = self.entries['Lokasi:'].get()
            tanggal_masuk = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO inventory 
                (kode_barang, nama_barang, kategori, stok, harga_beli, harga_jual, supplier, lokasi, tanggal_masuk, tanggal_update)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (kode_barang, nama_barang, kategori, stok, harga_beli, harga_jual, supplier, lokasi, tanggal_masuk, tanggal_masuk))
            
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
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Pilih barang yang akan diupdate!")
            return
        
        item_id = self.tree.item(selected_item[0])['values'][0]
        
        try:
            kode_barang = self.entries['Kode Barang:'].get()
            nama_barang = self.entries['Nama Barang:'].get()
            kategori = self.entries['Kategori:'].get()
            stok = int(self.entries['Stok:'].get() or 0)
            harga_beli = float(self.entries['Harga Beli:'].get() or 0)
            harga_jual = float(self.entries['Harga Jual:'].get() or 0)
            supplier = self.entries['Supplier:'].get()
            lokasi = self.entries['Lokasi:'].get()
            tanggal_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE inventory SET 
                kode_barang=?, nama_barang=?, kategori=?, stok=?, harga_beli=?, harga_jual=?, 
                supplier=?, lokasi=?, tanggal_update=?
                WHERE id=?
            ''', (kode_barang, nama_barang, kategori, stok, harga_beli, harga_jual, supplier, lokasi, tanggal_update, item_id))
            
            self.conn.commit()
            messagebox.showinfo("Sukses", "Barang berhasil diupdate!")
            self.load_data()
            
        except ValueError:
            messagebox.showerror("Error", "Stok dan harga harus berupa angka!")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")
    
    def delete_item(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Pilih barang yang akan dihapus!")
            return
        
        if messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin menghapus barang ini?"):
            item_id = self.tree.item(selected_item[0])['values'][0]
            
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM inventory WHERE id=?', (item_id,))
            self.conn.commit()
            
            messagebox.showinfo("Sukses", "Barang berhasil dihapus!")
            self.clear_form()
            self.load_data()
    
    def search_item(self):
        search_term = self.search_entry.get()
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM inventory 
            WHERE kode_barang LIKE ? OR nama_barang LIKE ? OR kategori LIKE ?
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        
        rows = cursor.fetchall()
        self.update_treeview(rows)
    
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
           
            self.entries['Kode Barang:'].delete(0, tk.END)
            self.entries['Kode Barang:'].insert(0, item_values[1])
            
            self.entries['Nama Barang:'].delete(0, tk.END)
            self.entries['Nama Barang:'].insert(0, item_values[2])
            
            self.entries['Kategori:'].delete(0, tk.END)
            self.entries['Kategori:'].insert(0, item_values[3])
            
            self.entries['Stok:'].delete(0, tk.END)
            self.entries['Stok:'].insert(0, item_values[4])
            
            self.entries['Harga Beli:'].delete(0, tk.END)
            self.entries['Harga Beli:'].insert(0, item_values[5])
            
            self.entries['Harga Jual:'].delete(0, tk.END)
            self.entries['Harga Jual:'].insert(0, item_values[6])
            
            self.entries['Supplier:'].delete(0, tk.END)
            self.entries['Supplier:'].insert(0, item_values[7])
            
            self.entries['Lokasi:'].delete(0, tk.END)
            self.entries['Lokasi:'].insert(0, item_values[8])
    
    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
    
    def show_low_stock(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM inventory WHERE stok < 10 ORDER BY stok ASC')
        rows = cursor.fetchall()
        
        if rows:
            self.update_treeview(rows)
            messagebox.showwarning("Stok Rendah", f"Terdapat {len(rows)} barang dengan stok rendah (<10)")
        else:
            messagebox.showinfo("Info", "Tidak ada barang dengan stok rendah")
    
    def export_to_excel(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT kode_barang, nama_barang, kategori, stok, harga_beli, harga_jual, 
                       supplier, lokasi, tanggal_masuk 
                FROM inventory
            ''')
            rows = cursor.fetchall()
            
            df = pd.DataFrame(rows, columns=['Kode Barang', 'Nama Barang', 'Kategori', 'Stok', 
                                           'Harga Beli', 'Harga Jual', 'Supplier', 'Lokasi', 'Tanggal Masuk'])
            
            filename = f"inventory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(filename, index=False)
            messagebox.showinfo("Sukses", f"Data berhasil diexport ke {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal export: {str(e)}")
    
    def show_stock_chart(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT nama_barang, stok FROM inventory ORDER BY stok DESC LIMIT 10')
        rows = cursor.fetchall()
        
        if not rows:
            messagebox.showinfo("Info", "Tidak ada data untuk ditampilkan")
            return
        
        names = [row[0] for row in rows]
        stocks = [row[1] for row in rows]
     
        chart_window = tk.Toplevel(self.root)
        chart_window.title("Grafik Stok Barang")
        chart_window.geometry("800x600")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(names, stocks, color='skyblue')
        ax.set_title('10 Barang dengan Stok Terbanyak')
        ax.set_xlabel('Nama Barang')
        ax.set_ylabel('Jumlah Stok')
        plt.xticks(rotation=45, ha='right')
    
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def show_total_value(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT SUM(stok * harga_beli) FROM inventory')
        total_value = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT COUNT(*) FROM inventory')
        total_items = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(stok) FROM inventory')
        total_stock = cursor.fetchone()[0] or 0
        
        messagebox.showinfo("Total Nilai Inventaris", 
                          f"Total Barang: {total_items}\n"
                          f"Total Stok: {total_stock}\n"
                          f"Total Nilai Inventaris: Rp {total_value:,.2f}")
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryManager(root)

    root.mainloop()
