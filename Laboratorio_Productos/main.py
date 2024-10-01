import os
import platform
from datetime import datetime

from clases import (    
    ProductoElectronico,
    ProductoAlimenticio,
    GestionProductos
)

def limpiar_pantalla():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

def mostrar_menu():
    print(" =============== Menú de Gestión de Productos =============== ")
    print(" 1. Agregar Producto Electrónico")
    print(" 2. Agregar Producto Alimenticio")
    print(" 3. Buscar Producto")
    print(" 4. Actualizar Precio de Producto")
    print(" 5. Actualizar Stock de Producto")
    print(" 6. Eliminar Producto")
    print(" 7. Mostrar todos los Productos")
    print(" 8. Salir")
    print(" ===============================================================")

def agregar_producto(gestion: GestionProductos, tipo_producto):
    try:
        nombre = input("Ingrese el nombre del producto: ")

        while True:
            try:
                precio = input("Ingrese el precio del producto: ")
                precio_validado = float(precio)
                if precio_validado <= 0:
                    raise ValueError("El precio debe ser mayor a 0")
                break
            except ValueError as e:
                print(f"Error: {e}")

        while True:
            try:
                stock = input("Ingrese el stock del producto: ")
                stock_validado = int(stock)
                if stock_validado < 0:
                    raise ValueError("El stock no puede ser negativo")
                break
            except ValueError as e:
                print(f"Error: {e}")

        origen = input("Ingrese el país de origen del producto: ")

        if tipo_producto == '1':
            while True:
                try:
                    fecha_fabricacion = input("Ingrese la fecha de fabricación del producto (YYYY-MM-DD): ")
                    datetime.strptime(fecha_fabricacion, '%Y-%m-%d')  # Validar formato de fecha
                    producto = ProductoElectronico(nombre, precio_validado, stock_validado, origen, fecha_fabricacion)
                    break
                except ValueError as e:
                    print(f"Error: Formato de fecha incorrecto. Use YYYY-MM-DD.")
        elif tipo_producto == '2':
            while True:
                try:
                    fecha_vencimiento = input("Ingrese la fecha de caducidad del producto (YYYY-MM-DD): ")
                    datetime.strptime(fecha_vencimiento, '%Y-%m-%d')  # Validar formato de fecha
                    producto = ProductoAlimenticio(nombre, precio_validado, stock_validado, origen, fecha_vencimiento)
                    break
                except ValueError as e:
                    print(f"Error: Formato de fecha incorrecto. Use YYYY-MM-DD.")
        else:
            print("Opción inválida")
            return

        gestion.crear_producto(producto)
        print(f"Producto {nombre} creado exitosamente.")

    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        input("Presione Enter para continuar...")

def buscar_producto_por_nombre(gestion):
    nombre = input("Ingrese el nombre del producto: ")
    producto = gestion.leer_producto(nombre)
    
    if producto:
        mostrar_info_producto(producto)
    else:
        print(f"No se encontró el producto {nombre}")
    
    input("\nPresione Enter para continuar")

def mostrar_info_producto(producto):
    print("\nInformación del producto:")
    print(f"Nombre: {producto['Nombre']}")
    print(f"Precio: ${producto['Precio']:.2f}")
    print(f"Stock: {producto['Stock']}")
    print(f"Origen: {producto['Origen']}")
    if producto['fecha_vencimiento']:
        print(f"Fecha de vencimiento: {producto['fecha_vencimiento']}")
        print("Tipo: Producto Alimenticio")
    elif producto['fecha_fabricacion']:
        print(f"Fecha de fabricación: {producto['fecha_fabricacion']}")
        print("Tipo: Producto Electrónico")

def actualizar_precio_producto(gestion):
    nombre = input("Ingrese el nombre del producto que desea actualizar: ")
    
    producto = gestion.leer_producto(nombre)
    if producto:
        mostrar_info_producto(producto)
        precio_actual = producto['Precio']
        print(f"\nPrecio actual de {nombre}: ${precio_actual:.2f}")
        
        opcion = input("¿Desea establecer un nuevo precio (1) o modificar por porcentaje (2)? ")
        
        if opcion == '1':
            nuevo_precio = float(input("Ingrese el nuevo precio: "))
        elif opcion == '2':
            porcentaje = float(input("Ingrese el porcentaje de cambio (positivo para aumentar, negativo para disminuir): "))
            nuevo_precio = precio_actual * (1 + porcentaje/100)
        else:
            print("Opción no válida.")
            return
        
        if gestion.actualizar_precio_producto(nombre, nuevo_precio):
            diferencia = nuevo_precio - precio_actual
            if diferencia > 0:
                print(f"El precio de {nombre} aumentó en ${diferencia:.2f}.")
            elif diferencia < 0:
                print(f"El precio de {nombre} disminuyó en ${abs(diferencia):.2f}.")
            else:
                print(f"El precio de {nombre} no cambió.")
    else:
        print(f"No se encontró el producto {nombre}")
    
    input("Presione Enter para continuar")

def actualizar_stock_producto(gestion):
    nombre = input("Ingrese el nombre del producto que desea actualizar: ")
    
    producto = gestion.leer_producto(nombre)
    if producto:
        mostrar_info_producto(producto)
        stock_actual = producto['Stock']
        print(f"\nStock actual de {nombre}: {stock_actual}")
        
        opcion = input("¿Desea establecer un nuevo valor (1) o modificar por cantidad (2)? ")
        
        if opcion == '1':
            nuevo_stock = int(input("Ingrese el nuevo valor de Stock: "))
        elif opcion == '2':
            cantidad = int(input("Ingrese la cantidad a añadir (positivo) o restar (negativo): "))
            nuevo_stock = stock_actual + cantidad
        else:
            print("Opción no válida.")
            return
        
        if gestion.actualizar_stock_producto(nombre, nuevo_stock):
            diferencia = nuevo_stock - stock_actual
            if diferencia > 0:
                print(f"El stock de {nombre} aumentó en {diferencia} unidades.")
            elif diferencia < 0:
                print(f"El stock de {nombre} disminuyó en {abs(diferencia)} unidades.")
            else:
                print(f"El stock de {nombre} no cambió.")
    else:
        print(f"No se encontró el producto {nombre}")
    
    input("Presione Enter para continuar")

def eliminar_producto(gestion):
    nombre_producto = input("Ingrese el nombre del producto a eliminar: ")
    
    # Primero, mostramos la información del producto
    producto = gestion.leer_producto(nombre_producto)
    if producto:
        mostrar_info_producto(producto)
        confirmacion = input(f"\n¿Está seguro de que desea eliminar el producto '{nombre_producto}'? (s/n): ")
        if confirmacion.lower() == 's':
            if gestion.eliminar_producto(nombre_producto):
                print(f"El producto '{nombre_producto}' ha sido eliminado correctamente.")
            else:
                print(f"No se pudo eliminar el producto '{nombre_producto}'.")
        else:
            print("Operación de eliminación cancelada.")
    else:
        print(f"No se encontró el producto '{nombre_producto}'.")
    
    input("\nPresione Enter para continuar")

def mostrar_todos_los_productos(gestion):
    print("\n=========== Listado Completo de Productos ================")
    productos = gestion.leer_todos_productos()
    
    if productos:
        for producto in productos:
            mostrar_info_producto(producto)
            print("-------------------------------------------------------")
    else:
        print("No se encontraron productos en la base de datos.")
    
    print("===============================================================")
    input("\nPresione Enter para continuar")

if __name__ == "__main__":
    gestion = GestionProductos()
    
    while True:
        limpiar_pantalla()
        mostrar_menu()
        opcion = input('Seleccione una opción: ')
        
        if opcion == '1' or opcion == '2':
            agregar_producto(gestion, opcion)
        elif opcion == '3':
            buscar_producto_por_nombre(gestion)    
        elif opcion == '4':
            actualizar_precio_producto(gestion)     
        elif opcion == '5':
            actualizar_stock_producto(gestion)      
        elif opcion == '6':
            eliminar_producto(gestion)  
        elif opcion == '7':
            mostrar_todos_los_productos(gestion)
        elif opcion == '8':
            print("Saliendo del programa...")
            break
        else:
            print("Opción no válida")