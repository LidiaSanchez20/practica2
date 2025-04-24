class Persona:
    def __init__(self, nombre, contacto):
        self.nombre = nombre
        self.contacto = contacto

class Cliente(Persona):
    def __init__(self, nombre, contacto, nivel_de_fidelidad=0):
        super().__init__(nombre, contacto)
        self.nivel_de_fidelidad = nivel_de_fidelidad
        self.historial_pedidos = []

    def realizar_pedido(self, pedido):
        self.historial_pedidos.append(pedido)

class Empleado(Persona):
    def __init__(self, nombre, contacto, rol):
        super().__init__(nombre, contacto)
        self.rol = rol

    def actualizar_inventario(self, inventario, producto, cantidad):
        inventario.actualizar_stock(producto, cantidad)

    def cambiar_estado_pedido(self, pedido, estado):
        pedido.actualizar_estado(estado)

class ProductoBase:
    def __init__(self, nombre_producto, precio):
        self.nombre_producto = nombre_producto
        self.precio = precio

    def calcular_precio(self):
        return self.precio

class Bebida(ProductoBase):
    catalogo_bebidas = []

    def __init__(self, nombre_producto, precio, tamano, tipo_bebida, stock=0):
        super().__init__(nombre_producto, precio)
        self.tamano = tamano
        self.tipo_bebida = tipo_bebida
        self.stock = stock
        self.personalizacion = {}

    @classmethod
    def agregar_bebida(cls, bebida):
        cls.catalogo_bebidas.append(bebida)

    @classmethod
    def obtener_catalogo_bebidas(cls):
        return cls.catalogo_bebidas

    def personalizar(self, opcion, valor):
        self.personalizacion[opcion] = valor

class Postre(ProductoBase):
    catalogo_postres = []

    def __init__(self, nombre_producto, precio, vegano, sin_gluten, stock=0):
        super().__init__(nombre_producto, precio)
        self.vegano = vegano
        self.sin_gluten = sin_gluten
        self.stock = stock
        self.personalizacion = {}

    @classmethod
    def agregar_postre(cls, postre):
        cls.catalogo_postres.append(postre)

    @classmethod
    def obtener_catalogo_postres(cls):
        return cls.catalogo_postres

class Inventario:
    def __init__(self):
        self.stock = {}

    def actualizar_stock(self, producto, cantidad):
        self.stock[producto] = max(0, self.stock.get(producto, 0) + cantidad)

    def consultar_disp(self, producto):
        return self.stock.get(producto, 0) > 0

class Pedido:
    def __init__(self, cliente):
        self.cliente = cliente
        self.productos = []
        self.estado = "Pendiente"
        self.pagado = False

    def agregar_producto(self, producto, inventario):
        if inventario.consultar_disp(producto.nombre_producto):
            self.productos.append(producto)
            inventario.actualizar_stock(producto.nombre_producto, -1)
        else:
            raise ValueError(f"Producto sin stock: {producto.nombre_producto}")

    def calcular_total(self):
        total = sum(p.calcular_precio() for p in self.productos)
        descuento = 0.05 * total if self.cliente.nivel_de_fidelidad > 2 else 0
        return total - descuento

    def actualizar_estado(self, nuevo_estado):
        self.estado = nuevo_estado

    def modificar_personalizacion(self, producto, opcion, valor):
        if isinstance(producto, Bebida):
            producto.personalizar(opcion, valor)

    def obtener_resumen(self):
        return {
            "Cliente": self.cliente.nombre,
            "Productos": [p.nombre_producto for p in self.productos],
            "Total": f"${self.calcular_total():.2f}",
            "Estado": self.estado
        }