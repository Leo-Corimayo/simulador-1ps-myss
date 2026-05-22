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
        self.root.geometry("1300x850")
        self.root.configure(bg=COLOR_BG)

        # Variables de estado de simulación
        self.reloj = 0.0
        self.PS = 0
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

        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=COLOR_BG)
        style.configure("Card.TFrame", background=COLOR_CARD, relief="flat")
        style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT, font=("Segoe UI", 10))
        style.configure("Header.TLabel", background=COLOR_CARD, foreground=COLOR_ACCENT, font=("Segoe UI", 12, "bold"))
        style.configure("Stat.TLabel", background=COLOR_CARD, foreground=COLOR_SUCCESS, font=("Consolas", 16, "bold"))
        
        style.configure("Treeview", background=COLOR_CARD, foreground=COLOR_TEXT, fieldbackground=COLOR_CARD, borderwidth=0, rowheight=25)
        style.map('Treeview', background=[('selected', COLOR_ACCENT)])

        self.sidebar = ttk.Frame(self.root, width=350, style="TFrame")
        self.sidebar.pack(side="left", fill="y", padx=20, pady=20)

        self.main_content = ttk.Frame(self.root, style="TFrame")
        self.main_content.pack(side="right", expand=True, fill="both", padx=20, pady=20)

        # --- Sidebar: Configuración ---
        ttk.Label(self.sidebar, text="CONFIGURACIÓN & EVENTOS", font=("Segoe UI", 12, "bold"), foreground=COLOR_ACCENT).pack(pady=(0, 20))
        
        self.entries = {}
        
        # Helper para crear fila de input min/max + btn random
        def crear_fila_rango(parent, texto, key_min, key_max, rnd_min_range, rnd_max_range):
            frame = ttk.Frame(parent, style="TFrame")
            frame.pack(fill="x", pady=5)
            ttk.Label(frame, text=texto, width=15).pack(side="left")
            e_min = tk.Entry(frame, width=5, bg=COLOR_CARD, fg=COLOR_TEXT, insertbackground=COLOR_TEXT, relief="flat")
            e_min.pack(side="left", padx=5)
            self.entries[key_min] = e_min
            
            ttk.Label(frame, text="-").pack(side="left")
            e_max = tk.Entry(frame, width=5, bg=COLOR_CARD, fg=COLOR_TEXT, insertbackground=COLOR_TEXT, relief="flat")
            e_max.pack(side="left", padx=5)
            self.entries[key_max] = e_max
            
            def rnd():
                e_min.delete(0, tk.END)
                e_max.delete(0, tk.END)
                t_min = random.uniform(rnd_min_range[0] * 60, rnd_min_range[1] * 60)
                t_max = random.uniform(t_min + 60, rnd_max_range[1] * 60)
                e_min.insert(0, self.format_time(t_min))
                e_max.insert(0, self.format_time(t_max))
                
            tk.Button(frame, text="RND", command=rnd, bg=COLOR_ACCENT, fg=COLOR_BG, font=("Segoe UI", 8, "bold"), relief="flat").pack(side="right")

        def crear_fila_simple(parent, texto, key, default, rnd_range):
            frame = ttk.Frame(parent, style="TFrame")
            frame.pack(fill="x", pady=5)
            ttk.Label(frame, text=texto, width=15).pack(side="left")
            e = tk.Entry(frame, width=8, bg=COLOR_CARD, fg=COLOR_TEXT, insertbackground=COLOR_TEXT, relief="flat")
            e.insert(0, default)
            e.pack(side="left", padx=5)
            self.entries[key] = e
            
            def rnd():
                e.delete(0, tk.END)
                if key == "cola_inicial":
                    e.insert(0, str(random.randint(int(rnd_range[0]), int(rnd_range[1]))))
                else:
                    t = random.uniform(rnd_range[0] * 60, rnd_range[1] * 60)
                    e.insert(0, self.format_time(t))
                
            tk.Button(frame, text="RND", command=rnd, bg=COLOR_ACCENT, fg=COLOR_BG, font=("Segoe UI", 8, "bold"), relief="flat").pack(side="right", padx=(5, 0))

        crear_fila_simple(self.sidebar, "Simulación Límite:", "limite", "100.00", (50, 300))
        ttk.Separator(self.sidebar, orient='horizontal').pack(fill='x', pady=10)
        
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
        
        ttk.Separator(self.sidebar, orient='horizontal').pack(fill='x', pady=10)
        crear_fila_simple(self.sidebar, "Paciencia Cola (m):", "paciencia", "10.00", (5, 20))
        crear_fila_simple(self.sidebar, "Cola Inicial:", "cola_inicial", "0", (0, 10))
        
        # Selector de Modo de Cola
        frame_modo = ttk.Frame(self.sidebar, style="TFrame")
        frame_modo.pack(fill="x", pady=5)
        ttk.Label(frame_modo, text="Modo de Cola:", width=15).pack(side="left")
        self.combo_modo = ttk.Combobox(frame_modo, values=["Sin Prioridad", "Con Prioridad (A > B)"], state="readonly", width=14)
        self.combo_modo.set("Sin Prioridad")
        self.combo_modo.pack(side="left", padx=5)
        
        crear_fila_simple(self.sidebar, "Prob. Cliente A (%):", "prob_a", "50.0", (10, 90))

        self.btn_run = tk.Button(self.sidebar, text="INICIAR SIMULACIÓN", command=self.start_sim, 
                                bg=COLOR_ACCENT, fg=COLOR_BG, font=("Segoe UI", 10, "bold"), 
                                relief="flat", padx=20, pady=10, cursor="hand2")
        self.btn_run.pack(pady=20, fill="x")

        # --- Main: Dashboard de Estado ---
        self.dash_frame = ttk.Frame(self.main_content, style="TFrame")
        self.dash_frame.pack(fill="x")

        self.card_reloj = self.create_stat_card(self.dash_frame, "RELOJ", "0.00")
        self.card_q = self.create_stat_card(self.dash_frame, "EN COLA", "0")
        self.card_qa = self.create_stat_card(self.dash_frame, "COLA A (ALT)", "0")
        self.card_qb = self.create_stat_card(self.dash_frame, "COLA B (BAJ)", "0")
        self.card_ps = self.create_stat_card(self.dash_frame, "PUESTO", "LIBRE")
        self.card_s = self.create_stat_card(self.dash_frame, "SERVIDOR", "TRABAJANDO")

        # --- Main: Representación Visual de Cola ---
        self.canvas_frame = ttk.Frame(self.main_content, style="Card.TFrame")
        self.canvas_frame.pack(fill="x", pady=15, ipady=5)
        
        self.canvas_cola = tk.Canvas(self.canvas_frame, height=50, bg=COLOR_CARD, highlightthickness=0)
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

        # Area Tabla
        self.table_frame = ttk.Frame(self.bottom_frame, style="Card.TFrame")
        self.table_frame.pack(side="right", fill="both", expand=True)

        cols = ("Reloj", "Evento", "Detalle", "Estado")
        self.tree = ttk.Treeview(self.table_frame, columns=cols, show="headings", height=8)
        self.tree.heading("Reloj", text="Reloj", anchor="w")
        self.tree.heading("Evento", text="Evento", anchor="w")
        self.tree.heading("Detalle", text="Detalle", anchor="w")
        self.tree.heading("Estado", text="Estado [Q, PS, S]", anchor="w")
        
        self.tree.column("Reloj", width=60)
        self.tree.column("Evento", width=120)
        self.tree.column("Detalle", width=140)
        self.tree.column("Estado", width=120)

        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


    def create_stat_card(self, parent, title, value):
        frame = ttk.Frame(parent, style="Card.TFrame")
        frame.pack(side="left", expand=True, fill="both", padx=5)
        ttk.Label(frame, text=title, style="Header.TLabel").pack(pady=(10, 0))
        lbl_val = ttk.Label(frame, text=value, style="Stat.TLabel")
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
        self.S = 1
        self.Q = 0
        self.QA = 0
        self.QB = 0
        self.HC_A = []
        self.HC_B = []
        self.cliente_tipos = {}
        self.abandonos_programados = {}
        self.cliente_id_counter = 0
        self.tree.delete(*self.tree.get_children())
        
        es_prioridad = (self.combo_modo.get() == "Con Prioridad (A > B)")
        prob_a = self.val('prob_a') / 100.0 if es_prioridad else 0.0

        # Cargar cola inicial
        n_inicial = int(self.val('cola_inicial'))
        if n_inicial > 0:
            # El primer cliente pasa directamente al puesto de servicio
            self.cliente_id_counter = 1
            self.PS = 1
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
        estado = f"Q={self.Q} PS={self.PS} S={self.S}"
        self.tree.insert("", "end", values=(self.format_time(self.reloj), evento, detalle, estado))
        self.tree.yview_moveto(1)

    def update_ui(self):
        self.card_reloj.config(text=self.format_time(self.reloj))
        es_prioridad = (self.combo_modo.get() == "Con Prioridad (A > B)")
        self.Q = self.QA + self.QB
        self.card_q.config(text=str(self.Q))
        
        if es_prioridad:
            self.card_qa.config(text=str(self.QA))
            self.card_qb.config(text=str(self.QB))
        else:
            self.card_qa.config(text="N/D")
            self.card_qb.config(text="N/D")
            
        self.card_ps.config(text="OCUPADO" if self.PS == 1 else "LIBRE", foreground=COLOR_ERROR if self.PS == 1 else COLOR_SUCCESS)
        self.card_s.config(text="TRABAJANDO" if self.S == 1 else "DESCANSO", foreground=COLOR_SUCCESS if self.S == 1 else COLOR_WARNING)
        
        self.canvas_cola.delete("all")
        sorted_queue = sorted(self.HC_A + self.HC_B)
        for i, cid in enumerate(sorted_queue[:30]):
            x = 10 + i * 25
            tipo = self.cliente_tipos.get(cid, 'B')
            color = COLOR_SUCCESS if (es_prioridad and tipo == 'A') else COLOR_ACCENT
            self.canvas_cola.create_oval(x, 10, x+20, 30, fill=color, outline="")
            
        if len(sorted_queue) > 30:
            self.canvas_cola.create_text(800, 20, text=f"+{len(sorted_queue)-30}", fill=COLOR_TEXT, font=("Segoe UI", 12, "bold"))

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
        self.btn_run.config(text="SIMULANDO...", state="disabled")
        
        def loop():
            limite = self.val('limite')
            self.log("INICIO", "Sistema listo")
            n_inicial = int(self.val('cola_inicial'))
            es_prioridad = (self.combo_modo.get() == "Con Prioridad (A > B)")
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
                        self.prox_fin_serv = self.reloj + self.generar_tiempo_servicio()
                        self.log("Llegada -> Directo", f"C{cid}{suffix} atendido")
                
                elif ev == "FIN_SERV":
                    self.PS = 0
                    self.prox_fin_serv = float('inf')
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
                        self.prox_fin_serv = self.reloj + self.generar_tiempo_servicio()
                        suffix = f" ({self.cliente_tipos[cid]})" if es_prioridad else ""
                        self.log("Regreso Serv -> Pasa", f"C{cid}{suffix} pasa al PS")
                    else:
                        self.log("Regreso Servidor", "Reanuda actividad")
                
                elif isinstance(ev, tuple) and ev[0] == "ABANDONO":
                    cid = ev[1]
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
            self.root.after(0, lambda: self.btn_run.config(text="INICIAR SIMULACIÓN", state="normal"))
            self.root.after(0, lambda: messagebox.showinfo("Simulación Completa", f"Fin a los {self.format_time(self.reloj)} min"))

        threading.Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = Simulador1PS_GUI(root)
    root.mainloop()
