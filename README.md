# Simulador de Sistemas Discretos - 1 Puesto de Servicio (1PS)

## Breve Presentación

### Logros Alcanzados
Se logró unificar las lógicas de los problemas 1, 2 y 3 en un solo motor de eventos discretos. El reloj gestiona correctamente las interrupciones del servidor (Problema 2) sin perder el estado de los clientes, y cancela exitosamente los eventos de abandono (Problema 3) si el cliente es llamado a ser atendido antes de su tiempo límite de espera.

### Dificultades
La principal dificultad fue el diseño de la lógica para el Problema 2, específicamente evitar que los clientes entraran al puesto de servicio cuando este figuraba como 'Libre' pero el servidor estaba en estado 'Ausente', lo cual requirió ajustar los filtros en el diagrama de Llegada.

### Puntos a Resolver
Queda pendiente agregar una interfaz gráfica, poder agregar visualmente las variables (falta bastante que se irá trabajando antes del parcial) o integrar el Problema 4 de prioridades múltiples.

---
**Desarrollado para la cátedra de Modelo y Simulación.**
