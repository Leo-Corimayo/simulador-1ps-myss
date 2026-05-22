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

class Simulador1PS_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador MySS - 1 Puesto de Servicio (Premium)")
        self.root.geometry("1420x920")
        self.root.configure(bg=COLOR_BG)

        # Variables de estado de simulación
        self.reloj = 0.0
        self.PS = 0
        self.zs = 0
        self.zs_cliente = 0
        self.cliente_en_ps = 0
        self.prox_llegada_ps = float('inf')
        self.S = 1
        self.Q = 0
        self.QA = 0
        self.QB = 0
        self.HC_A = []
        self.HC_B = []
        self.cliente_tipos = {}
        self.abandonos_programados = {}
        self.cliente_id_counter = 0
        self.historial_cola = [(0, 0)]
        self.jugando = False
        self.total_atendidos = 0
        self.total_abandonos = 0

        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=COLOR_BG)
        style.configure("Card.TFrame", background=COLOR_CARD, relief="flat")
        style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT, font=("Segoe UI", 11))
        style.configure("Header.TLabel", background=COLOR_CARD, foreground=COLOR_ACCENT, font=("Segoe UI", 12, "bold"))
        style.configure("Stat.TLabel", background=COLOR_CARD, foreground=COLOR_SUCCESS, font=("Consolas", 18, "bold"))
        
        # Estilos avanzados y espaciados para Treeview bajo el tema 'clam'
        style.configure("Treeview.Heading", background="#2C2C2C", foreground=COLOR_ACCENT, font=("Segoe UI", 11, "bold"), relief="flat")
        style.map("Treeview.Heading", background=[('active', "#3C3C3C")])
        style.configure("Treeview", background=COLOR_CARD, foreground=COLOR_TEXT, fieldbackground=COLOR_CARD, borderwidth=0, font=("Segoe UI", 11), rowheight=32)
        style.map('Treeview', background=[('selected', COLOR_ACCENT)])

        self.sidebar = ttk.Frame(self.root, style="TFrame")
        self.sidebar.pack(side="left", fill="y", padx=25, pady=25)

        self.main_content = ttk.Frame(self.root, style="TFrame")
        self.main_content.pack(side="right", expand=True, fill="both", padx=20, pady=25)

        # --- Sidebar: Configuración ---
        ttk.Label(self.sidebar, text="CONFIGURACIÓN & EVENTOS", font=("Segoe UI", 13, "bold"), foreground=COLOR_ACCENT).pack(pady=(0, 20))
        
        self.entries = {}
        
        # Helper para crear fila de input min/max + btn random (Aumentada y estilizada)
        def crear_fila_rango(parent, texto, key_min, key_max, rnd_min_range, rnd_max_range):
            frame = ttk.Frame(parent, style="TFrame")
            frame.pack(fill="x", pady=8)
            ttk.Label(frame, text=texto, width=17, font=("Segoe UI", 11)).pack(side="left")
            
            e_min = tk.Entry(frame, width=6, bg="#2C2C2C", fg=COLOR_TEXT, insertbackground=COLOR_TEXT, 
                             relief="flat", bd=0, highlightthickness=1, highlightbackground="#3E3E3E", 
                             highlightcolor=COLOR_ACCENT, font=("Consolas", 11, "bold"))
            e_min.pack(side="left", padx=5, ipady=3)
            self.entries[key_min] = e_min
            
            ttk.Label(frame, text="-", font=("Segoe UI", 11)).pack(side="left")
            
            e_max = tk.Entry(frame, width=6, bg="#2C2C2C", fg=COLOR_TEXT, insertbackground=COLOR_TEXT, 
                             relief="flat", bd=0, highlightthickness=1, highlightbackground="#3E3E3E", 
                             highlightcolor=COLOR_ACCENT, font=("Consolas", 11, "bold"))
            e_max.pack(side="left", padx=5, ipady=3)
            self.entries[key_max] = e_max
            
            def rnd():
                e_min.delete(0, tk.END)
                e_max.delete(0, tk.END)
                t_min = random.uniform(rnd_min_range[0] * 60, rnd_min_range[1] * 60)
                t_max = random.uniform(t_min + 60, rnd_max_range[1] * 60)
                e_min.insert(0, self.format_time(t_min))
                e_max.insert(0, self.format_time(t_max))
                
            tk.Button(frame, text="RND", command=rnd, bg=COLOR_ACCENT, fg=COLOR_BG, 
                      font=("Segoe UI", 9, "bold"), relief="flat", bd=0, 
                      activebackground=COLOR_SUCCESS, activeforeground=COLOR_BG, cursor="hand2").pack(side="right", padx=(5, 0), ipady=2, ipadx=4)

        # Helper para crear fila simple (Aumentada y estilizada)
        def crear_fila_simple(parent, texto, key, default, rnd_range):
            frame = ttk.Frame(parent, style="TFrame")
            frame.pack(fill="x", pady=8)
            ttk.Label(frame, text=texto, width=17, font=("Segoe UI", 11)).pack(side="left")
            
            e = tk.Entry(frame, width=14, bg="#2C2C2C", fg=COLOR_TEXT, insertbackground=COLOR_TEXT, 
                         relief="flat", bd=0, highlightthickness=1, highlightbackground="#3E3E3E", 
                         highlightcolor=COLOR_ACCENT, font=("Consolas", 11, "bold"))
            e.insert(0, default)
            e.pack(side="left", padx=5, ipady=3)
            self.entries[key] = e
            
            def rnd():
                e.delete(0, tk.END)
                if key == "cola_inicial":
                    e.insert(0, str(random.randint(int(rnd_range[0]), int(rnd_range[1]))))
                else:
                    t = random.uniform(rnd_range[0] * 60, rnd_range[1] * 60)
                    e.insert(0, self.format_time(t))
                
            tk.Button(frame, text="RND", command=rnd, bg=COLOR_ACCENT, fg=COLOR_BG, 
                      font=("Segoe UI", 9, "bold"), relief="flat", bd=0, 
                      activebackground=COLOR_SUCCESS, activeforeground=COLOR_BG, cursor="hand2").pack(side="right", padx=(5, 0), ipady=2, ipadx=4)

        crear_fila_simple(self.sidebar, "Simulación Límite:", "limite", "100.00", (50, 300))
        ttk.Separator(self.sidebar, orient='horizontal').pack(fill='x', pady=12)
        
        crear_fila_rango(self.sidebar, "T. Llegada (m):", "lleg_min", "lleg_max", (1, 5), (6, 12))
        self.entries['lleg_min'].insert(0, "3.00")
        self.entries['lleg_max'].insert(0, "7.00")
        
        crear_fila_rango(self.sidebar, "T. Servicio (m):", "serv_min", "serv_max", (1, 3), (4, 8))
        self.entries['serv_min'].insert(0, "2.00")
        self.entries['serv_max'].insert(0, "5.00")
        
        crear_fila_rango(self.sidebar, "T. Trabajo S (m):", "trab_min", "trab_max", (15, 30), (35, 90))
        self.entries['trab_min'].insert(0, "30.00")
        self.entries['trab_max'].insert(0, "60.00")
        
        crear_fila_rango(self.sidebar, "T. Descanso S (m):", "desc_min", "desc_max", (2, 5), (6, 20))
        self.entries['desc_min'].insert(0, "5.00")
        self.entries['desc_max'].insert(0, "15.00")
        
        ttk.Separator(self.sidebar, orient='horizontal').pack(fill='x', pady=12)
        crear_fila_simple(self.sidebar, "Paciencia Cola (m):", "paciencia", "10.00", (5, 20))
        crear_fila_simple(self.sidebar, "Cola Inicial:", "cola_inicial", "0", (0, 10))
        crear_fila_simple(self.sidebar, "T. Traslado ZS (m):", "traslado_zs", "0.10", (0.05, 0.5))
        
        # Selector de Modo de Cola
        frame_modo = ttk.Frame(self.sidebar, style="TFrame")
        frame_modo.pack(fill="x", pady=8)
        ttk.Label(frame_modo, text="Modo de Cola:", width=17, font=("Segoe UI", 11)).pack(side="left")
        self.combo_modo = ttk.Combobox(frame_modo, values=["Sin Prioridad", "Con Prioridad (A > B)", "Con Zona de Seguridad"], 
                                       state="readonly", width=16, font=("Segoe UI", 10))
        self.combo_modo.set("Sin Prioridad")
        self.combo_modo.pack(side="left", padx=5, ipady=2)
        
        crear_fila_simple(self.sidebar, "Prob. Cliente A (%):", "prob_a", "50.0", (10, 90))

        self.btn_run = tk.Button(self.sidebar, text="INICIAR SIMULACIÓN", command=self.start_sim, 
                                 bg=COLOR_SUCCESS, fg=COLOR_BG, font=("Segoe UI", 12, "bold"), 
                                 relief="flat", bd=0, activebackground=COLOR_ACCENT, activeforeground=COLOR_BG, 
                                 padx=20, pady=12, cursor="hand2")
        self.btn_run.pack(pady=25, fill="x")

        # --- Main: Dashboard de Estado ---
        self.dash_frame = ttk.Frame(self.main_content, style="TFrame")
        self.dash_frame.pack(fill="x")

        self.card_reloj = self.create_stat_card(self.dash_frame, "RELOJ", "0.00", COLOR_TEXT)
        self.card_q = self.create_stat_card(self.dash_frame, "EN COLA", "0", COLOR_ACCENT)
        self.card_qa = self.create_stat_card(self.dash_frame, "COLA A", "0", COLOR_SUCCESS)
        self.card_qb = self.create_stat_card(self.dash_frame, "COLA B", "0", COLOR_ACCENT)
        self.card_zs = self.create_stat_card(self.dash_frame, "ZONA SEG.", "LIBRE", COLOR_SUCCESS)
        self.card_ps = self.create_stat_card(self.dash_frame, "PUESTO", "LIBRE", COLOR_SUCCESS)
        self.card_s = self.create_stat_card(self.dash_frame, "SERVIDOR", "TRABAJANDO", COLOR_SUCCESS)
        self.card_atendidos = self.create_stat_card(self.dash_frame, "ATENDIDOS", "0", COLOR_SUCCESS)
        self.card_abandonos = self.create_stat_card(self.dash_frame, "ABANDONOS", "0", COLOR_ERROR)

        # --- Main: Representación Visual de Cola ---
        self.canvas_frame = ttk.Frame(self.main_content, style="Card.TFrame")
        self.canvas_frame.pack(fill="x", pady=15, ipady=8)
        
        self.canvas_cola = tk.Canvas(self.canvas_frame, height=90, bg=COLOR_CARD, highlightthickness=0)
        self.canvas_cola.pack(fill="x", padx=20)

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
        self.ax.set_title("Evolución de la Cola", color=COLOR_ACCENT)
        self.canvas_graph = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas_graph.get_tk_widget().pack(expand=True, fill="both", padx=5, pady=5)

        # Area Tabla (Treeview Ampliado y Espacioso)
        self.table_frame = ttk.Frame(self.bottom_frame, style="Card.TFrame")
        self.table_frame.pack(side="right", fill="both", expand=True)

        cols = ("Reloj", "Evento", "Detalle", "Estado")
        self.tree = ttk.Treeview(self.table_frame, columns=cols, show="headings", height=8)
        self.tree.heading("Reloj", text="Reloj", anchor="center")
        self.tree.heading("Evento", text="Evento", anchor="w")
        self.tree.heading("Detalle", text="Detalle", anchor="w")
        self.tree.heading("Estado", text="Estado", anchor="w")
        
        self.tree.column("Reloj", width=90, anchor="center")
        self.tree.column("Evento", width=160, anchor="w")
        self.tree.column("Detalle", width=250, anchor="w")
        self.tree.column("Estado", width=210, anchor="w")

        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


    def create_stat_card(self, parent, title, value, color=COLOR_SUCCESS):
        frame = ttk.Frame(parent, style="Card.TFrame")
        frame.pack(side="left", expand=True, fill="both", padx=4)
        ttk.Label(frame, text=title, style="Header.TLabel").pack(pady=(10, 0))
        lbl_val = tk.Label(frame, text=value, bg=COLOR_CARD, fg=color, font=("Consolas", 18, "bold"))
        lbl_val.pack(pady=(0, 10))
        return lbl_val

    def parse_to_seconds(self, val_str):
        try:
            val_str = val_str.strip()
            if "." in val_str:
                parts = val_str.split(".")
                minutes = int(parts[0]) if parts[0] else 0
                sec_str = parts[1]
                if len(sec_str) == 0:
                    seconds = 0
                elif len(sec_str) == 1:
                    seconds = int(sec_str) * 10
                else:
                    seconds = int(sec_str[:2])
                return float(minutes * 60 + seconds)
            else:
                return float(int(val_str) * 60)
        except Exception:
            return 0.0

    def format_time(self, total_seconds):
        minutes = int(total_seconds) // 60
        secs = int(total_seconds) % 60
        return f"{minutes}.{secs:02d}"

    def val(self, key):
        val_str = self.entries[key].get()
        if key in ("cola_inicial", "prob_a"):
            return float(val_str)
        return self.parse_to_seconds(val_str)

    def reset_sim(self):
        self.reloj = 0.0
        self.PS = 0
        self.zs = 0
        self.zs_cliente = 0
        self.cliente_en_ps = 0
        self.prox_llegada_ps = float('inf')
        self.S = 1
        self.Q = 0
        self.QA = 0
        self.QB = 0
        self.HC_A = []
        self.HC_B = []
        self.cliente_tipos = {}
        self.abandonos_programados = {}
        self.cliente_id_counter = 0
        self.total_atendidos = 0
        self.total_abandonos = 0
        self.tree.delete(*self.tree.get_children())
        
        es_prioridad = (self.combo_modo.get() == "Con Prioridad (A > B)")
        es_zs = (self.combo_modo.get() == "Con Zona de Seguridad")
        prob_a = self.val('prob_a') / 100.0 if es_prioridad else 0.0

        # Cargar cola inicial
        n_inicial = int(self.val('cola_inicial'))
        if n_inicial > 0:
            # El primer cliente pasa directamente al puesto de servicio
            self.cliente_id_counter = 1
            self.PS = 1
            self.cliente_en_ps = 1
            tipo = 'A' if (es_prioridad and random.random() < prob_a) else 'B'
            self.cliente_tipos[1] = tipo
            self.prox_fin_serv = self.reloj + self.generar_tiempo_servicio()
            
            # Los restantes clientes van a la cola
            if n_inicial > 1:
                paciencia = self.val('paciencia')
                for i in range(2, n_inicial + 1):
                    tipo_i = 'A' if (es_prioridad and random.random() < prob_a) else 'B'
                    self.cliente_tipos[i] = tipo_i
                    if tipo_i == 'A':
                        self.HC_A.append(i)
                        self.QA += 1
                    else:
                        self.HC_B.append(i)
                        self.QB += 1
                    self.abandonos_programados[i] = self.reloj + paciencia
                self.cliente_id_counter = n_inicial
        else:
            self.prox_fin_serv = float('inf')

        self.Q = self.QA + self.QB
        self.historial_cola = [(0.0, self.Q)]
        self.prox_llegada = self.generar_tiempo_llegada()
        self.prox_salida_serv = self.generar_tiempo_trabajo()
        self.prox_regreso_serv = float('inf')

    def generar_tiempo_llegada(self): return self.reloj + random.uniform(self.val('lleg_min'), self.val('lleg_max'))
    def generar_tiempo_servicio(self): return random.uniform(self.val('serv_min'), self.val('serv_max'))
    def generar_tiempo_trabajo(self): return self.reloj + random.uniform(self.val('trab_min'), self.val('trab_max'))
    def generar_tiempo_descanso(self): return random.uniform(self.val('desc_min'), self.val('desc_max'))

    def log(self, evento, detalle):
        es_zs = (self.combo_modo.get() == "Con Zona de Seguridad")
        if es_zs:
            estado = f"Q={self.Q} ZS={self.zs} PS={self.PS} S={self.S}"
        else:
            estado = f"Q={self.Q} PS={self.PS} S={self.S}"
        self.tree.insert("", "end", values=(self.format_time(self.reloj), evento, detalle, estado))
        self.tree.yview_moveto(1)

    def update_ui(self):
        self.card_reloj.config(text=self.format_time(self.reloj))
        es_prioridad = (self.combo_modo.get() == "Con Prioridad (A > B)")
        es_zs = (self.combo_modo.get() == "Con Zona de Seguridad")
        self.Q = self.QA + self.QB
        self.card_q.config(text=str(self.Q))
        self.card_atendidos.config(text=str(self.total_atendidos))
        self.card_abandonos.config(text=str(self.total_abandonos))
        
        if es_prioridad:
            self.card_qa.config(text=str(self.QA))
            self.card_qb.config(text=str(self.QB))
        else:
            self.card_qa.config(text="N/D")
            self.card_qb.config(text="N/D")
            
        if es_zs:
            self.card_zs.config(text=f"OCUPADA (C{self.zs_cliente})" if self.zs else "LIBRE", foreground=COLOR_WARNING if self.zs else COLOR_SUCCESS)
        else:
            self.card_zs.config(text="N/D", foreground=COLOR_TEXT)
            
        self.card_ps.config(text="OCUPADO" if self.PS == 1 else "LIBRE", foreground=COLOR_ERROR if self.PS == 1 else COLOR_SUCCESS)
        self.card_s.config(text="TRABAJANDO" if self.S == 1 else "DESCANSO", foreground=COLOR_SUCCESS if self.S == 1 else COLOR_WARNING)
        
        self.canvas_cola.delete("all")
        
        # Dibujar Secciones y Etiquetas (Aumentadas y centradas)
        self.canvas_cola.create_text(250, 15, text="COLA DE ESPERA", fill=COLOR_TEXT, font=("Segoe UI", 10, "bold"))
        self.canvas_cola.create_text(675, 15, text="ZONA DE SEGURIDAD", fill=COLOR_TEXT, font=("Segoe UI", 10, "bold"))
        self.canvas_cola.create_text(875, 15, text="PUESTO DE SERVICIO", fill=COLOR_TEXT, font=("Segoe UI", 10, "bold"))
        
        # Dibujar Cajas (Aumentadas)
        self.canvas_cola.create_rectangle(600, 30, 750, 70, outline=COLOR_WARNING, dash=(4, 4), width=2)
        self.canvas_cola.create_rectangle(800, 30, 950, 70, outline=COLOR_ERROR if self.PS == 1 else COLOR_SUCCESS, width=2)
        
        # Dibujar Clientes en Cola (Diámetro 24px)
        sorted_queue = sorted(self.HC_A + self.HC_B)
        for idx, cid in enumerate(sorted_queue[:20]):
            x = 560 - idx * 28
            if x < 10: break
            tipo = self.cliente_tipos.get(cid, 'B')
            color = COLOR_SUCCESS if (es_prioridad and tipo == 'A') else COLOR_ACCENT
            self.canvas_cola.create_oval(x, 38, x+24, 62, fill=color, outline="")
            self.canvas_cola.create_text(x+12, 50, text=f"C{cid}", fill=COLOR_BG, font=("Segoe UI", 9, "bold"))
            
        if len(sorted_queue) > 20:
            self.canvas_cola.create_text(15, 50, text=f"+{len(sorted_queue)-20}", fill=COLOR_TEXT, font=("Segoe UI", 11, "bold"))
            
        # Dibujar Cliente en ZS (Diámetro 24px)
        if es_zs and self.zs:
            self.canvas_cola.create_oval(663, 38, 687, 62, fill=COLOR_WARNING, outline="")
            self.canvas_cola.create_text(675, 50, text=f"C{self.zs_cliente}", fill=COLOR_BG, font=("Segoe UI", 9, "bold"))
            
        # Dibujar Cliente en PS (Diámetro 24px)
        if self.PS == 1 and hasattr(self, 'cliente_en_ps') and self.cliente_en_ps:
            self.canvas_cola.create_oval(863, 38, 887, 62, fill=COLOR_ERROR, outline="")
            self.canvas_cola.create_text(875, 50, text=f"C{self.cliente_en_ps}", fill=COLOR_BG, font=("Segoe UI", 9, "bold"))

        t_data, q_data = zip(*self.historial_cola)
        t_data_mins = [t / 60.0 for t in t_data]
        self.ax.clear()
        self.ax.set_facecolor(COLOR_CARD)
        self.ax.plot(t_data_mins, q_data, color=COLOR_ACCENT, linewidth=2)
        self.ax.fill_between(t_data_mins, q_data, color=COLOR_ACCENT, alpha=0.2)
        self.ax.set_title("Evolución de la Cola", color=COLOR_ACCENT)
        self.canvas_graph.draw_idle()

    def start_sim(self):
        if self.jugando: return
        self.jugando = True
        self.reset_sim()
        self.update_ui()
        self.btn_run.config(text="SIMULANDO...", bg="#3A3A3A", fg="#777777", state="disabled")
        
        def loop():
            limite = self.val('limite')
            self.log("INICIO", "Sistema listo")
            n_inicial = int(self.val('cola_inicial'))
            es_prioridad = (self.combo_modo.get() == "Con Prioridad (A > B)")
            es_zs = (self.combo_modo.get() == "Con Zona de Seguridad")
            if n_inicial > 0:
                suffix1 = f" ({self.cliente_tipos[1]})" if es_prioridad else ""
                self.log("Cola Inicial", f"Inicia con {n_inicial} clientes")
                self.log("Atención Inicial", f"C1{suffix1} pasa directo al PS")
                for i in range(2, n_inicial + 1):
                    suffix_i = f" ({self.cliente_tipos[i]})" if es_prioridad else ""
                    self.log("Cola Inicial", f"C{i}{suffix_i} entra a la cola")
            
            while self.reloj < limite:
                eventos = [
                    (self.prox_llegada, "LLEGADA"),
                    (self.prox_fin_serv, "FIN_SERV"),
                    (self.prox_salida_serv, "SALIDA_S"),
                    (self.prox_regreso_serv, "REGRESO_S")
                ]
                if es_zs and self.prox_llegada_ps != float('inf'):
                    eventos.append((self.prox_llegada_ps, "LLEGADA_ZS_PS"))
                    
                if self.abandonos_programados:
                    cid_min = min(self.abandonos_programados, key=self.abandonos_programados.get)
                    eventos.append((self.abandonos_programados[cid_min], ("ABANDONO", cid_min)))

                prox_t, ev = min(eventos, key=lambda x: x[0])
                if prox_t > limite: break
                
                self.reloj = prox_t
                
                if ev == "LLEGADA":
                    self.prox_llegada = self.generar_tiempo_llegada()
                    self.cliente_id_counter += 1
                    cid = self.cliente_id_counter
                    
                    prob_a = self.val('prob_a') / 100.0 if es_prioridad else 0.0
                    tipo = 'A' if (es_prioridad and random.random() < prob_a) else 'B'
                    self.cliente_tipos[cid] = tipo
                    suffix = f" ({tipo})" if es_prioridad else ""
                    
                    if es_zs:
                        self.Q = self.QA + self.QB
                        if self.Q == 0 and self.zs == 0 and self.PS == 0:
                            self.zs = 1
                            self.zs_cliente = cid
                            self.prox_llegada_ps = self.reloj + self.val('traslado_zs')
                            self.log("Llegada -> ZS", f"C{cid} directo a ZS")
                        else:
                            self.HC_B.append(cid)
                            self.QB += 1
                            self.Q = self.QA + self.QB
                            paciencia = self.val('paciencia')
                            self.abandonos_programados[cid] = self.reloj + paciencia
                            self.log("Llegada -> Cola", f"C{cid} a cola")
                    else:
                        if self.S == 0 or self.PS == 1:
                            if tipo == 'A':
                                self.HC_A.append(cid)
                                self.QA += 1
                            else:
                                self.HC_B.append(cid)
                                self.QB += 1
                            self.Q = self.QA + self.QB
                            paciencia = self.val('paciencia')
                            self.abandonos_programados[cid] = self.reloj + paciencia
                            self.log("Llegada", f"C{cid}{suffix} a cola")
                        else:
                            self.PS = 1
                            self.cliente_en_ps = cid
                            self.prox_fin_serv = self.reloj + self.generar_tiempo_servicio()
                            self.log("Llegada -> Directo", f"C{cid}{suffix} atendido")
                
                elif ev == "LLEGADA_ZS_PS":
                    cid = self.zs_cliente
                    self.zs = 0
                    self.zs_cliente = 0
                    self.prox_llegada_ps = float('inf')
                    self.PS = 1
                    self.cliente_en_ps = cid
                    
                    if self.S == 1:
                        self.prox_fin_serv = self.reloj + self.generar_tiempo_servicio()
                    else:
                        self.prox_fin_serv = self.prox_regreso_serv + self.generar_tiempo_servicio()
                        
                    self.log("Llegada a PS", f"C{cid} llega al PS de ZS")
                
                elif ev == "FIN_SERV":
                    self.PS = 0
                    self.cliente_en_ps = 0
                    self.prox_fin_serv = float('inf')
                    self.total_atendidos += 1
                    
                    if es_zs:
                        self.Q = self.QA + self.QB
                        if self.Q > 0:
                            cid = self.HC_B.pop(0)
                            self.QB -= 1
                            self.Q = self.QA + self.QB
                            
                            if cid in self.abandonos_programados:
                                del self.abandonos_programados[cid]
                                
                            self.zs = 1
                            self.zs_cliente = cid
                            self.prox_llegada_ps = self.reloj + self.val('traslado_zs')
                            self.log("Fin Serv -> ZS", f"C{cid} de cola a ZS")
                        else:
                            self.log("Fin Servicio", "PS libre. ZS libre.")
                    else:
                        self.Q = self.QA + self.QB
                        if self.Q > 0:
                            if self.HC_A:
                                cid = self.HC_A.pop(0)
                                self.QA -= 1
                            else:
                                cid = self.HC_B.pop(0)
                                self.QB -= 1
                            self.Q = self.QA + self.QB
                            
                            if cid in self.abandonos_programados: del self.abandonos_programados[cid]
                            self.PS = 1
                            self.cliente_en_ps = cid
                            self.prox_fin_serv = self.reloj + self.generar_tiempo_servicio()
                            suffix = f" ({self.cliente_tipos[cid]})" if es_prioridad else ""
                            self.log("Fin Servicio -> Pasa", f"C{cid}{suffix} pasa al PS")
                        else:
                            self.log("Fin Servicio", "PS queda libre")
                
                elif ev == "SALIDA_S":
                    self.S = 0
                    descanso = self.generar_tiempo_descanso()
                    self.prox_regreso_serv = self.reloj + descanso
                    self.prox_salida_serv = float('inf')
                    if self.PS == 1:
                        self.prox_fin_serv += descanso
                        self.log("Salida Servidor", "Servicio Activo Pausado")
                    else:
                        self.log("Salida Servidor", "Servidor Descansa")
                
                elif ev == "REGRESO_S":
                    self.S = 1
                    self.prox_salida_serv = self.generar_tiempo_trabajo()
                    self.prox_regreso_serv = float('inf')
                    
                    if es_zs:
                        self.log("Regreso Servidor", "Reanuda actividad")
                    else:
                        self.Q = self.QA + self.QB
                        if self.PS == 0 and self.Q > 0:
                            if self.HC_A:
                                cid = self.HC_A.pop(0)
                                self.QA -= 1
                            else:
                                cid = self.HC_B.pop(0)
                                self.QB -= 1
                            self.Q = self.QA + self.QB
                            
                            if cid in self.abandonos_programados: del self.abandonos_programados[cid]
                            self.PS = 1
                            self.cliente_en_ps = cid
                            self.prox_fin_serv = self.reloj + self.generar_tiempo_servicio()
                            suffix = f" ({self.cliente_tipos[cid]})" if es_prioridad else ""
                            self.log("Regreso Serv -> Pasa", f"C{cid}{suffix} pasa al PS")
                        else:
                            self.log("Regreso Servidor", "Reanuda actividad")
                
                elif isinstance(ev, tuple) and ev[0] == "ABANDONO":
                    cid = ev[1]
                    self.total_abandonos += 1
                    tipo = self.cliente_tipos.get(cid, 'B')
                    if tipo == 'A':
                        if cid in self.HC_A:
                            self.HC_A.remove(cid)
                            self.QA -= 1
                    else:
                        if cid in self.HC_B:
                            self.HC_B.remove(cid)
                            self.QB -= 1
                    self.Q = self.QA + self.QB
                    
                    if cid in self.abandonos_programados: del self.abandonos_programados[cid]
                    suffix = f" ({tipo})" if es_prioridad else ""
                    self.log("Abandono Cola", f"C{cid}{suffix} se fue")

                self.historial_cola.append((self.reloj, self.Q))
                self.root.after(0, self.update_ui)
                time.sleep(0.08) # Animacion

            self.jugando = False
            self.root.after(0, lambda: self.btn_run.config(text="INICIAR SIMULACIÓN", bg=COLOR_SUCCESS, fg=COLOR_BG, state="normal"))
            self.root.after(0, lambda: messagebox.showinfo("Simulación Completa", f"Fin a los {self.format_time(self.reloj)} min"))

        threading.Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = Simulador1PS_GUI(root)
    root.mainloop()
