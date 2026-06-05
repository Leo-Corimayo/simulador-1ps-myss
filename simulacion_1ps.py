import random

class Eventos:
    LLEGADA_TOTEM = "Llegada Totem"
    FIN_TOTEM = "Fin Totem"
    ABANDONO_TOTEM = "Abandono Totem"
    FIN_CONSULTORIO = "Fin Consultorio"

class SimulacionDosEtapas:
    def __init__(self):
        # Reloj y límites
        self.reloj = 0.0
        self.limite_simulacion = 480.0  # 8 horas por defecto
        
        # Parámetros del Tótem (Etapa 1)
        self.tiempo_llegada_cte = 2.0  # 2 min constantes
        self.tiempo_totem_min = 5.0
        self.tiempo_totem_max = 6.0
        self.paciencia_totem = 10.0
        
        # Parámetros de Consultorios (Etapa 2)
        self.capacidad_sala = 10
        self.tiempo_consulta_min = 15.0
        self.tiempo_consulta_max = 20.0
        self.num_consultorios = 2
        
        # Variables de estado - Etapa 1
        self.totem_ocupado = False
        self.totem_cliente = None
        self.cola_totem = []  # Lista de dicts: {"id": int, "llegada": float}
        self.abandonos_programados_totem = {}  # {cliente_id: tiempo_abandono}
        
        # Variables de estado - Etapa 2
        self.cola_consultorios = []  # Lista de IDs de clientes en sala de espera
        self.consultorios_ocupados = [False] * self.num_consultorios
        self.consultorios_clientes = [None] * self.num_consultorios
        
        # Agenda de Eventos Futuros
        self.prox_llegada_totem = 0.0  # El primer cliente llega en t=0.0 o t=2.0?
        # La consigna dice "Los clientes llegan para obtener su turno cada 2 minutos (cte)".
        # Generalmente, el primer cliente llega en t=2.0 o t=0.0. Vamos a programar la primera llegada a t=2.0.
        self.prox_fin_totem = float('inf')
        self.prox_fin_consultorios = [float('inf')] * self.num_consultorios
        
        # Contadores de estadísticas
        self.cliente_id_counter = 0
        self.abandonos_totem = 0
        self.abandonos_sala = 0
        self.clientes_atendidos = 0
        
    def generar_tiempo_totem(self):
        return random.uniform(self.tiempo_totem_min, self.tiempo_totem_max)
        
    def generar_tiempo_consulta(self):
        return random.uniform(self.tiempo_consulta_min, self.tiempo_consulta_max)
        
    def init_simulacion(self, limite=480.0):
        self.limite_simulacion = limite
        self.reloj = 0.0
        self.cliente_id_counter = 0
        self.abandonos_totem = 0
        self.abandonos_sala = 0
        self.clientes_atendidos = 0
        
        self.totem_ocupado = False
        self.totem_cliente = None
        self.cola_totem = []
        self.abandonos_programados_totem = {}
        
        self.cola_consultorios = []
        self.consultorios_ocupados = [False] * self.num_consultorios
        self.consultorios_clientes = [None] * self.num_consultorios
        
        # Primera llegada a los 2 minutos
        self.prox_llegada_totem = self.tiempo_llegada_cte
        self.prox_fin_totem = float('inf')
        self.prox_fin_consultorios = [float('inf')] * self.num_consultorios
        
        print(f"\n--- Inicio Simulación (Límite: {limite} min) ---")
        
    def get_proximo_evento(self):
        eventos = [
            (self.prox_llegada_totem, Eventos.LLEGADA_TOTEM),
            (self.prox_fin_totem, Eventos.FIN_TOTEM)
        ]
        
        for i in range(self.num_consultorios):
            eventos.append((self.prox_fin_consultorios[i], (Eventos.FIN_CONSULTORIO, i)))
            
        if self.abandonos_programados_totem:
            min_abandono_id = min(self.abandonos_programados_totem, key=self.abandonos_programados_totem.get)
            eventos.append((self.abandonos_programados_totem[min_abandono_id], (Eventos.ABANDONO_TOTEM, min_abandono_id)))
            
        # Filtrar infinitos
        eventos_validos = [e for e in eventos if e[0] < float('inf')]
        if not eventos_validos:
            return None, None
            
        proximo_tiempo, evento = min(eventos_validos, key=lambda x: x[0])
        return proximo_tiempo, evento
        
    def rutina_llegada_totem(self):
        self.prox_llegada_totem = self.reloj + self.tiempo_llegada_cte
        self.cliente_id_counter += 1
        cid = self.cliente_id_counter
        
        print(f"[{self.reloj:6.2f}] EVENTO: Llegada Cliente {cid} al Tótem")
        
        if self.totem_ocupado:
            self.cola_totem.append({"id": cid, "llegada": self.reloj})
            self.abandonos_programados_totem[cid] = self.reloj + self.paciencia_totem
            print(f"  -> Tótem ocupado. Cliente {cid} entra a la cola del Tótem (Q={len(self.cola_totem)}).")
        else:
            self.totem_ocupado = True
            self.totem_cliente = cid
            self.prox_fin_totem = self.reloj + self.generar_tiempo_totem()
            print(f"  -> Tótem libre. Cliente {cid} comienza a ser atendido en el Tótem.")
            
    def rutina_fin_totem(self):
        cid = self.totem_cliente
        print(f"[{self.reloj:6.2f}] EVENTO: Fin Servicio Tótem (Cliente {cid})")
        
        # Liberar Tótem
        self.totem_ocupado = False
        self.totem_cliente = None
        self.prox_fin_totem = float('inf')
        
        # Pasar a la etapa 2: Consultorios
        if len(self.cola_consultorios) < self.capacidad_sala:
            # Hay asiento disponible en la sala
            # Verificar si algún consultorio está libre de inmediato
            consultorio_libre = -1
            for i in range(self.num_consultorios):
                if not self.consultorios_ocupados[i]:
                    consultorio_libre = i
                    break
                    
            if consultorio_libre != -1:
                # Pasa directo a consulta
                self.consultorios_ocupados[consultorio_libre] = True
                self.consultorios_clientes[consultorio_libre] = cid
                self.prox_fin_consultorios[consultorio_libre] = self.reloj + self.generar_tiempo_consulta()
                print(f"  -> Cliente {cid} pasa directo al Consultorio {consultorio_libre+1}.")
            else:
                # Va a la sala de espera
                self.cola_consultorios.append(cid)
                print(f"  -> Cliente {cid} toma asiento en la sala de espera (Cola={len(self.cola_consultorios)}/10).")
        else:
            # Sala llena: abandona perdiendo el turno
            self.abandonos_sala += 1
            print(f"  -> [!] Sala de espera llena. Cliente {cid} abandona el lugar y pierde su turno.")
            
        # Atender al siguiente en la cola del Tótem si hay
        if self.cola_totem:
            siguiente = self.cola_totem.pop(0)
            scid = siguiente["id"]
            if scid in self.abandonos_programados_totem:
                del self.abandonos_programados_totem[scid]
                
            self.totem_ocupado = True
            self.totem_cliente = scid
            self.prox_fin_totem = self.reloj + self.generar_tiempo_totem()
            print(f"  -> Cliente {scid} de la cola del Tótem pasa a ser atendido.")
            
    def rutina_abandono_totem(self, cid):
        print(f"[{self.reloj:6.2f}] EVENTO: Abandono Fila Tótem (Cliente {cid})")
        
        # Eliminar de la cola
        indice = -1
        for i, c in enumerate(self.cola_totem):
            if c["id"] == cid:
                indice = i
                break
                
        if indice != -1:
            self.cola_totem.pop(indice)
            self.abandonos_totem += 1
            print(f"  -> Cliente {cid} perdió la paciencia y abandonó la fila del Tótem.")
            
        if cid in self.abandonos_programados_totem:
            del self.abandonos_programados_totem[cid]
            
    def rutina_fin_consultorio(self, idx):
        cid = self.consultorios_clientes[idx]
        print(f"[{self.reloj:6.2f}] EVENTO: Fin Consulta en Consultorio {idx+1} (Cliente {cid})")
        
        self.consultorios_ocupados[idx] = False
        self.consultorios_clientes[idx] = None
        self.prox_fin_consultorios[idx] = float('inf')
        self.clientes_atendidos += 1
        
        # Si hay alguien en la sala de espera, entra
        if self.cola_consultorios:
            siguiente_cid = self.cola_consultorios.pop(0)
            self.consultorios_ocupados[idx] = True
            self.consultorios_clientes[idx] = siguiente_cid
            self.prox_fin_consultorios[idx] = self.reloj + self.generar_tiempo_consulta()
            print(f"  -> Cliente {siguiente_cid} sale de la sala de espera e ingresa al Consultorio {idx+1}.")
            
    def ejecutar(self):
        while self.reloj < self.limite_simulacion:
            prox_t, ev_info = self.get_proximo_evento()
            
            if prox_t is None or prox_t > self.limite_simulacion:
                break
                
            self.reloj = prox_t
            
            if ev_info == Eventos.LLEGADA_TOTEM:
                self.rutina_llegada_totem()
            elif ev_info == Eventos.FIN_TOTEM:
                self.rutina_fin_totem()
            elif isinstance(ev_info, tuple):
                if ev_info[0] == Eventos.ABANDONO_TOTEM:
                    self.rutina_abandono_totem(ev_info[1])
                elif ev_info[0] == Eventos.FIN_CONSULTORIO:
                    self.rutina_fin_consultorio(ev_info[1])
                    
        print(f"\n--- Fin Simulación (Reloj: {self.reloj:.2f} / Límite: {self.limite_simulacion}) ---")
        print(f"Abandonos en Fila del Tótem: {self.abandonos_totem}")
        print(f"Abandonos en Sala de Espera (Sin Asiento): {self.abandonos_sala}")
        if self.abandonos_totem > self.abandonos_sala:
            print("Se producen más abandonos en: a. En la fila del tótem para obtener el turno")
        elif self.abandonos_sala > self.abandonos_totem:
            print("Se producen más abandonos en: b. En la sala de espera de los 2 consultorios")
        else:
            print("Se produce la misma cantidad de abandonos en ambos lugares")

if __name__ == "__main__":
    sim = SimulacionDosEtapas()
    sim.init_simulacion(480.0)
    sim.ejecutar()
