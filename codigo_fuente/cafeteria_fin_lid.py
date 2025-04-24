import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import csv
import os
import sys
from backend2 import *

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

USUARIOS_FILE = "usuarios.csv"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
CSV_FILE = "productos.csv"

class CafeteriaApp:
    pedidos_en_tiempo_real = []

    def __init__(self, root):
        self.root = root
        self.root.title("Coffee Time")
        self.root.geometry("800x600")
        self.root.config(bg="#eae1be")
        self.root.iconbitmap(os.path.join(BASE_DIR, "icono_coffee.ico"))

        self.canvas = tk.Canvas(self.root, bg="#eae1be")
        self.canvas.pack(fill="both", expand=True)
        self.imagen_original = Image.open(os.path.join(BASE_DIR, "fondo_inicio.png"))
        self.canvas.imagen_original = self.imagen_original
        self.canvas.bind("<Configure>", self.redimensionar_fondo)
        self.total_pago_label = None

        self.pantalla_inicio()

    def redimensionar_fondo(self, event):
        nuevo_ancho = event.width
        nuevo_alto = event.height
        imagen_redimensionada = self.canvas.imagen_original.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)
        foto = ImageTk.PhotoImage(imagen_redimensionada)
        self.canvas.create_image(0, 0, image=foto, anchor="nw")
        self.canvas.image = foto

    def pantalla_inicio(self):
        for widget in self.canvas.winfo_children():
            widget.destroy()

        tk.Label(self.canvas, text="Bienvenido a Coffee Time", font=("Cormorant Garamond", 18)).place(relx=0.5, rely=0.3, anchor="center")
        tk.Button(self.canvas, text="Iniciar Sesión", command=self.abrir_login, bg="#eae1be", width=20).place(relx=0.5, rely=0.45, anchor="center")
        tk.Button(self.canvas, text="Registrarse", command=self.abrir_registro, bg="#eae1be", width=20).place(relx=0.5, rely=0.55, anchor="center")

    def abrir_login(self):
        login_win = tk.Toplevel(self.root)
        login_win.title("Iniciar Sesión")
        login_win.geometry("600x500")
        login_win.config(bg="#e8d2aa")

        tk.Label(login_win, text="Username:", bg="#F1F3F0").place(x=160, y=100)
        entry_username = tk.Entry(login_win, width=30)
        entry_username.place(x=230, y=100)

        tk.Label(login_win, text="Password:", bg="#F1F3F0").place(x=160, y=160)
        entry_password = tk.Entry(login_win, show="*", width=30)
        entry_password.place(x=230, y=160)

        def hacer_login():
            username = entry_username.get().strip()
            password = entry_password.get().strip()
            rol = self.verificar_login(username, password)
            if rol:
                messagebox.showinfo("Login Exitoso", f"Bienvenido, {username} ({rol})", parent=login_win)
                login_win.destroy()
                self.abrir_interfaz_usuario(rol, username)
            else:
                messagebox.showerror("Error", "Datos incorrectos", parent=login_win)

        tk.Button(login_win, text="Login", command=hacer_login, bg="#F1F3F0", width=35).place(x=160, y=250)

    def abrir_registro(self):
        reg_win = tk.Toplevel(self.root)
        reg_win.title("Registro")
        reg_win.geometry("800x600")
        reg_win.config(bg="#eae1be")

        tk.Label(reg_win, text="Registro de Cliente", bg="#eae1be", font=("Arial", 14)).place(x=50, y=30)
        tk.Label(reg_win, text="Username:", bg="#eae1be").place(x=50, y=80)
        entry_username = tk.Entry(reg_win)
        entry_username.place(x=150, y=80)

        tk.Label(reg_win, text="Password:", bg="#eae1be").place(x=50, y=120)
        entry_password = tk.Entry(reg_win, show="*")
        entry_password.place(x=150, y=120)

        tk.Label(reg_win, text="Confirm Password:", bg="#eae1be").place(x=50, y=160)
        entry_confirm = tk.Entry(reg_win, show="*")
        entry_confirm.place(x=150, y=160)

        def registrar():
            username = entry_username.get().strip()
            password = entry_password.get().strip()
            confirm = entry_confirm.get().strip()
            if not username or not password:
                messagebox.showerror("Error", "Todos los campos son obligatorios.", parent=reg_win)
                return
            if password != confirm:
                messagebox.showerror("Error", "Las contraseñas no coinciden.", parent=reg_win)
                return
            usuarios = self.cargar_usuarios()
            if username in usuarios:
                messagebox.showerror("Error", "El username ya existe.", parent=reg_win)
                return
            usuarios[username] = {"password": password, "rol": "cliente"}
            self.guardar_usuarios(usuarios)
            messagebox.showinfo("Registro", "Usuario registrado exitosamente.", parent=reg_win)
            reg_win.destroy()
            self.abrir_interfaz_usuario("cliente", username)

        tk.Button(reg_win, text="Registrar", command=registrar, bg="#eae1be").place(x=150, y=200)

    def cerrar_sesion(self):
        self.current_order = None
        self.usuario_actual = None
        for widget in self.root.winfo_children():
            widget.destroy()
        self.__init__(self.root)

    def abrir_interfaz_usuario(self, rol, username):
        self.root.geometry("1300x700")
        for widget in self.root.winfo_children():
            widget.destroy()

        canvas = tk.Canvas(self.root, bg="#eae1be")
        canvas.pack(fill="both", expand=True)
        fondo = Image.open(os.path.join(BASE_DIR, "fondo_cafeteria.png"))
        canvas.imagen_original = fondo

        def redimensionar_fondo(event):
            nuevo_ancho = event.width
            nuevo_alto = event.height
            imagen_redimensionada = canvas.imagen_original.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)
            foto = ImageTk.PhotoImage(imagen_redimensionada)
            canvas.create_image(0, 0, image=foto, anchor="nw")
            canvas.image = foto

        canvas.bind("<Configure>", redimensionar_fondo)

        notebook = ttk.Notebook(canvas)
        notebook.place(x=20, y=100, width=800, height=630)

        self.tab_menu = tk.Frame(notebook, bg="#eae1be")
        notebook.add(self.tab_menu, text="Menú")
        self.cargar_catalogo_csv()
        self.configurar_tab_menu(self.tab_menu)

        if rol == "cliente":
            pedido_prev = next((p for p in CafeteriaApp.pedidos_en_tiempo_real if p.cliente.nombre == username and p.estado not in ("Finalizado", "Cancelado")), None)

            if pedido_prev:
                self.current_order = pedido_prev
            else:
                self.current_order = Pedido(Cliente(username, ""))
                CafeteriaApp.pedidos_en_tiempo_real.append(self.current_order)

            self.tab_pedidos = tk.Frame(notebook, bg="#eae1be")
            notebook.add(self.tab_pedidos, text="Pedidos")
            self.configurar_tab_pedidos(self.tab_pedidos)

            self.tab_pago = tk.Frame(notebook, bg="#eae1be")
            notebook.add(self.tab_pago, text="Pago")
            self.configurar_tab_pago(self.tab_pago)

        elif rol == "administrador":
            self.tab_admin = tk.Frame(notebook, bg="#eae1be")
            notebook.add(self.tab_admin, text="Administración")
            self.configurar_tab_admin(self.tab_admin)

        tk.Button(self.root, text="Cerrar sesión", command=self.cerrar_sesion, bg="#eae1be").place(x=20, y=20)
        tk.Label(self.root, text="Gracias por usar Coffee Time ☕", bg="#eae1be", font=("Arial", 10, "italic")).place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

    def configurar_tab_menu(self, tab):
        for w in tab.winfo_children():
            w.destroy()
        tab.config(bg="#eae1be")
        cont = tk.Frame(tab, bg="#eae1be")
        cont.pack(pady=10)

        frm_b = tk.Frame(cont, bg="#eae1be")
        frm_b.grid(row=0, column=0, padx=20)
        tk.Label(frm_b, text="Bebidas", font=("Cormorant Garamond", 16), bg="#eae1be").pack()
        self.tree_bebidas = ttk.Treeview(frm_b, columns=("Nombre", "Precio"), show="headings", height=10)
        for col, w in [("Nombre", 200), ("Precio", 80)]:
            self.tree_bebidas.heading(col, text=col)
            self.tree_bebidas.column(col, width=w, anchor="center")
        self.tree_bebidas.tag_configure('agotado', foreground='grey')
        for i, b in enumerate(Bebida.obtener_catalogo_bebidas()):
            stock = self.inventario.stock.get(b.nombre_producto, 0)
            tags = ('agotado',) if stock <= 0 else ()
            self.tree_bebidas.insert("", "end", iid=str(i), values=(b.nombre_producto, f"${b.precio:.2f}", stock), tags=tags)
        sb = ttk.Scrollbar(frm_b, command=self.tree_bebidas.yview)
        self.tree_bebidas.configure(yscrollcommand=sb.set)
        self.tree_bebidas.pack(side="left")
        sb.pack(side="right", fill="y")

        frm_p = tk.Frame(cont, bg="#eae1be")
        frm_p.grid(row=0, column=1, padx=20)
        tk.Label(frm_p, text="Postres", font=("Cormorant Garamond", 16), bg="#eae1be").pack()
        self.tree_postres = ttk.Treeview(frm_p, columns=("Nombre", "Precio"), show="headings", height=10)
        for col, w in [("Nombre", 200), ("Precio", 80)]:
            self.tree_postres.heading(col, text=col)
            self.tree_postres.column(col, width=w, anchor="center")
        self.tree_postres.tag_configure('agotado', foreground='grey')
        for i, p in enumerate(Postre.obtener_catalogo_postres()):
            stock = self.inventario.stock.get(p.nombre_producto, 0)
            tags = ('agotado',) if stock <= 0 else ()
            self.tree_postres.insert("", "end", iid=str(i), values=(p.nombre_producto, f"${p.precio:.2f}", stock), tags=tags)
        sb2 = ttk.Scrollbar(frm_p, command=self.tree_postres.yview)
        self.tree_postres.configure(yscrollcommand=sb2.set)
        self.tree_postres.pack(side="left")
        sb2.pack(side="right", fill="y")

        tk.Button(tab, text="Agregar al Carrito", command=self.agregar_producto_al_carrito, bg="#eae1be").pack(pady=10)

    def eliminar_producto_admin(self):
        producto_seleccionado = self.tree_stock.selection()
        if not producto_seleccionado:
            return messagebox.showwarning("Eliminar", "Selecciona un producto del listado.")
    
        prod_nombre = self.tree_stock.item(producto_seleccionado[0])['values'][0]
    
        confirm = messagebox.askyesno("Eliminar Producto", f"¿Estás seguro de que deseas eliminar '{prod_nombre}'?")
        if not confirm:
            return

        if prod_nombre in self.inventario.stock:
            del self.inventario.stock[prod_nombre]
    
        Bebida.catalogo_bebidas = [b for b in Bebida.catalogo_bebidas if b.nombre_producto != prod_nombre]
        Postre.catalogo_postres = [p for p in Postre.catalogo_postres if p.nombre_producto != prod_nombre]

        self.guardar_stock_csv()
        self.configurar_tab_menu(self.tab_menu)
        self.configurar_tab_admin(self.tab_admin)


    def configurar_tab_pedidos(self, tab):
        for w in tab.winfo_children():
            w.destroy()
        tab.config(bg="#eae1be")

        wrapper = tk.Frame(tab, bg="#eae1be")
        wrapper.pack(pady=10)

        tk.Label(wrapper, text="Panel de Pedidos", font=("Arial", 14, "bold"), bg="#eae1be").pack(pady=5)

        frame_carrito = tk.LabelFrame(wrapper, text="Carrito de Compras", font=("Arial", 10), bg="#eae1be", padx=10, pady=10)
        frame_carrito.pack(pady=5)
        self.carrito_listbox = tk.Listbox(frame_carrito, width=60, height=8)
        self.carrito_listbox.pack()

        info_frame = tk.Frame(wrapper, bg="#eae1be")
        info_frame.pack(pady=5)
        self.estado_label = tk.Label(info_frame, text="Estado: N/A", font=("Arial", 10), bg="#eae1be")
        self.estado_label.pack()
        self.total_label = tk.Label(info_frame, text="Total: $0.00", font=("Arial", 10), bg="#eae1be")
        self.total_label.pack()

        btn_frame = tk.Frame(wrapper, bg="#eae1be")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Eliminar Producto", command=self.eliminar_producto_carrito, bg="#eae1be", width=18).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Finalizar Pedido", command=self.finalizar_pedido, bg="#eae1be", width=18).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Actualizar", command=self.actualizar_pedidos, bg="#eae1be", width=18).grid(row=0, column=2, padx=5)

        self.actualizar_pedidos()

    def configurar_tab_pago(self, tab):
        for w in tab.winfo_children():
            w.destroy()
        tab.config(bg="#eae1be")

        self.total_pago_label = tk.Label(tab, font=("Arial", 12), bg="#eae1be")
        self.total_pago_label.pack(pady=5)

        self.actualizar_total_pago()

        metodo_pago = ttk.Combobox(tab, values=["Efectivo", "Tarjeta"], state="readonly")
        metodo_pago.current(0)
        metodo_pago.pack(pady=5)

        def procesar_pago():
            if self.current_order.pagado:
                return messagebox.showinfo("Ya pagado", "Este pedido ya ha sido pagado.")

            if not self.current_order:
                return messagebox.showwarning("Sin Pedido", "No hay pedido activo.")
    
            if self.current_order.estado == "Entregado":
                return messagebox.showinfo("Pedido entregado", "Este pedido ya fue entregado. No se puede volver a pagar.")

            metodo = metodo_pago.get()
            messagebox.showinfo("Pago", f"Pago con {metodo} recibido.")

            self.current_order.pagado = True
            self.actualizar_pedidos()
            self.actualizar_total_pago()
            self.btn_procesar_pago.config(state="disabled")

        self.btn_procesar_pago = tk.Button(tab, text="Procesar Pago", command=procesar_pago, bg="#eae1be")
        self.btn_procesar_pago.pack(pady=10)

        if self.current_order and self.current_order.estado == "Pagado":
            self.btn_procesar_pago.config(state="disabled")

    def configurar_tab_admin(self, tab):
        for w in tab.winfo_children():
            w.destroy()
        tab.config(bg="#eae1be")

        tk.Label(tab, text="Administración", font=("Arial", 14), bg="#eae1be").pack(pady=10)

        tree_frame = tk.Frame(tab, bg="#eae1be")
        tree_frame.pack(pady=5)
        self.tree_stock = ttk.Treeview(tree_frame, columns=("Prod", "Stock"), show="headings", height=5)
        self.tree_stock.heading("Prod", text="Producto")
        self.tree_stock.heading("Stock", text="Stock")
        for prod, qty in self.inventario.stock.items():
            self.tree_stock.insert("", "end", values=(prod, qty))
        self.tree_stock.pack(side="left")
        sb = ttk.Scrollbar(tree_frame, command=self.tree_stock.yview)
        sb.pack(side="right", fill="y")
        self.tree_stock.configure(yscrollcommand=sb.set)

        def actualizar_tabla():
            self.tree_stock.delete(*self.tree_stock.get_children())
            for prod, qty in self.inventario.stock.items():
                self.tree_stock.insert("", "end", values=(prod, qty))
            self.configurar_tab_menu(self.tab_menu)

        def abrir_ventana_actualizar():
            vent = tk.Toplevel()
            vent.title("Actualizar Stock")
            vent.geometry("300x200")
            vent.config(bg="#eae1be")
            tk.Label(vent, text="Producto:", bg="#eae1be").pack(pady=5)
            entry_p = tk.Entry(vent)
            entry_p.pack(pady=5)
            tk.Label(vent, text="Cantidad (+/-):", bg="#eae1be").pack(pady=5)
            entry_q = tk.Entry(vent)
            entry_q.pack(pady=5)
            def upd():
                prod = entry_p.get().strip()
                try:
                    cant = int(entry_q.get())
                except:
                    return messagebox.showerror("Error", "Cantidad inválida.")
                if prod not in self.inventario.stock:
                    return messagebox.showerror("Error", "Producto no encontrado.")
                self.inventario.actualizar_stock(prod, cant)
                self.guardar_stock_csv()
                messagebox.showinfo("Stock", "Stock actualizado.")
                actualizar_tabla()
                vent.destroy()
            tk.Button(vent, text="Actualizar", command=upd, bg="#eae1be").pack(pady=10)

        def abrir_ventana_agregar():
            ventana = tk.Toplevel()
            ventana.title("Agregar Producto")
            ventana.geometry("400x350")
            ventana.config(bg="#eae1be")

            tipo_prod = tk.StringVar(value="Bebida")
            tk.Radiobutton(ventana, text="Bebida", variable=tipo_prod, value="Bebida", bg="#eae1be").pack()
            tk.Radiobutton(ventana, text="Postre", variable=tipo_prod, value="Postre", bg="#eae1be").pack()
            tk.Label(ventana, text="Nombre del producto:", bg="#eae1be").pack()
            entry_nombre = tk.Entry(ventana); entry_nombre.pack(pady=5)
            tk.Label(ventana, text="Precio:", bg="#eae1be").pack()
            entry_precio = tk.Entry(ventana); entry_precio.pack(pady=5)
            tk.Label(ventana, text="Tamaño (bebida):", bg="#eae1be").pack()
            entry_tamano = tk.Entry(ventana); entry_tamano.pack(pady=5)
            tk.Label(ventana, text="Tipo (bebida):", bg="#eae1be").pack()
            entry_tipo = tk.Entry(ventana); entry_tipo.pack(pady=5)

            def guardar():
                nombre = entry_nombre.get().strip()
                try:
                    precio = float(entry_precio.get())
                except:
                    return messagebox.showerror("Error", "Precio inválido.")
                if tipo_prod.get() == "Bebida":
                    nueva = Bebida(nombre, precio, entry_tamano.get(), entry_tipo.get())
                    Bebida.agregar_bebida(nueva)
                    self.guardar_producto_csv(nueva, "Bebida", entry_tamano.get(), entry_tipo.get())
                else:
                    nueva = Postre(nombre, precio, False, False)
                    Postre.agregar_postre(nueva)
                    self.guardar_producto_csv(nueva, "Postre", "", "", 5)
                self.inventario.actualizar_stock(nombre, 5)
                self.guardar_stock_csv()
                actualizar_tabla()
                self.configurar_tab_menu(self.tab_menu)
                ventana.destroy()
            tk.Button(ventana, text="Guardar", command=guardar, bg="#eae1be").pack(pady=20)

        btn_frame = tk.Frame(tab, bg="#eae1be")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Actualizar Stock", command=abrir_ventana_actualizar, bg="#eae1be").grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Agregar Producto", command=abrir_ventana_agregar, bg="#eae1be").grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Eliminar Producto", command=self.eliminar_producto_admin, bg="#eae1be").grid(row=0, column=2, padx=5)

        frame_pedidos = tk.LabelFrame(tab, text="Pedidos Activos", font=("Arial", 12), bg="#eae1be")
        frame_pedidos.pack(pady=10, fill="x",expand=True, padx=10)
        
        tabla_frame = tk.Frame(frame_pedidos, bg="#eae1be")
        tabla_frame.pack(fill="both", expand=True)

        scroll_y = ttk.Scrollbar(tabla_frame, orient="vertical")
        scroll_y.pack(side="right", fill="y")

        self.tree_pedidos = ttk.Treeview(tabla_frame, columns=("Cliente", "Estado", "Pago", "Productos"), show="headings", yscrollcommand=scroll_y.set)
        self.tree_pedidos.heading("Cliente", text="Cliente")
        self.tree_pedidos.heading("Estado", text="Estado")
        self.tree_pedidos.heading("Pago", text="Pago")
        self.tree_pedidos.heading("Productos", text="Productos")
        self.tree_pedidos.pack(side="left", fill="both", expand=True)

        self.tree_pedidos.configure(yscrollcommand=scroll_y.set)

        self.actualizar_tabla_pedidos_admin()

        def actualizar_estado_pedido_admin(nuevo_estado):
            sel = self.tree_pedidos.selection()
            if not sel:
                return messagebox.showwarning("Seleccionar", "Seleccione un pedido")
            i = int(sel[0])
            pedido = CafeteriaApp.pedidos_en_tiempo_real[i]

            if nuevo_estado == "Entregado" and not getattr(pedido, 'pagado', False):
                return messagebox.showwarning("No permitido", "Solo puedes marcar como entregado un pedido que ya fue pagado.")

            if "Cancelado" in nuevo_estado:
                razon = simpledialog.askstring("Motivo", "Razón de cancelación:")
                if not razon:
                    return
                nuevo_estado += f": {razon}"
                
            pedido.actualizar_estado(nuevo_estado)    
            self.actualizar_tabla_pedidos_admin()

        btns = tk.Frame(frame_pedidos, bg="#eae1be")
        btns.pack(pady=5)
        tk.Button(btns, text="Pendiente", command=lambda: actualizar_estado_pedido_admin("Pendiente"), bg="#eae1be").pack(side="left", padx=5)
        tk.Button(btns, text="Entregado", command=lambda: actualizar_estado_pedido_admin("Entregado"), bg="#eae1be").pack(side="left", padx=5)
        tk.Button(btns, text="Cancelar", command=lambda: actualizar_estado_pedido_admin("Cancelado"), bg="#eae1be").pack(side="left", padx=5)

        def eliminar_pedido_entregado():
            sel = self.tree_pedidos.selection()
            if not sel:
                return messagebox.showwarning("Seleccionar", "Seleccione un pedido")
            i = int(sel[0])
            pedido = CafeteriaApp.pedidos_en_tiempo_real[i]
            if pedido.estado != "Entregado":
                return messagebox.showwarning("No permitido", "Solo puedes eliminar pedidos entregados.")
            confirm = messagebox.askyesno("Confirmar", "¿Deseas eliminar este pedido entregado?")
            if confirm:
                CafeteriaApp.pedidos_en_tiempo_real.pop(i)
                self.actualizar_tabla_pedidos_admin()

        tk.Button(btns, text="Eliminar Entregado", command=eliminar_pedido_entregado, bg="#eae1be").pack(side="left", padx=5)


    def actualizar_total_pago(self):
        if self.total_pago_label and self.current_order:
            total = self.current_order.calcular_total()
            self.total_pago_label.config(text=f"Total a pagar: ${total:.2f}")

    def actualizar_pedidos(self):
        if not self.current_order:
            return
        self.carrito_listbox.delete(0, tk.END)
        for prod in self.current_order.productos:
            txt = f"{prod.nombre_producto} - ${prod.precio:.2f}"
            if hasattr(prod, 'personalizacion') and prod.personalizacion:
                txt += " (" + ", ".join(f"{k}: {v}" for k, v in prod.personalizacion.items()) + ")"
            self.carrito_listbox.insert(tk.END, txt)
        self.estado_label.config(text="Estado: " + self.current_order.estado)
        self.total_label.config(text=f"Total: ${self.current_order.calcular_total():.2f}")
        self.actualizar_total_pago()

    def actualizar_tabla_pedidos_admin(self): 
        if hasattr(self, 'tree_pedidos') and self.tree_pedidos.winfo_exists():
            self.tree_pedidos.delete(*self.tree_pedidos.get_children())
            for i, pedido in enumerate(CafeteriaApp.pedidos_en_tiempo_real):
                productos = ", ".join(p.nombre_producto for p in pedido.productos)
                self.tree_pedidos.insert("", "end", iid=i, values=(
                    pedido.cliente.nombre, 
                    pedido.estado, 
                    "Sí" if pedido.pagado else "No",
                    productos
                ))

    def cargar_usuarios(self):
        usuarios = {}
        try:
            with open(USUARIOS_FILE, "r", newline="", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) >= 3:
                        username, password, rol = row[0], row[1], row[2]
                        usuarios[username] = {"password": password, "rol": rol}
        except FileNotFoundError:
            usuarios[ADMIN_USERNAME] = {"password": ADMIN_PASSWORD, "rol": "administrador"}
            self.guardar_usuarios(usuarios)
        return usuarios

    def guardar_usuarios(self, usuarios):
        with open(USUARIOS_FILE, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            for username, datos in usuarios.items():
                writer.writerow([username, datos["password"], datos["rol"]])

    def verificar_login(self, username, password):
        usuarios = self.cargar_usuarios()
        usuario = usuarios.get(username)
        if usuario and usuario["password"] == password:
            return usuario["rol"]
        return None
    
    def cargar_catalogo_csv(self):
        Bebida.catalogo_bebidas = []
        Postre.catalogo_postres = []
        stock_inicial = {}
        try:
            with open(CSV_FILE, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for row in reader:
                    if len(row) < 6:
                        continue
                    nombre, raw_precio, tipo, extra1, extra2, raw_stock = row
                    try:
                        precio = float(raw_precio)
                        stock = int(raw_stock)
                    except ValueError:
                        continue
                    stock_inicial[nombre] = stock
                    if tipo == "Bebida":
                        b = Bebida(nombre, precio, extra1, extra2)
                        Bebida.agregar_bebida(b)
                    else:
                        p = Postre(nombre, precio, False, False)
                        Postre.agregar_postre(p)
        except FileNotFoundError:
            return
        self.inventario = Inventario()
        self.inventario.stock = stock_inicial

    def guardar_stock_csv(self):
        try:
            with open(CSV_FILE, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Nombre", "Precio", "Tipo", "Extra1", "Extra2", "Stock"])
                for bebida in Bebida.obtener_catalogo_bebidas():
                    stock = self.inventario.stock.get(bebida.nombre_producto, 0)
                    writer.writerow([bebida.nombre_producto, bebida.precio, "Bebida", bebida.tamano, bebida.tipo_bebida, stock])
                for postre in Postre.obtener_catalogo_postres():
                    stock = self.inventario.stock.get(postre.nombre_producto, 0)
                    writer.writerow([postre.nombre_producto, postre.precio, "Postre", "", "", stock])
        except Exception as e:
            messagebox.showerror("Error al guardar stock", str(e))

    def guardar_producto_csv(self, producto, tipo, extra1="", extra2="", stock=5):
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([producto.nombre_producto, producto.precio, tipo, extra1, extra2, stock])

    def agregar_producto_al_carrito(self):
        sel_b = self.tree_bebidas.selection()
        sel_p = self.tree_postres.selection()
        prod = None
        if sel_b:
            prod = Bebida.obtener_catalogo_bebidas()[int(sel_b[0])]
        elif sel_p:
            prod = Postre.obtener_catalogo_postres()[int(sel_p[0])]
        if not self.current_order:
            self.current_order = Pedido(Cliente(self.usuario_actual, ""))
            CafeteriaApp.pedidos_en_tiempo_real.append(self.current_order)
        if prod:
            if self.inventario.stock.get(prod.nombre_producto, 0) <= 0:
                return messagebox.showwarning("Agotado", f"{prod.nombre_producto} sin stock.")
            if isinstance(prod, Bebida):
                self.personalizar_bebida(prod)
            self.current_order.agregar_producto(prod, self.inventario)
            self.guardar_stock_csv()
            self.actualizar_pedidos()
        else:
            messagebox.showwarning("Seleccionar", "No seleccionaste nada.")
        self.actualizar_total_pago()

    def personalizar_bebida(self, bebida):
        ventana = tk.Toplevel()
        ventana.title("Personaliza tu bebida")
        ventana.geometry("300x300")
        ventana.config(bg="#eae1be")
        tk.Label(ventana, text="Tamaño:", bg="#eae1be").pack(pady=5)
        entrada_tamano = tk.Entry(ventana)
        entrada_tamano.pack(pady=5)
        var_az = tk.IntVar()
        tk.Checkbutton(ventana, text="Extra azúcar", variable=var_az, bg="#eae1be").pack(pady=5)

        def guardar():
            tam = entrada_tamano.get().strip() or bebida.tamano
            bebida.personalizar("tamaño", tam)
            bebida.personalizar("con_azúcar", "Sí" if var_az.get() else "No")
            ventana.destroy()

        tk.Button(ventana, text="Guardar", command=guardar, bg="#eae1be").pack(pady=20)
        ventana.grab_set()
        ventana.wait_window()

    def eliminar_producto_carrito(self):
        sel = self.carrito_listbox.curselection()
        if not sel:
            return messagebox.showwarning("Eliminar", "Nada seleccionado.")
        i = sel[0]
        try:
            self.current_order.productos.pop(i)
        except:
            pass
        self.actualizar_pedidos()
        self.actualizar_total_pago()

    def finalizar_pedido(self):
        if self.current_order:
            self.current_order.actualizar_estado("Finalizado")
            messagebox.showinfo("Finalizado", "Pedido finalizado.")
            self.actualizar_pedidos()
            self.carrito_listbox.delete(0, tk.END)
            self.estado_label.config(text="Estado: Finalizado")
            self.total_label.config(text="Total: $0.00")
            if hasattr(self, 'total_pago_label'):
                self.total_pago_label.config(text="Total a pagar: $0.00")   
            self.current_order = None
        else:
            messagebox.showwarning("Sin Pedido", "No hay pedido.")
        self.actualizar_total_pago()

if __name__ == "__main__":
    root = tk.Tk()
    app = CafeteriaApp(root)
    root.mainloop()