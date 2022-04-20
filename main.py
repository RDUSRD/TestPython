# -*- coding: utf-8 -*-
# Importamos los modulos principales para el manejo de GUI y base de datos
import kivy
import os
import sqlite3

# Configuracion adicional para iniciar con un tamaño predeterminada la app
from kivy.config import Config
Config.set("graphics","width","340")
Config.set("graphics","hight","640")

# Mas imports provenientes de kivy, cada uno es un modulo creador de vizualizaciones en widgets
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label 
from kivy.uix.screenmanager import ScreenManager, Screen 
from kivy.uix.screenmanager import FadeTransition
from kivy.properties import StringProperty
from kivy.uix.image import Image

# Clase conectora con la base de datos en sqlite3
def connect_to_database(path):
    try:
        con = sqlite3.connect(path)
        cursor = con.cursor()
        create_table_clientes(cursor)
        con.commit()
        con.close()
    except Exception as e:
        print(e)

# Sentencia SQL para la creacion de tabla, en caso de que exista no hara nada
def create_table_clientes(cursor):
    cursor.execute(
        '''
        CREATE TABLE clientes(
        ID        INT   PRIMARY KEY  NOT NULL,
        Nombre    TEXT               NOT NULL,
        Apellido  TEXT               NOT NULL,
        Telefono  INT                NOT NULL,
        Email     TEXT               NOT NULL,
        
        )'''
    )

# Clase creada para manejar un mensaje popup para indicar un error
class MessagePopup(Popup):
    pass

# Clase del screen manager o manejador de pantallas, es encargada de tener todo widget dentro de si para manejarlas a su antojo
class MainWid(ScreenManager):
    def __init__(self,**kwargs):
        super(MainWid,self).__init__()
        self.APP_PATH = os.getcwd()
        self.DB_PATH = self.APP_PATH+'/clientes_database.db'
        self.StartWid = StartWid(self)
        self.DataBaseWid = DataBaseWid(self)
        self.InsertDataWid = BoxLayout()
        self.UpdateDataWid = BoxLayout()
        self.Popup = MessagePopup()

        # Como estaba indicado anteriormente, en este codigo debajo, se maneja la pantalla que se presenta al momento
        wid = Screen(name='start')
        wid.add_widget(self.StartWid)
        self.add_widget(wid)
        wid = Screen(name='database')
        wid.add_widget(self.DataBaseWid)
        self.add_widget(wid)
        wid = Screen(name='insertdata')
        wid.add_widget(self.InsertDataWid)
        self.add_widget(wid)
        wid = Screen(name='updatedata')
        wid.add_widget(self.UpdateDataWid)
        self.add_widget(wid)
        
        self.goto_start()

    # Funcion para ir a la primera pantalla de inicio
    def goto_start(self):
        self.current = 'start'

    # Funcion para ir a la segunda pantalla, observacion de base de datos
    def goto_database(self):
        self.DataBaseWid.check_memory()
        self.current = 'database'

    # Funcion para ir a pantalla de insertar datos
    def goto_insertdata(self):
        self.InsertDataWid.clear_widgets()
        wid = InsertDataWid(self)
        self.InsertDataWid.add_widget(wid)
        self.current = 'insertdata'

    # Funcion para ir a pantalla de actualizar datos
    def goto_updatedata(self,data_id):
        self.UpdateDataWid.clear_widgets()
        wid = UpdateDataWid(self,data_id)
        self.UpdateDataWid.add_widget(wid)
        self.current = 'updatedata'

# Widget de comienzo de pantalla
class StartWid(BoxLayout):
    def __init__(self,mainwid,**kwargs):
        super(StartWid,self).__init__()
        self.mainwid = mainwid
        
    def create_database(self):
        connect_to_database(self.mainwid.DB_PATH)
        self.mainwid.goto_database()

# Widget donde esta la base de datos en observacion
class DataBaseWid(BoxLayout):
    def __init__(self,mainwid,**kwargs):
        super(DataBaseWid,self).__init__()
        self.mainwid = mainwid

    # Funcion para revisar la memoria de la base de datos y recuperar datos para imprimir
    def check_memory(self):
        self.ids.container.clear_widgets()
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        cursor.execute('select ID, Nombre, Apellido, Telefono, Email from clientes')
        for i in cursor:
            wid = DataWid(self.mainwid)
            r1 = 'ID: '+str(100000000+i[0])[1:9]+'\n'
            r2 = i[1]+', '+i[2]+'\n'
            r3 = 'Telefono: '+str(i[3])+'\n'
            r4 = 'Email: '+str(i[4])
            wid.data_id = str(i[0])
            wid.data = r1+r2+r3+r4
            self.ids.container.add_widget(wid)
        wid = NewDataButton(self.mainwid)
        self.ids.container.add_widget(wid)
        con.close()
        
# Widget de presentacion de la pantalla de actualizar
class UpdateDataWid(BoxLayout):
    def __init__(self,mainwid,data_id,**kwargs):
        super(UpdateDataWid,self).__init__()
        self.mainwid = mainwid
        self.data_id = data_id
        self.check_memory()

    # Funcion para buscar el cliente a actualizar y sus datos
    def check_memory(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        s = 'select Nombre, Apellido, Telefono, Email from clientes where ID='
        cursor.execute(s+self.data_id)
        for i in cursor:
            self.ids.ti_nombre.text = i[0]
            self.ids.ti_apellido.text = i[1]
            self.ids.ti_telefono.text = str(i[2])
            self.ids.ti_email.text = str(i[3])
        con.close()

    # Funcion para actualizar con datos nuevos al cliente ya buscado
    def update_data(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        d1 = self.ids.ti_nombre.text
        d2 = self.ids.ti_apellido.text
        d3 = self.ids.ti_telefono.text
        d4 = self.ids.ti_email.text
        a1 = (d1,d2,d3,d4)
        s1 = 'UPDATE clientes SET'
        s2 = 'Nombre="%s",Apellido="%s",Telefono=%s,Email="%s"' % a1
        s3 = 'WHERE ID=%s' % self.data_id

        # Try/except para mostrar el popup de error en caso de que algo este mal
        try:
            cursor.execute(s1+' '+s2+' '+s3)
            con.commit()
            con.close()
            self.mainwid.goto_database()
        except Exception as e:
            message = self.mainwid.Popup.ids.message
            self.mainwid.Popup.open()
            self.mainwid.Popup.title = "Data base error"
            if '' in a1:
                message.text = 'Uno o más campos están vacíos'
            else: 
                message.text = str(e)
            con.close()

    # Funcion para eliminar datos de la base de datos
    def delete_data(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        s = 'delete from clientes where ID='+self.data_id
        cursor.execute(s)
        con.commit()
        con.close()
        self.mainwid.goto_database()

    # Funcion para volver a la pantalla de observacion de base de datos
    def back_to_dbw(self):
        self.mainwid.goto_database()

# Widget de insertar datos
class InsertDataWid(BoxLayout):
    def __init__(self,mainwid,**kwargs):
        super(InsertDataWid,self).__init__()
        self.mainwid = mainwid

    # Funcion para insertar datos en la base de datos
    def insert_data(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        d1 = self.ids.ti_id.text
        d2 = self.ids.ti_nombre.text
        d3 = self.ids.ti_apellido.text
        d4 = self.ids.ti_telefono.text
        d5 = self.ids.ti_email.text
        a1 = (d1,d2,d3,d4,d5)
        s1 = 'INSERT INTO clientes(ID, Nombre, Apellido, Telefono, Email)'
        s2 = 'VALUES(%s,"%s","%s",%s,"%s")' % a1
        try:
            cursor.execute(s1+' '+s2)
            con.commit()
            con.close()
            self.mainwid.goto_database()
        except Exception as e:
            message = self.mainwid.Popup.ids.message
            self.mainwid.Popup.open()
            self.mainwid.Popup.title = "Data base error"
            if '' in a1:
                message.text = 'Uno o más campos están vacíos'
            else: 
                message.text = str(e)
            con.close()

    # Funcion para volver a segunda pantalla
    def back_to_dbw(self):
        self.mainwid.goto_database()

# Widget que aparece dentro del widget de la segunda pantalla. la de observacion de datos, aqui se imprimen los datos
class DataWid(BoxLayout):
    def __init__(self,mainwid,**kwargs):
        super(DataWid,self).__init__()
        self.mainwid = mainwid

    # Funcion para entrar en la pantalla de actualizar datos
    def update_data(self,data_id):
        self.mainwid.goto_updatedata(data_id)

# Widget de boton
class NewDataButton(Button):
    def __init__(self,mainwid,**kwargs):
        super(NewDataButton,self).__init__()
        self.mainwid = mainwid

    # Funcion para insertar nuevo cliente o dato
    def create_new_cliente(self):
        self.mainwid.goto_insertdata()

# Clase main para hacer la app ejecutable
class MainApp(App):
    def build(self):
        return MainWid()

if __name__ == '__main__':
    MainApp().run()
