from tkinter import *
import sqlite3

root = Tk()
root.title('Hola mundo: todo list')
root.geometry('400x400')
root.configure(background='#333333')

# conexión con bbdd
conn = sqlite3.connect('todo.db')
c = conn.cursor()

c.execute("""
    CREATE TABLE if not exists todo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        description TEXT NOT NULL,
        completed BOOLEAN NOT NULL
    )
""")

conn.commit()

# funciones

def addTodo():
    todo = e.get()
    if todo:
        c.execute("""
        INSERT INTO todo (description, completed) VALUES (?, ?)
        """,(todo, False)
        )
        conn.commit()
        # limpiamos campo entry
        e.delete(0, END)
        render_todos()
    else:
        pass

# currying!!
def complete(id):
    def _complete():
        todo = c.execute("SELECT * from todo WHERE id=?", (id, )).fetchone()
        # cambia el estado de completed al contrario del que tuviera, por eso se niega que, por cierto está en la última columna (3)
        c.execute("UPDATE todo SET completed = ? WHERE id =?", (not todo[3], id))
        conn.commit()
        render_todos()
    return _complete

# currying!!
def remove(id):
    def _remove():
        c.execute("DELETE FROM todo WHERE id = ?", (id, ))
        conn.commit()
        render_todos()
    return _remove

def render_todos():
    rows = c.execute("SELECT * from todo").fetchall()

    # ACTUALIZAR: antes de renderizar nuevo contenido, HAY QUE ELIMINAR EL CONTENIDO QUE HUBIERA ANTES!
    for widget in frame.winfo_children():
        widget.destroy()


    for i in range(0, len(rows)):
        id = rows[i][0]
        completed = rows[i][3]
        description = rows[i][2]

        # EXPLICACIÓN IMPORTANTE!!!!!

        # anchor='w' empuja a la izq (west) el contenido
        # para pasar el id de la tarea a marcar como completada se usa una función lambda, pero...la función lambda, siempre que esté dentro de un bucle, se va a ejecutar con el valor del último elemento, puesto que el id está constantemente reemplazándose
        # en este caso le estamos pasando el id, pues se va a ejecutar con el id del último elemento
        # para solucionarlo hay que retrasar la ejecución de la función, esto se hace envolviendo la función en otra y eliminado la lambda, que es realmente lo mismo, pero en este caso se hace "fuera" en la definición de la función. Realmente no se va a ejecutar completamente hasta que no se pulse el check
        # t = Checkbutton(frame, text=description, width=40, anchor='w', command=lambda: complete(id))
        # esto se conoce como currying

        # con esta línea cambiamos el color a uno más claro si la tarea está completada
        color = '#aaaaaa' if completed else '#555555'
        t = Checkbutton(frame, text=description, fg=color, width=40, anchor='w', command=complete(id))
        t.grid(row=i, column=0)

        # con esta instrucción marcamos el check si la tarea está completada, caso contrario queda desmarcado
        t.select() if completed else t.deselect()

        btn = Button(frame, text="eliminar", command=remove(id))
        btn.grid(row=i, column=1)
  

# creamos interfaz gráfica
l = Label(root, text="Tarea")
l.grid(row=0, column=0)

e = Entry(root, width=40)
e.grid(row=0, column=1)

btn = Button(root, text="Agregar", command=addTodo)
btn.grid(row=0, column=2)

frame = LabelFrame(root, text='Mis tareas', padx=5, pady=5)
frame.grid(row=1, column=0, columnspan=3, sticky='nswe', padx=5)

e.focus()

# detección de la tecla enter, bind entrega un evento, no nos interesa hacer nada con él epro si no lo incluímos da error.
# para ello usamos una función lambda
root.bind('<Return>', lambda x: addTodo())

# cada vez que abramos la app. lo primero q veremos serán nuestros todos
# los trae esta instrucción:
render_todos()
root.mainloop()