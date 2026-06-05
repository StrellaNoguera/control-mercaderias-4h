import csv
import os
from datetime import datetime

ARCHIVO_STOCK = "stock.csv"
ARCHIVO_MOVIMIENTOS = "movimientos.csv"

# ──────────────────────────────────────────────
# UTILIDADES
# ──────────────────────────────────────────────

def inicializar_archivos():
    """Crea los archivos CSV si no existen."""
    if not os.path.exists(ARCHIVO_STOCK):
        with open(ARCHIVO_STOCK, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "nombre", "categoria", "cantidad", "precio_unitario", "stock_minimo"])

    if not os.path.exists(ARCHIVO_MOVIMIENTOS):
        with open(ARCHIVO_MOVIMIENTOS, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["fecha", "producto_id", "producto_nombre", "tipo", "cantidad", "observacion"])


def leer_stock():
    """Devuelve lista de productos del stock."""
    productos = []
    with open(ARCHIVO_STOCK, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            productos.append(row)
    return productos


def guardar_stock(productos):
    """Guarda la lista de productos en el archivo."""
    with open(ARCHIVO_STOCK, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "nombre", "categoria", "cantidad", "precio_unitario", "stock_minimo"])
        writer.writeheader()
        writer.writerows(productos)


def registrar_movimiento(producto_id, nombre, tipo, cantidad, observacion=""):
    """Registra una entrada o salida en el historial."""
    with open(ARCHIVO_MOVIMIENTOS, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            producto_id,
            nombre,
            tipo,
            cantidad,
            observacion
        ])


def nuevo_id(productos):
    """Genera un ID autoincremental."""
    if not productos:
        return "1"
    return str(max(int(p["id"]) for p in productos) + 1)


def separador():
    print("\n" + "─" * 45)


# ──────────────────────────────────────────────
# FUNCIONES PRINCIPALES
# ──────────────────────────────────────────────

def agregar_producto():
    separador()
    print("  AGREGAR PRODUCTO")
    separador()
    nombre = input("Nombre del producto: ").strip()
    if not nombre:
        print("❌ El nombre no puede estar vacío.")
        return
    categoria = input("Categoría (ej: bebidas, limpieza, snacks): ").strip()
    try:
        cantidad = int(input("Cantidad inicial: "))
        precio = float(input("Precio unitario (Gs.): "))
        stock_min = int(input("Stock mínimo antes de alerta: "))
    except ValueError:
        print("❌ Ingresá solo números en cantidad, precio y stock mínimo.")
        return

    productos = leer_stock()
    nuevo = {
        "id": nuevo_id(productos),
        "nombre": nombre,
        "categoria": categoria,
        "cantidad": str(cantidad),
        "precio_unitario": str(precio),
        "stock_minimo": str(stock_min)
    }
    productos.append(nuevo)
    guardar_stock(productos)
    registrar_movimiento(nuevo["id"], nombre, "ENTRADA", cantidad, "Stock inicial")
    print(f"\n✅ Producto '{nombre}' agregado con ID {nuevo['id']}.")


def ver_stock():
    separador()
    print("  STOCK ACTUAL")
    separador()
    productos = leer_stock()
    if not productos:
        print("No hay productos registrados.")
        return

    print(f"{'ID':<5} {'Nombre':<22} {'Categoría':<14} {'Cant':>5} {'Precio':>12} {'Mín':>5}")
    print("─" * 65)
    for p in productos:
        alerta = " ⚠️ " if int(p["cantidad"]) <= int(p["stock_minimo"]) else ""
        print(f"{p['id']:<5} {p['nombre']:<22} {p['categoria']:<14} {int(p['cantidad']):>5} {float(p['precio_unitario']):>12,.0f} {int(p['stock_minimo']):>5}{alerta}")
    print()


def registrar_entrada():
    separador()
    print("  REGISTRAR ENTRADA (reposición)")
    separador()
    ver_stock()
    try:
        pid = input("ID del producto: ").strip()
        cantidad = int(input("Cantidad a agregar: "))
    except ValueError:
        print("❌ Ingresá un número válido.")
        return

    productos = leer_stock()
    for p in productos:
        if p["id"] == pid:
            p["cantidad"] = str(int(p["cantidad"]) + cantidad)
            guardar_stock(productos)
            registrar_movimiento(pid, p["nombre"], "ENTRADA", cantidad)
            print(f"\n✅ Entrada registrada. Stock actual de '{p['nombre']}': {p['cantidad']}")
            return
    print("❌ Producto no encontrado.")


def registrar_salida():
    separador()
    print("  REGISTRAR SALIDA (venta/uso)")
    separador()
    ver_stock()
    try:
        pid = input("ID del producto: ").strip()
        cantidad = int(input("Cantidad a descontar: "))
    except ValueError:
        print("❌ Ingresá un número válido.")
        return

    productos = leer_stock()
    for p in productos:
        if p["id"] == pid:
            stock_actual = int(p["cantidad"])
            if cantidad > stock_actual:
                print(f"❌ No hay suficiente stock. Disponible: {stock_actual}")
                return
            p["cantidad"] = str(stock_actual - cantidad)
            guardar_stock(productos)
            registrar_movimiento(pid, p["nombre"], "SALIDA", cantidad)
            nuevo_stock = int(p["cantidad"])
            print(f"\n✅ Salida registrada. Stock actual de '{p['nombre']}': {nuevo_stock}")
            if nuevo_stock <= int(p["stock_minimo"]):
                print(f"⚠️  ALERTA: Stock bajo el mínimo ({p['stock_minimo']} unidades).")
            return
    print("❌ Producto no encontrado.")


def alertas_stock_bajo():
    separador()
    print("  ALERTAS DE STOCK BAJO")
    separador()
    productos = leer_stock()
    bajos = [p for p in productos if int(p["cantidad"]) <= int(p["stock_minimo"])]
    if not bajos:
        print("✅ Todos los productos tienen stock suficiente.")
        return
    print(f"{'ID':<5} {'Nombre':<25} {'Stock actual':>13} {'Mínimo':>8}")
    print("─" * 55)
    for p in bajos:
        print(f"{p['id']:<5} {p['nombre']:<25} {int(p['cantidad']):>13} {int(p['stock_minimo']):>8}")


def ver_movimientos():
    separador()
    print("  HISTORIAL DE MOVIMIENTOS")
    separador()
    if not os.path.exists(ARCHIVO_MOVIMIENTOS):
        print("No hay movimientos registrados.")
        return
    with open(ARCHIVO_MOVIMIENTOS, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        filas = list(reader)
    if not filas:
        print("No hay movimientos registrados.")
        return
    # Mostrar los últimos 20
    ultimos = filas[-20:]
    print(f"{'Fecha':<18} {'Producto':<20} {'Tipo':<8} {'Cant':>6}  {'Obs.'}")
    print("─" * 65)
    for m in ultimos:
        print(f"{m['fecha']:<18} {m['producto_nombre']:<20} {m['tipo']:<8} {int(m['cantidad']):>6}  {m['observacion']}")
    if len(filas) > 20:
        print(f"\n  (mostrando los últimos 20 de {len(filas)} registros)")


def eliminar_producto():
    separador()
    print("  ELIMINAR PRODUCTO")
    separador()
    ver_stock()
    pid = input("ID del producto a eliminar: ").strip()
    productos = leer_stock()
    nuevos = [p for p in productos if p["id"] != pid]
    if len(nuevos) == len(productos):
        print("❌ Producto no encontrado.")
        return
    confirmar = input(f"¿Segura que querés eliminar el producto ID {pid}? (s/n): ").strip().lower()
    if confirmar == "s":
        guardar_stock(nuevos)
        print("✅ Producto eliminado.")
    else:
        print("Operación cancelada.")


# ──────────────────────────────────────────────
# MENÚ PRINCIPAL
# ──────────────────────────────────────────────

def menu():
    inicializar_archivos()
    while True:
        separador()
        print("  4H MARKET — Control de Mercaderías")
        separador()
        print("  1. Ver stock actual")
        print("  2. Agregar producto nuevo")
        print("  3. Registrar entrada (reposición)")
        print("  4. Registrar salida (venta/uso)")
        print("  5. Ver alertas de stock bajo")
        print("  6. Ver historial de movimientos")
        print("  7. Eliminar producto")
        print("  0. Salir")
        separador()
        opcion = input("  Elegí una opción: ").strip()

        if opcion == "1":
            ver_stock()
        elif opcion == "2":
            agregar_producto()
        elif opcion == "3":
            registrar_entrada()
        elif opcion == "4":
            registrar_salida()
        elif opcion == "5":
            alertas_stock_bajo()
        elif opcion == "6":
            ver_movimientos()
        elif opcion == "7":
            eliminar_producto()
        elif opcion == "0":
            print("\n  Hasta luego 👋\n")
            break
        else:
            print("❌ Opción inválida.")

        input("\n  Presioná Enter para continuar...")


if __name__ == "__main__":
    menu()
