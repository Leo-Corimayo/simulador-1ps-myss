import random

# Definición de nombres de eventos para legibilidad
class Eventos:
    LLEGADA_CLIENTE = "Llegada Cliente"
    FIN_SERVICIO = "Fin de Servicio"
    SALIDA_SERVIDOR = "Salida Servidor"
    REGRESO_SERVIDOR = "Regreso Servidor"
    ABANDONO_COLA = "Abandono"

class Simulacion1PS:
    def __init__(self):
        # 1. Variables de Estado
        self.reloj = 0.0
        self.PS = 0    # 0 = Libre, 1 = Ocupado
        self.S = 1     # 1 = Trabajando, 0 = Ausente/Descansando
        self.Q = 0
        self.HC = []   # Lista de diccionarios que guarda id de cliente y hora exacta de llegada
        
        self.cliente_id_counter = 0

        # Parámetros de la simulación
        self.limite_simulacion = 0.0
        self.tiempo_max_espera = 10.0  # Límite de paciencia en cola (ej. 10 min)
        
        # 2. Lista de Eventos Futuros (Agenda)
        # Se inician en infinito (float('inf')), indicando que no están programados
        self.proxima_llegada_cliente = float('inf')
        self.proximo_fin_servicio = float('inf')
        self.proxima_salida_servidor = float('inf')
        self.proximo_regreso_servidor = float('inf')
        
        # Abandonos programados: Diccionario {cliente_id: tiempo_abandono}
        # Permite rastrear un abandono por cada cliente en cola
        self.abandonos_programados = {}

    # --- Generadores de tiempos aleatorios ---
    def generar_tiempo_llegada(self):
        return random.expovariate(1/5.0)  # Llega 1 cliente cada 5 min aprox

    def generar_tiempo_servicio(self):
        return random.uniform(2.0, 5.0)   # Tarda entre 2 y 5 min en atender

    def generar_tiempo_trabajo(self):
        return random.uniform(30.0, 90.0) # Trabaja entre 30 y 90 min antes de descansar

    def generar_tiempo_descanso(self):
        return random.uniform(5.0, 15.0)  # Descansa entre 5 y 15 min

    # --- Inicialización ---
    def init_simulacion(self, limite, q_inicial, ps_inicial, s_inicial):
        self.limite_simulacion = limite
        self.Q = q_inicial
        self.PS = ps_inicial
        self.S = s_inicial
        self.reloj = 0.0

        print(f"\n--- Inicio Simulación (Límite: {limite} min) ---")

        # Configurar estado inicial según los parámetros provistos
        if self.Q > 0:
            for _ in range(self.Q):
                self.cliente_id_counter += 1
                self.HC.append({"id": self.cliente_id_counter, "llegada": self.reloj})
                self.abandonos_programados[self.cliente_id_counter] = self.reloj + self.tiempo_max_espera

        if self.PS == 1:
            self.proximo_fin_servicio = self.reloj + self.generar_tiempo_servicio()

        if self.S == 1:
            self.proxima_salida_servidor = self.reloj + self.generar_tiempo_trabajo()
        else:
            self.proximo_regreso_servidor = self.reloj + self.generar_tiempo_descanso()

        # Programa la 1ra Llegada de Cliente
        self.proxima_llegada_cliente = self.reloj + self.generar_tiempo_llegada()

    # --- Búsqueda del Próximo Evento ---
    def get_proximo_evento(self):
        # Reunimos todos los eventos en una lista de tuplas (tiempo, nombre_evento)
        eventos = [
            (self.proxima_llegada_cliente, Eventos.LLEGADA_CLIENTE),
            (self.proximo_fin_servicio, Eventos.FIN_SERVICIO),
            (self.proxima_salida_servidor, Eventos.SALIDA_SERVIDOR),
            (self.proximo_regreso_servidor, Eventos.REGRESO_SERVIDOR)
        ]
        
        # Buscar en la lista de abandonos cuál es el próximo en ocurrir
        if self.abandonos_programados:
            min_abandono_id = min(self.abandonos_programados, key=self.abandonos_programados.get)
            evento_abandono_tuple = (Eventos.ABANDONO_COLA, min_abandono_id)
            eventos.append((self.abandonos_programados[min_abandono_id], evento_abandono_tuple))
            
        # Filtrar los eventos que están en infinito y encontrar el de menor hora
        eventos_validos = [e for e in eventos if e[0] < float('inf')]
        if not eventos_validos:
            return None, None
            
        proximo_tiempo, evento = min(eventos_validos, key=lambda x: x[0])
        return proximo_tiempo, evento

    # --- 4. Subrutinas por Evento ---
    def rutina_llegada_cliente(self):
        print(f"[{self.reloj:6.2f}] EVENTO: Llegada Cliente")
        # Programar próxima llegada
        self.proxima_llegada_cliente = self.reloj + self.generar_tiempo_llegada()
        
        self.cliente_id_counter += 1
        cid = self.cliente_id_counter
        
        # Lógica: Si S=0 o PS=1 -> sumar a Q, anotar HC y programar Abandono
        if self.S == 0 or self.PS == 1:
            self.Q += 1
            self.HC.append({"id": cid, "llegada": self.reloj})
            self.abandonos_programados[cid] = self.reloj + self.tiempo_max_espera
            print(f"  -> Servidor ocupado/ausente. Cliente {cid} entra a la cola (Q={self.Q}).")
        # Lógica: Si S=1 y PS=0 -> PS=1 y programar Fin Servicio
        elif self.S == 1 and self.PS == 0:
            self.PS = 1
            self.proximo_fin_servicio = self.reloj + self.generar_tiempo_servicio()
            print(f"  -> Servidor libre. Cliente {cid} pasa a ser atendido directamente.")
            
    def rutina_fin_servicio(self):
        print(f"[{self.reloj:6.2f}] EVENTO: Fin de Servicio")
        # Lógica: PS=0. 
        self.PS = 0
        self.proximo_fin_servicio = float('inf')
        
        # Lógica: Si Q>0 -> Q-1, PS=1, borrar su HC, cancelar su Abandono y programar Fin Servicio
        if self.Q > 0:
            self.Q -= 1
            cliente = self.HC.pop(0) # Se atiende al primero en llegar (FIFO)
            cid = cliente["id"]
            self.PS = 1
            
            # CANCELAR su evento de Abandono
            if cid in self.abandonos_programados:
                del self.abandonos_programados[cid]
                
            self.proximo_fin_servicio = self.reloj + self.generar_tiempo_servicio()
            espera = self.reloj - cliente['llegada']
            print(f"  -> El Cliente {cid} deja la cola y entra a servicio. (Q={self.Q}). Esperó: {espera:.2f} min.")
        else:
            print("  -> No hay clientes esperando. El Puesto de Servicio queda libre.")

    def rutina_salida_servidor(self):
        print(f"[{self.reloj:6.2f}] EVENTO: Salida Servidor (Inicio Descanso)")
        # Lógica: S=0. Programar Regreso Servidor.
        self.S = 0
        self.proxima_salida_servidor = float('inf')
        tiempo_descanso = self.generar_tiempo_descanso()
        self.proximo_regreso_servidor = self.reloj + tiempo_descanso
        
        # Lógica: Si PS=1 -> pausar servicio sumando tiempo de descanso al Fin de Servicio
        if self.PS == 1:
            self.proximo_fin_servicio += tiempo_descanso
            print(f"  -> El servidor está atendiendo. Pausa su tarea. Retomará en {tiempo_descanso:.2f} min.")
        else:
            print(f"  -> El servidor está libre y se va a descansar por {tiempo_descanso:.2f} min.")

    def rutina_regreso_servidor(self):
        print(f"[{self.reloj:6.2f}] EVENTO: Regreso Servidor (Fin Descanso)")
        # Lógica: S=1. Programar próxima Salida Servidor.
        self.S = 1
        self.proximo_regreso_servidor = float('inf')
        self.proxima_salida_servidor = self.reloj + self.generar_tiempo_trabajo()
        
        # Lógica: Si PS=0 y Q>0 -> Q-1, PS=1, cancelar Abandono, programar Fin Servicio
        if self.PS == 0 and self.Q > 0:
            self.Q -= 1
            cliente = self.HC.pop(0)
            cid = cliente["id"]
            self.PS = 1
            if cid in self.abandonos_programados:
                del self.abandonos_programados[cid]
            self.proximo_fin_servicio = self.reloj + self.generar_tiempo_servicio()
            print(f"  -> Servidor retorna. Empieza a atender al Cliente {cid} de la cola.")
        elif self.PS == 1:
            print("  -> Servidor retorna y se reanuda el servicio que estaba pausado.")

    def rutina_abandono_cola(self, cid):
        print(f"[{self.reloj:6.2f}] EVENTO: Abandono Cola (Cliente {cid})")
        # Lógica: Q-1. Eliminar al cliente específico del vector HC.
        indice_a_remover = None
        for i, c in enumerate(self.HC):
            if c["id"] == cid:
                indice_a_remover = i
                break
                
        if indice_a_remover is not None:
            self.HC.pop(indice_a_remover)
            self.Q -= 1
            print(f"  -> El Cliente {cid} perdió la paciencia y se fue. (Q={self.Q}).")
            
        # Limpiamos el evento de la lista de abandonos
        if cid in self.abandonos_programados:
            del self.abandonos_programados[cid]

    # --- 3. Bucle Principal (Director) ---
    def ejecutar(self):
        # Mientras el Reloj < Límite
        while self.reloj < self.limite_simulacion:
            # Busca el evento con hora MENOR
            prox_tiempo, evento_info = self.get_proximo_evento()
            
            # Condición de corte por si no hay más eventos a futuro en el rango
            if prox_tiempo is None or prox_tiempo > self.limite_simulacion:
                break
                
            # Avanza el Reloj a esa hora
            self.reloj = prox_tiempo
            
            # Ejecuta la función del evento
            if isinstance(evento_info, tuple) and evento_info[0] == Eventos.ABANDONO_COLA:
                self.rutina_abandono_cola(evento_info[1])
            elif evento_info == Eventos.LLEGADA_CLIENTE:
                self.rutina_llegada_cliente()
            elif evento_info == Eventos.FIN_SERVICIO:
                self.rutina_fin_servicio()
            elif evento_info == Eventos.SALIDA_SERVIDOR:
                self.rutina_salida_servidor()
            elif evento_info == Eventos.REGRESO_SERVIDOR:
                self.rutina_regreso_servidor()

        print(f"\n--- Fin Simulación (Reloj: {self.reloj:.2f} / Límite: {self.limite_simulacion}) ---")
        print(f"Estado final -> Q={self.Q}, PS={self.PS}, S={self.S}")

if __name__ == "__main__":
    sim = Simulacion1PS()
    
    print("=== Configuración de la Simulación ===")
    try:
        limite_input = input("Límite de simulación en minutos [Presiona Enter para 100]: ")
        limite = float(limite_input) if limite_input else 100.0
        
        q_ini_input = input("Tamaño inicial de cola (Q) [Presiona Enter para 0]: ")
        q_ini = int(q_ini_input) if q_ini_input else 0
        
        ps_ini_input = input("Estado inicial del PS (0=Libre, 1=Ocupado) [Presiona Enter para 0]: ")
        ps_ini = int(ps_ini_input) if ps_ini_input else 0
        
        s_ini_input = input("Presencia del servidor (0=Ausente, 1=Trabajando) [Presiona Enter para 1]: ")
        s_ini = int(s_ini_input) if s_ini_input else 1
    except ValueError:
        print("\n[!] Valores inválidos, se usarán los valores por defecto.")
        limite, q_ini, ps_ini, s_ini = 100.0, 0, 0, 1

    sim.init_simulacion(limite, q_ini, ps_ini, s_ini)
    sim.ejecutar()
