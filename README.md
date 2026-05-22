# Simulador de Sistemas Discretos - 1 Puesto de Servicio (1PS)

Un simulador dinámico, interactivo y de alta fidelidad visual desarrollado en Python con `tkinter` y `matplotlib` para la modelización, análisis y auditoría de sistemas de cola y eventos discretos.

---

## 🚀 Resolución Unificada de la Guía (Problemas 1 al 5)

Este software ha evolucionado de manera sobresaliente y logra **unificar y parametrizar en una sola interfaz interactiva la resolución completa de los 5 problemas de la guía académica (bloque 1 Puesto de Servicio - 1PS)**:

1.  **Problema 1 (Simulación Básica):** Modelado de eventos discretos con reloj de simulación, tasas de arribo (`T. Llegada`), tasas de atención (`T. Servicio`), cola general `Q` y límites de simulación.
2.  **Problema 2 (Ciclos de Trabajo y Descanso del Servidor):** Eventos autónomos de interrupción `SALIDA_S` y reanudación `REGRESO_S` según tiempos aleatorios. El motor pausa la atención activa del Puesto de Servicio (PS) durante el descanso y la reanuda inmediatamente al finalizar sin perder el progreso del cliente en curso.
3.  **Problema 3 (Paciencia y Abandono de Clientes):** Configuración de paciencia en cola. Se gestiona de manera asíncrona un evento de `ABANDONO` único para cada cliente. Si el tiempo expira antes de ser atendido, el cliente abandona físicamente la cola y el evento es auditado en el historial.
4.  **Problema 4 (Prioridades Múltiples A y B):** Clasificación probabilística del tipo de cliente (Alta Prioridad A vs Baja Prioridad B) configurable mediante porcentaje. Encolado segmentado (`HC_A` y `HC_B`) donde los clientes A se atienden antes que los B (prioridad no preactiva).
5.  **Problema 5 (Zona de Seguridad):** Simulación espacial de un pasillo de traslado previo al Puesto de Servicio. Incluye tiempo de traslado y modelado formal de la variable académica de estado binaria `zs` (libre/ocupada) y traza `zs_cliente`.

---

## 🎨 Características Visuales y Estéticas Premium

La interfaz gráfica de la aplicación ha sido rediseñada para ofrecer una experiencia estética premium y una legibilidad sobresaliente:

*   **Panel de Configuración Ampliado:** 
    *   Campos numéricos (`tk.Entry`) con fuente **Consolas 11 Bold** para asegurar una lectura perfecta.
    *   Diseño plano (flat) premium con fondo `#2C2C2C` y borde fino que se ilumina en color púrpura de acento (`COLOR_ACCENT`) al recibir foco de edición.
    *   Etiquetas en **Segoe UI 11** y espaciado interno vertical (`ipady=3`) para mayor comodidad física.
    *   Botones **RND** y **Simulador** con colores vibrantes, estados de retroalimentación interactivos al hacer clic y cambios de color dinámicos (el botón principal se oscurece a `SIMULANDO...` y regresa a verde `COLOR_SUCCESS` al terminar).
*   **Tabla de Simulación (Treeview) Ultra-Legible:**
    *   Fondo oscuro y cabeceras dinámicas personalizadas en **Segoe UI 11 Bold** con hover activo.
    *   Separación física de filas ampliada a **`32px`** (`rowheight=32`) para una legibilidad digna de herramientas analíticas profesionales.
    *   Columnas ensanchadas y formateadas (`Reloj`, `Evento`, `Detalle` y `Estado`) para mostrar de forma holgada los estados de las variables académicas (`Q=... ZS=... PS=... S=...`) sin ningún tipo de recorte o truncamiento de texto.
*   **Canvas de Cola Dinámico (90px):**
    *   Visualización de clientes con círculos individuales ampliados a **`24px`** de diámetro con su ID de cliente (`C1`, `C2`, etc.) en **Segoe UI 9 Bold** totalmente legible.
    *   Cajas delimitadoras aumentadas y centradas para modelar físicamente las secciones de la Cola, la Zona de Seguridad y el Puesto de Servicio.

---

## 📁 Estructura del Proyecto

*   `simulador_grafico.py`: Implementación multihilo asíncrona de la versión gráfica premium (Model-View-Controller).
*   `simulacion_1ps.py`: Implementación de consola lineal del Problema 1 orientada puramente a logs en terminal.

---

## 💻 Cómo Ejecutar el Proyecto

Recomendamos utilizar la versión gráfica interactiva para auditar y comprender mejor la dinámica del sistema:

### 1. Ejecutar Versión Gráfica Premium
```bash
python simulador_grafico.py
```

### 2. Ejecutar Versión de Consola Standard
```bash
python simulacion_1ps.py
```

---
**Desarrollado con fines académicos para la cátedra de Modelo y Simulación.**
