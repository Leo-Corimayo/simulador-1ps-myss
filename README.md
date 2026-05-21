# Simulador de Sistemas Discretos - 1 Puesto de Servicio (1PS)

## Breve Presentación

### Logros Alcanzados
- **Motor Unificado**: Se logró unificar las lógicas de los problemas 1, 2 y 3 en un solo motor de eventos discretos. El reloj gestiona correctamente las interrupciones del servidor (Problema 2) sin perder el estado de los clientes, y cancela exitosamente los eventos de abandono (Problema 3) si el cliente es llamado a ser atendido antes de su tiempo límite de espera.
- **Interfaz Gráfica Premium**: Se implementó una interfaz visual moderna (modo oscuro) interactiva mediante Tkinter y Matplotlib que visualiza la cola, el estado del puesto de servicio y la evolución de la fila en tiempo real.

### Dificultades
La principal dificultad fue el diseño de la lógica para el Problema 2, específicamente evitar que los clientes entraran al puesto de servicio cuando este figuraba como 'Libre' pero el servidor estaba en estado 'Ausente', lo cual requirió ajustar los filtros en el diagrama de Llegada.

### Puntos a Resolver / Futuras Mejoras
- Integrar el Problema 4 de prioridades múltiples en la cola.

---

## Cómo Ejecutar el Proyecto

Este proyecto cuenta con dos versiones independientes:

### 1. Versión Gráfica Premium (Recomendado)
Incluye panel de configuración de variables interactivo, vista animada de la cola, gráficos estadísticos de evolución temporal de la cola en tiempo real y logs detallados de eventos.
```bash
python simulador_grafico.py
```

### 2. Versión de Consola
Una implementación directa orientada puramente a la ejecución y visualización de logs a través de la terminal estándar.
```bash
python simulacion_1ps.py
```

---
**Desarrollado para la cátedra de Modelo y Simulación.**
