""" Objetivo: Mediante la creación de repositorios en GitHub que implemente la solución propuesta en el laboratorio anterior con persistencia en una base de datos SQL.

Descripción: En este laboratorio, deberás implementar la solución utilizando Python en el paradigma de programación orientada a objetos. 
La persistencia de los datos deberá realizarse en una base de datos SQL. 
Una vez completada la solución, deberás subir el código a un repositorio público en GitHub y proporcionar el enlace correspondiente para su evaluación.
 """

import mysql.connector
from mysql.connector import Error
from decouple import config

from datetime import datetime
from datetime import date
import traceback

class Producto:
    def __init__(self, nombre, precio, stock, origen):
        self.__nombre = nombre
        self.__precio = self.validar_precio(precio)
        self.__stock = self.validar_stock(stock)
        self.__origen = origen
    
    @property    
    def nombre(self):
        return self.__nombre.capitalize()
    
    @property
    def precio(self):
        return float(self.__precio)
    
    @property
    def stock(self):
        return int(self.__stock)
    
    @property
    def origen(self):
        return self.__origen.capitalize() 
    
    #SETTERS
    
    @precio.setter
    def precio(self, nuevo_precio):
        self.__precio = self.validar_precio(nuevo_precio) 

    @stock.setter
    def stock(self, nuevo_stock):
        self.__stock = self.validar_stock(nuevo_stock)
        
    @staticmethod
    def validar_precio(precio):
        try:
            precio_num = float(precio)
            if precio_num <= 0:
                raise ValueError("El precio debe ser mayor a 0")
            return precio_num
        except ValueError as e:
            raise ValueError(f"Error en el precio: {str(e)}")

    @staticmethod
    def validar_stock(stock):
        try:
            stock_num = int(stock)
            if stock_num < 0:
                raise ValueError("El stock no puede ser negativo")
            return stock_num
        except ValueError as e:
            raise ValueError(f"Error en el stock: {str(e)}")
    
    
    #FUNCIONES
    def to_dict(self):
        return {
            "nombre": self.nombre,
            "precio": self.precio,
            "stock": self.stock,
            "origen": self.origen             
        }
        
    def __str__(self):
        return f"{self.nombre}"
    
class ProductoElectronico(Producto):
    def __init__(self, nombre, precio, stock, origen, fecha_fabricacion):
        super().__init__(nombre, precio, stock, origen)        
        self.__fecha_fabricacion = self.validar_fecha(fecha_fabricacion)
        
    
    @property
    def fecha_fabricacion(self):
        return self.__fecha_fabricacion.strftime('%Y-%m-%d')
    
    @fecha_fabricacion.setter
    def fecha_fabricacion(self, nueva_fecha):
        self.__fecha_fabricacion = self.validar_fecha(nueva_fecha)
    
    
    def validar_fecha(self, fecha):
        try: 
            fecha_fabricacion = datetime.strptime(fecha, '%Y-%m-%d')
            return fecha_fabricacion.date()
        except ValueError:
            raise ValueError("Ingrese un formato de fecha correcto: dd-mm-aaaa")
        
        
    def to_dict(self):
        data = super().to_dict()
        data['fecha_fabricacion'] = self.fecha_fabricacion 
        return data
        
    def __str__(self):
        return f'{super().__str__()} - Fecha de Fabricación: {self.fecha_fabricacion}'

class ProductoAlimenticio(Producto):
    def __init__(self, nombre, precio, stock, origen, fecha_vencimiento):
        super().__init__(nombre, precio, stock, origen)        
        self.__fecha_vencimiento = self.validar_fecha(fecha_vencimiento)
        
    
    @property
    def fecha_vencimiento(self):
        return self.__fecha_vencimiento.strftime('%Y-%m-%d') 
       
    @fecha_vencimiento.setter
    def fecha_vencimiento(self, nueva_fecha):
        self.__fecha_vencimiento = self.validar_fecha(nueva_fecha) 
        
    def validar_fecha(self, fecha):
        try: 
            fecha_vencimiento = datetime.strptime(fecha, '%Y-%m-%d')
            return fecha_vencimiento.date()
        except ValueError:
            raise ValueError("Ingrese un formato de fecha correcto: aaaa-mm-dd")
    
    
    def to_dict(self):
        data = super().to_dict()
        data['fecha_vencimiento'] = self.fecha_vencimiento 
        return data
        
    def __str__(self):
        return f'{super().__str__()} - Fecha de Vencimiento: {self.fecha_vencimiento}'
    
class GestionProductos:
    def __init__(self):
        self.host = config('DB_HOST')
        self.database = config('DB_NAME')
        self.user = config('DB_USER')
        self.password = config('DB_PASSWORD')
        self.port =config('DB_PORT')
        
    def connect(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                database= self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            
            if connection.is_connected():
                return connection
        except Error as e:
            print(f"error al conectar a la base de datos: {e}")
            return None

           
    @staticmethod
    def serializar_fecha(obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    def crear_producto(self, producto):
        try:
            connection = self.connect()          
            if connection:
                with connection.cursor() as cursor:
                    # Verificar nombre
                    cursor.execute('SELECT nombre FROM productos WHERE nombre = %s', (producto.nombre,))
                    if cursor.fetchone():
                        print(f'Error: Ya existe el producto {producto.nombre}')
                        return
                    
                    query_productos = '''INSERT INTO productos(nombre, precio, stock, origen)
                    VALUES(%s, %s, %s, %s)
                    '''
                    cursor.execute(query_productos, (producto.nombre, producto.precio, producto.stock, producto.origen))                    
                    
                    if isinstance(producto, ProductoAlimenticio):
                        query_especifico = '''INSERT INTO productoalimenticio (nombre, fecha_vencimiento)
                        VALUES (%s, %s)                         
                        '''
                        fecha_vencimiento = datetime.strptime(producto.fecha_vencimiento, '%Y-%m-%d').date()
                        cursor.execute(query_especifico, (producto.nombre, fecha_vencimiento))
                    elif isinstance(producto, ProductoElectronico):
                        query_especifico = '''INSERT INTO productoelectronico (nombre, fecha_fabricacion)
                        VALUES (%s, %s)                         
                        '''
                        fecha_fabricacion = datetime.strptime(producto.fecha_fabricacion, '%Y-%m-%d').date()
                        cursor.execute(query_especifico, (producto.nombre, fecha_fabricacion))

                    connection.commit()
                    print(f"El producto ({producto.nombre}) fue creado correctamente")
        except Exception as error:
            print(f'Error inesperado al crear producto: {error}')
            traceback.print_exc()  # traceback 
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def leer_producto(self, nombre):
        try:
            connection = self.connect()
            if connection:
                with connection.cursor(dictionary=True) as cursor:
                    query = """
                    SELECT p.*, pa.fecha_vencimiento, pe.fecha_fabricacion
                    FROM Productos p
                    LEFT JOIN productoAlimenticio pa ON p.Nombre = pa.Nombre
                    LEFT JOIN productoElectronico pe ON p.Nombre = pe.Nombre
                    WHERE p.Nombre = %s
                    """
                    cursor.execute(query, (nombre,))
                    producto = cursor.fetchone()

                    if producto:
                        return producto
                    else:
                        print(f"No se encontró el producto {nombre}")
                        return None
        except Exception as error:
            print(f'Error inesperado al leer producto: {error}')
            traceback.print_exc()
        finally:
            if connection and connection.is_connected():
                connection.close()
        return None

    def actualizar_precio_producto(self, nombre_producto, nuevo_precio):
        try:
            connection = self.connect()
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute('UPDATE productos SET precio = %s WHERE nombre = %s', (nuevo_precio, nombre_producto))
                    
                    if cursor.rowcount > 0:
                        connection.commit()
                        print(f"El precio se actualizó correctamente para el producto {nombre_producto}")
                        return True
                    else:
                        print(f"No se pudo actualizar el precio del producto {nombre_producto}")
                        return False
        
        except Exception as e:
            print(f"Error al actualizar el precio del producto: {e}")
            return False
        finally:
            if connection and connection.is_connected():
                connection.close()

    def actualizar_stock_producto(self, nombre_producto, nuevo_stock):
        try:
            connection = self.connect()
            if connection:
                with connection.cursor() as cursor:                    
                    cursor.execute('UPDATE productos SET stock = %s WHERE nombre = %s', (nuevo_stock, nombre_producto))
                    
                    if cursor.rowcount > 0:
                        connection.commit()
                        print(f"El stock se actualizó correctamente para el producto {nombre_producto}")
                        return True
                    else:
                        print(f"No se pudo actualizar el stock del producto {nombre_producto}")
                        return False
        
        except Exception as e:
            print(f"Error al actualizar el stock del producto: {e}")
            return False
        finally:
            if connection and connection.is_connected():
                connection.close() 
      
    def eliminar_producto(self, nombre_producto):
        try:
            connection = self.connect()
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM productos WHERE nombre = %s", (nombre_producto,))
                    if not cursor.fetchone():
                        print(f"No se encontró el producto {nombre_producto}")
                        return False

                    # eliminar tablas relacionadas
                    cursor.execute("DELETE FROM productoelectronico WHERE nombre = %s", (nombre_producto,))
                    cursor.execute("DELETE FROM productoalimenticio WHERE nombre = %s", (nombre_producto,))
                    
                    # tabla principal
                    cursor.execute("DELETE FROM productos WHERE nombre = %s", (nombre_producto,))
                    
                    if cursor.rowcount > 0:
                        connection.commit()
                        return True
                    else:
                        print(f"No se pudo eliminar el producto {nombre_producto}")
                        return False
        except mysql.connector.Error as e:
            print(f"Error al eliminar el producto: {e}")
            return False
        finally:
            if connection and connection.is_connected():
                connection.close()


    def leer_todos_productos(self):
        try:
            connection = self.connect()
            if connection:
                with connection.cursor(dictionary=True) as cursor:
                    query = """
                    SELECT p.*, pa.fecha_vencimiento, pe.fecha_fabricacion
                    FROM Productos p
                    LEFT JOIN productoAlimenticio pa ON p.Nombre = pa.Nombre
                    LEFT JOIN productoElectronico pe ON p.Nombre = pe.Nombre
                    """
                    cursor.execute(query)
                    productos = cursor.fetchall()

                    if productos:
                        return productos
                    else:
                        return []
        except Exception as error:
            print(f'Error inesperado al leer productos: {error}')
            traceback.print_exc()
        finally:
            if connection and connection.is_connected():
                connection.close()
        return []
