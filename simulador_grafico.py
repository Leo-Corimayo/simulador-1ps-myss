import tkinter as tk
from tkinter import ttk, messagebox
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time

# Configuración de Colores Premium
COLOR_BG = "#121212"
COLOR_CARD = "#1E1E1E"
COLOR_ACCENT = "#BB86FC"
COLOR_TEXT = "#E1E1E1"
COLOR_SUCCESS = "#03DAC6"
COLOR_ERROR = "#CF6679"
COLOR_WARNING = "#F2994A"

class SimuladorDosEtapas_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador Clínico - Doble Etapa (Tótem y 2 Consultorios)")
        self.root.geometry("1420x920")
        self.root.configure(bg=COLOR_BG)

        # Variables de estado de simulación
        self.reloj = 0.0
        self.totem_ocupado = False
        self.totem_cliente = None
        self.cola_totem = []  # Lista de dicts: {"id": id, "llegada": tiempo}
        self.abandonos_programados_totem = {}
        
        self.cola_consultorios = []  # Lista de IDs
        self.consultorios_ocupados = [False, False]
        self.consultorios_clientes = [None, None]
        
        self.prox_llegada_totem = 2.0
        self.prox_fin_totem = float('inf')
        self.prox_fin_consultorios = [float('inf'), float('inf')]
        
        self.cliente_id_counter = 0
        self.abandonos_totem = 0
        self.abandonos_sala = 0
        self.clientes_atendidos = 0
        
        # Historial para gráficos
        self.historial_tiempos = [0.0]
        self.historial_cola_totem = [0]
        self.historial_cola_sala = [0]
        
        self.jugando = False
        self.velocidad = 0.05  # Retardo en segundos por paso

        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=COLOR_BG)
        style.configure("Card.TFrame", background=COLOR_CARD, relief="flat")
        style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT, font=("Segoe UI", 11))
        style.configure("Header.TLabel", background=COLOR_CARD, foreground=COLOR_ACCENT, font=("Segoe UI", 11, "bold"))
        
        # Estilos avanzados para el Treeview
        style.configure("Treeview.Heading", background="#2C2C2C", foreground=COLOR_ACCENT, font=("Segoe UI", 11, "bold"), relief="flat")
        style.map("Treeview.Heading", background=[('active', "#3C3C3C")])
        style.configure("Treeview", background=COLOR_CARD, foreground=COLOR_TEXT, fieldbackground=COLOR_CARD, borderwidth=0, font=("Segoe UI", 10), rowheight=28)
        style.map('Treeview', background=[('selected', COLOR_ACCENT)])

        self.sidebar = ttk.Frame(self.root, style="TFrame")
        self.sidebar.pack(side="left", fill="y", padx=25, pady=25)

        self.main_content = ttk.Frame(self.root, style="TFrame")
        self.main_content.pack(side="right", expand=True, fill="both", padx=20, pady=25)

        # --- Sidebar: Configuración ---
        ttk.Label(self.sidebar, text="CONFIGURACIÓN SIMULACIÓN", font=("Segoe UI", 13, "bold"), foreground=COLOR_ACCENT).pack(pady=(0, 20))
        
        self.entries = {}
        
        def crear_fila_simple(parent, texto, key, default):
            frame = ttk.Frame(parent, style="TFrame")
            frame.pack(fill="x", pady=6)
            ttk.Label(frame, text=texto, width=19, font=("Segoe UI", 11)).pack(side="left")
            e = tk.Entry(frame, width=12, bg="#2C2C2C", fg=COLOR_TEXT, insertbackground=COLOR_TEXT, 
                             relief="flat", bd=0, highlightthickness=1, highlightbackground="#3E3E3E", 
                             highlightcolor=COLOR_ACCENT, font=("Consolas", 11, "bold"))
            e.insert(0, default)
            e.pack(side="left", padx=5, ipady=3)
            self.entries[key] = e

        crear_fila_simple(self.sidebar, "Duración (min):", "limite", "480.0")
        crear_fila_simple(self.sidebar, "Llegada Tótem (cte):", "llegada_cte", "2.0")
        crear_fila_simple(self.sidebar, "Tótem Min (m):", "totem_min", "5.0")
        crear_fila_simple(self.sidebar, "Tótem Max (m):", "totem_max", "6.0")
        crear_fila_simple(self.sidebar, "Paciencia Tótem (cte):", "paciencia_cte", "10.0")
        crear_fila_simple(self.sidebar, "Asientos Sala:", "capacidad_sala", "10")
        crear_fila_simple(self.sidebar, "Consulta Min (m):", "consulta_min", "15.0")
        crear_fila_simple(self.sidebar, "Consulta Max (m):", "consulta_max", "20.0")
        
        # Control de velocidad
        frame_vel = ttk.Frame(self.sidebar, style="TFrame")
        frame_vel.pack(fill="x", pady=8)
        ttk.Label(frame_vel, text="Paso Animación:", width=19, font=("Segoe UI", 11)).pack(side="left")
        self.combo_vel = ttk.Combobox(frame_vel, values=["Lento", "Medio", "Rápido", "Instantáneo"], 
                                       state="readonly", width=11, font=("Segoe UI", 10))
        self.combo_vel.set("Medio")
        self.combo_vel.pack(side="left", padx=5, ipady=2)

        self.btn_run = tk.Button(self.sidebar, text="INICIAR SIMULACIÓN", command=self.start_sim, 
                                 bg=COLOR_SUCCESS, fg=COLOR_BG, font=("Segoe UI", 12, "bold"), 
                                 relief="flat", bd=0, activebackground=COLOR_ACCENT, activeforeground=COLOR_BG, 
                                 padx=20, pady=12, cursor="hand2")
        self.btn_run.pack(pady=20, fill="x")

        # --- Main: Dashboard de Estado ---
        self.dash_frame = ttk.Frame(self.main_content, style="TFrame")
        self.dash_frame.pack(fill="x")

        self.card_reloj = self.create_stat_card(self.dash_frame, "RELOJ", "0.00", COLOR_TEXT)
        self.card_q_totem = self.create_stat_card(self.dash_frame, "COLA TÓTEM", "0", COLOR_ACCENT)
        self.card_totem_status = self.create_stat_card(self.dash_frame, "TÓTEM", "LIBRE", COLOR_SUCCESS)
        self.card_q_sala = self.create_stat_card(self.dash_frame, "SALA ESPERA", "0 / 10", COLOR_WARNING)
        self.card_c1 = self.create_stat_card(self.dash_frame, "CONSULT. 1", "LIBRE", COLOR_SUCCESS)
        self.card_c2 = self.create_stat_card(self.dash_frame, "CONSULT. 2", "LIBRE", COLOR_SUCCESS)
        self.card_ab_totem = self.create_stat_card(self.dash_frame, "AB. TÓTEM", "0", COLOR_ERROR)
        self.card_ab_sala = self.create_stat_card(self.dash_frame, "AB. SALA", "0", COLOR_ERROR)
        self.card_mayor_ab = self.create_stat_card(self.dash_frame, "MAYOR ABANDONO", "-", COLOR_WARNING)

        # --- Main: Representación Visual del Flujo ---
        self.canvas_frame = ttk.Frame(self.main_content, style="Card.TFrame")
        self.canvas_frame.pack(fill="x", pady=15, ipady=8)
        
        self.canvas_flujo = tk.Canvas(self.canvas_frame, height=130, bg=COLOR_CARD, highlightthickness=0)
        self.canvas_flujo.pack(fill="x", padx=20)

        # --- Main: Gráfico y Tabla ---
        self.bottom_frame = ttk.Frame(self.main_content, style="TFrame")
        self.bottom_frame.pack(expand=True, fill="both")
        
        # Area Grafico
        self.graph_frame = ttk.Frame(self.bottom_frame, style="Card.TFrame")
        self.graph_frame.pack(side="left", expand=True, fill="both", padx=(0, 10))
        
        self.fig, self.ax = plt.subplots(figsize=(4, 3), dpi=100)
        self.fig.patch.set_facecolor(COLOR_CARD)
        self.ax.set_facecolor(COLOR_CARD)
        self.ax.spines['bottom'].set_color(COLOR_TEXT)
        self.ax.spines['left'].set_color(COLOR_TEXT)
        self.ax.tick_params(axis='x', colors=COLOR_TEXT)
        self.ax.tick_params(axis='y', colors=COLOR_TEXT)
        self.ax.set_title("Ocupación de Colas", color=COLOR_ACCENT)
        self.canvas_graph = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas_graph.get_tk_widget().pack(expand=True, fill="both", padx=5, pady=5)

        # Area Tabla
        self.table_frame = ttk.Frame(self.bottom_frame, style="Card.TFrame")
        self.table_frame.pack(side="right", fill="both", expand=True)

        cols = ("Reloj", "Evento", "Detalle", "Estado")
        self.tree = ttk.Treeview(self.table_frame, columns=cols, show="headings", height=8)
        self.tree.heading("Reloj", text="Reloj", anchor="center")
        self.tree.heading("Evento", text="Evento", anchor="w")
        self.tree.heading("Detalle", text="Detalle", anchor="w")
        self.tree.heading("Estado", text="Estado", anchor="w")
        
        self.tree.column("Reloj", width=80, anchor="center")
        self.tree.column("Evento", width=140, anchor="w")
        self.tree.column("Detalle", width=260, anchor="w")
        self.tree.column("Estado", width=220, anchor="w")

        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_stat_card(self, parent, title, value, color=COLOR_SUCCESS):
        frame = ttk.Frame(parent, style="Card.TFrame")
        frame.pack(side="left", expand=True, fill="both", padx=4)
        ttk.Label(frame, text=title, style="Header.TLabel").pack(pady=(10, 0))
        lbl_val = tk.Label(frame, text=value, bg=COLOR_CARD, fg=color, font=("Consolas", 15, "bold"))
        lbl_val.pack(pady=(0, 10))
        return lbl_val

    def val(self, key):
        return float(self.entries[key].get())

    def reset_sim(self):
        self.reloj = 0.0
        self.totem_ocupado = False
        self.totem_cliente = None
        self.cola_totem = []
        self.abandonos_programados_totem = {}
        
        self.cola_consultorios = []
        self.consultorios_ocupados = [False, False]
        self.consultorios_clientes = [None, None]
        
        self.prox_llegada_totem = self.val("llegada_cte")
        self.prox_fin_totem = float('inf')
        self.prox_fin_consultorios = [float('inf'), float('inf')]
        
        self.cliente_id_counter = 0
        self.abandonos_totem = 0
        self.abandonos_sala = 0
        self.clientes_atendidos = 0
        
        self.historial_tiempos = [0.0]
        self.historial_cola_totem = [0]
        self.historial_cola_sala = [0]
        
        self.tree.delete(*self.tree.get_children())
        
        vel_mode = self.combo_vel.get()
        if vel_mode == "Lento":
            self.velocidad = 0.2
        elif vel_mode == "Medio":
            self.velocidad = 0.05
        elif vel_mode == "Rápido":
            self.velocidad = 0.005
        else:
            self.velocidad = 0.0  # Instantáneo

    def log(self, evento, detalle):
        estado = f"Q_T={len(self.cola_totem)} Sala={len(self.cola_consultorios)}/10"
        self.tree.insert("", "end", values=(f"{self.reloj:.2f}", evento, detalle, estado))
        self.tree.yview_moveto(1)

    def draw_elements(self):
        self.canvas_flujo.delete("all")
        
        # Nombres de Zonas
        self.canvas_flujo.create_text(130, 15, text="FILA TÓTEM", fill=COLOR_TEXT, font=("Segoe UI", 9, "bold"))
        self.canvas_flujo.create_text(320, 15, text="TÓTEM", fill=COLOR_TEXT, font=("Segoe UI", 9, "bold"))
        self.canvas_flujo.create_text(570, 15, text="SALA DE ESPERA (ASIENTOS)", fill=COLOR_TEXT, font=("Segoe UI", 9, "bold"))
        self.canvas_flujo.create_text(870, 15, text="CONSULTORIOS", fill=COLOR_TEXT, font=("Segoe UI", 9, "bold"))
        
        # Marcos para estaciones
        self.canvas_flujo.create_rectangle(270, 35, 370, 85, outline=COLOR_ACCENT, width=2)
        self.canvas_flujo.create_rectangle(440, 35, 700, 95, outline=COLOR_WARNING, dash=(4, 2), width=1)
        self.canvas_flujo.create_rectangle(780, 25, 960, 55, outline=COLOR_SUCCESS if not self.consultorios_ocupados[0] else COLOR_ERROR, width=2)
        self.canvas_flujo.create_rectangle(780, 65, 960, 95, outline=COLOR_SUCCESS if not self.consultorios_ocupados[1] else COLOR_ERROR, width=2)
        
        # Clientes en fila Tótem
        for idx, item in enumerate(self.cola_totem[:10]):
            x = 240 - idx * 24
            self.canvas_flujo.create_oval(x, 48, x + 18, 66, fill=COLOR_ACCENT, outline="")
            self.canvas_flujo.create_text(x + 9, 57, text=f"{item['id']}", fill=COLOR_BG, font=("Segoe UI", 8, "bold"))
            
        if len(self.cola_totem) > 10:
            self.canvas_flujo.create_text(15, 57, text=f"+{len(self.cola_totem)-10}", fill=COLOR_TEXT, font=("Segoe UI", 9, "bold"))
            
        # Cliente en Tótem
        if self.totem_ocupado and self.totem_cliente:
            self.canvas_flujo.create_oval(311, 48, 329, 66, fill=COLOR_SUCCESS, outline="")
            self.canvas_flujo.create_text(320, 57, text=f"C{self.totem_cliente}", fill=COLOR_BG, font=("Segoe UI", 8, "bold"))
            
        # Asientos en sala de espera (10 asientos)
        for i in range(10):
            row = i // 5
            col = i % 5
            x = 460 + col * 46
            y = 45 + row * 26
            
            # Dibujar asiento vacío o lleno
            if i < len(self.cola_consultorios):
                cid = self.cola_consultorios[i]
                self.canvas_flujo.create_rectangle(x, y, x + 35, y + 20, fill=COLOR_WARNING, outline="")
                self.canvas_flujo.create_text(x + 17, y + 10, text=f"C{cid}", fill=COLOR_BG, font=("Segoe UI", 8, "bold"))
            else:
                self.canvas_flujo.create_rectangle(x, y, x + 35, y + 20, outline="#555555", width=1)
                self.canvas_flujo.create_text(x + 17, y + 10, text="L", fill="#555555", font=("Segoe UI", 7))
                
        # Consultorios
        if self.consultorios_ocupados[0]:
            self.canvas_flujo.create_oval(800, 31, 818, 49, fill=COLOR_ERROR, outline="")
            self.canvas_flujo.create_text(809, 40, text=f"C{self.consultorios_clientes[0]}", fill=COLOR_BG, font=("Segoe UI", 8, "bold"))
            self.canvas_flujo.create_text(890, 40, text="Cons. 1 Ocup.", fill=COLOR_ERROR, font=("Segoe UI", 8, "bold"))
        else:
            self.canvas_flujo.create_text(870, 40, text="Cons. 1 Libre", fill=COLOR_SUCCESS, font=("Segoe UI", 8))
            
        if self.consultorios_ocupados[1]:
            self.canvas_flujo.create_oval(800, 71, 818, 89, fill=COLOR_ERROR, outline="")
            self.canvas_flujo.create_text(809, 80, text=f"C{self.consultorios_clientes[1]}", fill=COLOR_BG, font=("Segoe UI", 8, "bold"))
            self.canvas_flujo.create_text(890, 80, text="Cons. 2 Ocup.", fill=COLOR_ERROR, font=("Segoe UI", 8, "bold"))
        else:
            self.canvas_flujo.create_text(870, 80, text="Cons. 2 Libre", fill=COLOR_SUCCESS, font=("Segoe UI", 8))

    def update_ui(self):
        self.card_reloj.config(text=f"{self.reloj:.2f}")
        self.card_q_totem.config(text=str(len(self.cola_totem)))
        self.card_totem_status.config(
            text="OCUPADO" if self.totem_ocupado else "LIBRE",
            foreground=COLOR_ERROR if self.totem_ocupado else COLOR_SUCCESS
        )
        self.card_q_sala.config(text=f"{len(self.cola_consultorios)} / 10")
        
        self.card_c1.config(
            text=f"C{self.consultorios_clientes[0]} ({self.prox_fin_consultorios[0] - self.reloj:.1f}m)" if self.consultorios_ocupados[0] else "LIBRE",
            foreground=COLOR_ERROR if self.consultorios_ocupados[0] else COLOR_SUCCESS
        )
        self.card_c2.config(
            text=f"C{self.consultorios_clientes[1]} ({self.prox_fin_consultorios[1] - self.reloj:.1f}m)" if self.consultorios_ocupados[1] else "LIBRE",
            foreground=COLOR_ERROR if self.consultorios_ocupados[1] else COLOR_SUCCESS
        )
        
        self.card_ab_totem.config(text=str(self.abandonos_totem))
        self.card_ab_sala.config(text=str(self.abandonos_sala))
        
        if self.abandonos_totem > self.abandonos_sala:
            self.card_mayor_ab.config(text="FILA TÓTEM", fg=COLOR_ERROR)
        elif self.abandonos_sala > self.abandonos_totem:
            self.card_mayor_ab.config(text="SALA ESPERA", fg=COLOR_ERROR)
        else:
            self.card_mayor_ab.config(text="IGUALES", fg=COLOR_TEXT)
            
        self.draw_elements()
        
        # Gráficos
        self.ax.clear()
        self.ax.set_facecolor(COLOR_CARD)
        self.ax.plot(self.historial_tiempos, self.historial_cola_totem, label="Fila Tótem", color=COLOR_ACCENT, linewidth=1.5)
        self.ax.plot(self.historial_tiempos, self.historial_cola_sala, label="Sala de Espera", color=COLOR_WARNING, linewidth=1.5)
        self.ax.legend(facecolor=COLOR_CARD, labelcolor=COLOR_TEXT)
        self.ax.set_title("Ocupación de Colas", color=COLOR_ACCENT)
        self.canvas_graph.draw_idle()

    def start_sim(self):
        if self.jugando: return
        self.jugando = True
        self.reset_sim()
        self.update_ui()
        self.btn_run.config(text="SIMULANDO...", bg="#3A3A3A", fg="#777777", state="disabled")
        
        def loop():
            limite = self.val("limite")
            self.log("INICIO", "Sistema listo")
            
            while self.reloj < limite:
                # Armar lista de eventos
                eventos = [
                    (self.prox_llegada_totem, "LLEGADA_TOTEM"),
                    (self.prox_fin_totem, "FIN_TOTEM")
                ]
                for i in range(2):
                    eventos.append((self.prox_fin_consultorios[i], f"FIN_CONSULTORIO_{i}"))
                    
                if self.abandonos_programados_totem:
                    min_cid = min(self.abandonos_programados_totem, key=self.abandonos_programados_totem.get)
                    eventos.append((self.abandonos_programados_totem[min_cid], f"ABANDONO_TOTEM_{min_cid}"))
                    
                prox_t, ev = min(eventos, key=lambda x: x[0])
                if prox_t > limite: break
                
                self.reloj = prox_t
                
                if ev == "LLEGADA_TOTEM":
                    self.prox_llegada_totem = self.reloj + self.val("llegada_cte")
                    self.cliente_id_counter += 1
                    cid = self.cliente_id_counter
                    
                    if self.totem_ocupado:
                        self.cola_totem.append({"id": cid, "llegada": self.reloj})
                        self.abandonos_programados_totem[cid] = self.reloj + self.val("paciencia_cte")
                        self.log("Llegada Tótem", f"Cliente {cid} entra a la fila")
                    else:
                        self.totem_ocupado = True
                        self.totem_cliente = cid
                        self.prox_fin_totem = self.reloj + random.uniform(self.val("totem_min"), self.val("totem_max"))
                        self.log("Llegada Tótem", f"Cliente {cid} pasa directo al Tótem")
                        
                elif ev == "FIN_TOTEM":
                    cid = self.totem_cliente
                    self.totem_ocupado = False
                    self.totem_cliente = None
                    self.prox_fin_totem = float('inf')
                    
                    # Intentar meter en la etapa 2
                    if len(self.cola_consultorios) < self.val("capacidad_sala"):
                        # Buscar si hay consultorio libre
                        consultorio_libre = -1
                        for idx in range(2):
                            if not self.consultorios_ocupados[idx]:
                                consultorio_libre = idx
                                break
                        if consultorio_libre != -1:
                            self.consultorios_ocupados[consultorio_libre] = True
                            self.consultorios_clientes[consultorio_libre] = cid
                            self.prox_fin_consultorios[consultorio_libre] = self.reloj + random.uniform(self.val("consulta_min"), self.val("consulta_max"))
                            self.log("Fin Tótem", f"C{cid} pasa directo a Consultorio {consultorio_libre+1}")
                        else:
                            self.cola_consultorios.append(cid)
                            self.log("Fin Tótem", f"C{cid} va a la sala de espera")
                    else:
                        self.abandonos_sala += 1
                        self.log("Abandono Sala", f"C{cid} se va por sala llena")
                        
                    # Siguiente en el tótem
                    if self.cola_totem:
                        siguiente = self.cola_totem.pop(0)
                        scid = siguiente["id"]
                        if scid in self.abandonos_programados_totem:
                            del self.abandonos_programados_totem[scid]
                        self.totem_ocupado = True
                        self.totem_cliente = scid
                        self.prox_fin_totem = self.reloj + random.uniform(self.val("totem_min"), self.val("totem_max"))
                        
                elif ev.startswith("ABANDONO_TOTEM_"):
                    cid = int(ev.split("_")[-1])
                    indice = -1
                    for idx, c in enumerate(self.cola_totem):
                        if c["id"] == cid:
                            indice = idx
                            break
                    if indice != -1:
                        self.cola_totem.pop(indice)
                        self.abandonos_totem += 1
                        self.log("Abandono Tótem", f"Cliente {cid} cansado de esperar en fila")
                    if cid in self.abandonos_programados_totem:
                        del self.abandonos_programados_totem[cid]
                        
                elif ev.startswith("FIN_CONSULTORIO_"):
                    idx = int(ev.split("_")[-1])
                    cid = self.consultorios_clientes[idx]
                    self.consultorios_ocupados[idx] = False
                    self.consultorios_clientes[idx] = None
                    self.prox_fin_consultorios[idx] = float('inf')
                    self.clientes_atendidos += 1
                    self.log("Fin Consulta", f"C{cid} sale de Consultorio {idx+1}")
                    
                    if self.cola_consultorios:
                        scid = self.cola_consultorios.pop(0)
                        self.consultorios_ocupados[idx] = True
                        self.consultorios_clientes[idx] = scid
                        self.prox_fin_consultorios[idx] = self.reloj + random.uniform(self.val("consulta_min"), self.val("consulta_max"))
                        self.log("Entrada Consulta", f"C{scid} de la sala entra a Consultorio {idx+1}")

                self.historial_tiempos.append(self.reloj)
                self.historial_cola_totem.append(len(self.cola_totem))
                self.historial_cola_sala.append(len(self.cola_consultorios))
                
                if self.velocidad > 0:
                    self.root.after(0, self.update_ui)
                    time.sleep(self.velocidad)
            
            # Fin del bucle
            self.root.after(0, self.update_ui)
            self.jugando = False
            self.root.after(0, lambda: self.btn_run.config(text="INICIAR SIMULACIÓN", bg=COLOR_SUCCESS, fg=COLOR_BG, state="normal"))
            
            res_str = (
                f"Simulación finalizada en {self.reloj:.2f} min.\n\n"
                f"Abandonos en Fila Tótem: {self.abandonos_totem}\n"
                f"Abandonos en Sala de Espera: {self.abandonos_sala}\n\n"
                f"Mayor volumen de abandonos: "
                f"{'La Fila del Tótem' if self.abandonos_totem > self.abandonos_sala else 'La Sala de Espera' if self.abandonos_sala > self.abandonos_totem else 'Iguales'}"
            )
            self.root.after(0, lambda: messagebox.showinfo("Resultados Finales", res_str))

        threading.Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorDosEtapas_GUI(root)
    root.mainloop()
