import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
import getpass

# Obtener el nombre de usuario del sistema operativo
usuario_actual = getpass.getuser()

if usuario_actual != "Felip":
    messagebox.showerror("Error de Acceso", "Lo siento, no tienes permiso para usar este programa.")
    exit()

# Conexión a la base de datos
conn = sqlite3.connect('club_submarinismo.db')
cursor = conn.cursor()

# Crear tablas si no existen
cursor.execute('''
    CREATE TABLE IF NOT EXISTS EXPEDICION (
        idExpedicion INTEGER PRIMARY KEY,
        fecha TEXT,
        lugar TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS ANIMAL (
        idAnimal INTEGER PRIMARY KEY,
        nombre TEXT,
        N_cient TEXT,
        idExpedicion INTEGER,
        cebo TEXT,
        FOREIGN KEY (idExpedicion) REFERENCES EXPEDICION(idExpedicion),
        CONSTRAINT unique_nombre UNIQUE (nombre)
    )
''')

conn.commit()

def agregar_expedicion_animal():
    fecha = fecha_entry.get()
    lugar = lugar_entry.get()
    animal = animal_entry.get()
    N_cient = N_cient_entry.get()
    
    if not fecha or not lugar or not animal or not N_cient:
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return
    
    # Verificar si el animal o nombre científico ya existe en la base de datos
    cursor.execute('''
        SELECT fecha
        FROM ANIMAL
        JOIN EXPEDICION ON ANIMAL.idExpedicion = EXPEDICION.idExpedicion
        WHERE nombre = ? OR N_cient = ?
    ''', (animal, N_cient))
    resultado = cursor.fetchone()
    
    if resultado:
        messagebox.showinfo("Aviso", f"Esta especie ya se introdujo en la base de datos el {resultado[0]}.")
        return
    
    # Si no existe, agregar la expedición y el animal
    cursor.execute('INSERT INTO EXPEDICION (fecha, lugar) VALUES (?, ?)', (fecha, lugar))
    conn.commit()
    messagebox.showinfo("Éxito", "Expedición agregada con éxito.")

    id_expedicion = cursor.lastrowid
    
    cursor.execute('INSERT INTO ANIMAL (nombre, N_cient, idExpedicion) VALUES (?, ?, ?)', (animal, N_cient, id_expedicion))
    conn.commit()
    messagebox.showinfo("Éxito", "Animal agregado con éxito.")

def mostrar_animales():
    cursor.execute('''
        SELECT ANIMAL.idAnimal, ANIMAL.nombre, ANIMAL.N_cient, ANIMAL.cebo, EXPEDICION.lugar, EXPEDICION.fecha
        FROM ANIMAL
        LEFT JOIN EXPEDICION ON ANIMAL.idExpedicion = EXPEDICION.idExpedicion
    ''')
    animales = cursor.fetchall()
    if animales:
        animales_text = ""
        for animal in animales:
            animales_text += f"ID: {animal[0]}\n"
            animales_text += f"Nombre: {animal[1]}\n"
            animales_text += f"N Científico: {animal[2]}\n"
            animales_text += f"Cebo: {animal[3]}\n" if animal[3] else ""
            animales_text += f"Lugar: {animal[4]}\n"
            animales_text += f"Fecha: {animal[5]}\n"
            animales_text += "-------------------------------------\n"
        messagebox.showinfo("Animales Registrados", animales_text)
    else:
        messagebox.showinfo("Animales Registrados", "No hay animales registrados.")

def agregar_cebo():
    id_animal = simpledialog.askinteger("ID del Animal", "Introduce el ID del animal:")
    cebo = simpledialog.askstring("Agregar Cebo", "Introduce el cebo:")
    
    if id_animal is None or cebo is None:
        messagebox.showerror("Error", "Debes proporcionar el ID del animal y el cebo.")
        return
    
    # Verificar si la ID del animal está registrada en la base de datos
    cursor.execute('SELECT idAnimal FROM ANIMAL WHERE idAnimal = ?', (id_animal,))
    resultado = cursor.fetchone()
    if not resultado:
        messagebox.showerror("Error", "La ID del animal no está registrada en la base de datos.")
        return
    
    # Obtener el nombre del animal
    cursor.execute('SELECT nombre FROM ANIMAL WHERE idAnimal = ?', (id_animal,))
    nombre_animal = cursor.fetchone()[0]
    
    # Insertar el cebo con el nombre del animal
    cursor.execute('UPDATE ANIMAL SET cebo = ? WHERE idAnimal = ?', (cebo, id_animal))
    conn.commit()
    messagebox.showinfo("Éxito", "Cebo agregado con éxito.")

# Interfaz gráfica con Tkinter
root = tk.Tk()
root.title("Club de Submarinismo")

frame_datos = tk.Frame(root)
frame_datos.pack(pady=10)

tk.Label(frame_datos, text="Fecha:", anchor="w").grid(row=0, column=0, sticky="w")
fecha_entry = tk.Entry(frame_datos)
fecha_entry.grid(row=0, column=1, sticky="w")

tk.Label(frame_datos, text="Lugar:", anchor="w").grid(row=1, column=0, sticky="w")
lugar_entry = tk.Entry(frame_datos)
lugar_entry.grid(row=1, column=1, sticky="w")

tk.Label(frame_datos, text="Animal:", anchor="w").grid(row=2, column=0, sticky="w")
animal_entry = tk.Entry(frame_datos)
animal_entry.grid(row=2, column=1, sticky="w")

tk.Label(frame_datos, text="N. científico:", anchor="w").grid(row=3, column=0, sticky="w")
N_cient_entry = tk.Entry(frame_datos)
N_cient_entry.grid(row=3, column=1, sticky="w")

agregar_button = tk.Button(frame_datos, text="Agregar Expedición y Animal", command=agregar_expedicion_animal)
agregar_button.grid(row=4, columnspan=2, pady=5)

mostrar_animales_button = tk.Button(frame_datos, text="Mostrar Animales", command=mostrar_animales)
mostrar_animales_button.grid(row=5, columnspan=2, pady=5)

agregar_cebo_button = tk.Button(frame_datos, text="Agregar Cebo", command=agregar_cebo)
agregar_cebo_button.grid(row=6, columnspan=2, pady=5)

# Botón para salir
salir_button = tk.Button(frame_datos, text="Salir", command=root.destroy)
salir_button.grid(row=7, columnspan=2, pady=5)

root.mainloop()
