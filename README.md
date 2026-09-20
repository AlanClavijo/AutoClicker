# ⚡ Auto Clicker Pro & Contador de Clicks

Una aplicación de escritorio moderna, rápida e intuitiva para Windows escrita en Python con `CustomTkinter` y `pynput`. Incluye auto-clicker personalizable en tiempo real y contador dual de clicks (automáticos vs manuales).

---

## 📥 Descarga Directa

[![Descargar para Windows](https://img.shields.io/badge/Descargar-AutoClicker.exe-blue?style=for-the-badge&logo=windows&logoColor=white)](../../releases/latest)

> 🚀 **¿Cómo instalar?**
> 1. Haz clic en el botón de arriba o ve a la sección de [Releases](../../releases/latest).
> 2. Descarga el archivo **`AutoClicker.exe`** (no requiere instalar Python ni dependencias adicionales).
> 3. Haz doble clic en el archivo ejecutado para usar la aplicación.

---

## ✨ Características

- ⚡ **Auto-Clicker Multihilo**: Ejecución fluida sin congelar la ventana.
- ⏱️ **Intervalo Personalizable**: Configura Horas, Minutos, Segundos y Milisegundos.
- 🎯 **Opciones de Click**:
  - Botón: Izquierdo, Derecho o Medio.
  - Tipo: Click simple o Doble click.
  - Modo: Repetición infinita o límite de N clicks.
- 🔢 **Contador Dual en Tiempo Real**:
  - Clicks Automáticos registrados por el sistema.
  - Clicks Manuales que realizas en tu computadora.
- ⌨️ **Tecla Rápida Global (Hotkey `F8`)**: Activa/Desactiva el auto clicker incluso con la ventana minimizada.
- 🎨 **Interfaz Moderna**: Modo oscuro fluido basado en las guías de diseño Fluent de Windows 11.

---

## 💻 Desarrollo Local

Si deseas ejecutar o modificar el código fuente:

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/AutoClicker.git
cd AutoClicker

# 2. Crear entorno virtual e instalar dependencias
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 3. Ejecutar la aplicación
python app.py
```

### 🔨 Compilar tu propio ejecutable (.exe)

```bash
pip install pyinstaller
pyinstaller app.spec
```

El ejecutable generado se guardará en la carpeta `dist/app.exe`.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.
