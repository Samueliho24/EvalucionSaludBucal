# Compilación del APK — EvalucionSaludBucal

## Requisitos

El script `webview/android-build` es un shell script POSIX que compila, empaqueta y firma el APK **sin Gradle ni Android Studio**. Solo funciona en **Linux** (o macOS con ajustes menores). Windows no está soportado.

### Paquetes necesarios

| Herramienta | Propósito | Paquete (Debian/Ubuntu) |
|---|---|---|
| `sh`, `sed`, `find`, `grep` | Shell y utilidades base | `dash` o `bash` (vienen instalados) |
| `zip` | Empaquetar `classes.dex` y assets dentro del APK | `zip` |
| `javac` (JDK 11) | Compilar `Main.java` a `.class` | `openjdk-11-jdk` |
| `keytool` (JDK 11) | Generar keystore para firmar | `openjdk-11-jdk` |
| `d8` (build-tools) | Convertir `.class` → `classes.dex` | Android SDK build-tools |
| `aapt2` (build-tools) | Compilar y linkear recursos XML | Android SDK build-tools |
| `zipalign` (build-tools) | Alinear el APK | Android SDK build-tools |
| `apksigner` (build-tools) | Firmar el APK | Android SDK build-tools |
| `adb` (platform-tools) | Instalar APK en dispositivo (opcional) | Android SDK platform-tools |

### Android SDK

Necesitas el SDK de Android, específicamente:

- **`platforms/android-<API>`** — contiene `android.jar` contra el que se compila. Si no se define `TARGETAPI`, el script usa el API level más alto que encuentre instalado.
- **`build-tools/`** — contiene `d8`, `aapt2`, `zipalign`, `apksigner`.

---

## Instalación paso a paso (Debian/Ubuntu)

### 1. Java 11 y zip

```bash
sudo apt update
sudo apt install openjdk-11-jdk zip
```

Verificar:

```bash
java -version
# openjdk version "11.0.x"
javac -version
# javac 11.0.x
```

### 2. Android SDK

Opción recomendada: usar `sdkmanager` (command-line tools de Google).

```bash
# Descargar command-line tools (verifica la URL actual en https://developer.android.com/studio#command-line-tools)
wget https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip commandlinetools-linux-11076708_latest.zip
mkdir -p ~/Android/Sdk/cmdline-tools
mv cmdline-tools ~/Android/Sdk/cmdline-tools/latest
export ANDROID_HOME=~/Android/Sdk
```

Instalar platform y build-tools:

```bash
# Instalar API 34 y build-tools (puedes cambiar la versión)
$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager \
  "platforms;android-34" \
  "build-tools;34.0.0"
```

**Alternativa manual**: descargar el SDK desde developer.android.com/studio, extraerlo, y dentro crear la estructura `platforms/android-34/` y `build-tools/34.0.0/` copiando los archivos correspondientes.

### 3. Agregar al PATH

```bash
export PATH=$PATH:$ANDROID_HOME/build-tools/34.0.0:$ANDROID_HOME/platform-tools
```

Para hacerlo permanente, agrega lo siguiente a `~/.bashrc`:

```bash
export ANDROID_HOME=~/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/build-tools/34.0.0:$ANDROID_HOME/platform-tools
```

---

## Compilar el APK

### 1. Regenerar form.html (si editaste form.jinja.html)

```bash
# Desde la raíz del repositorio
python3 webview/gen.py
# Requiere: pip install jinja2
```

### 2. Compilar

```bash
cd webview
./android-build
```

Esto genera `EvalucionSaludBucal.apk` en el directorio `webview/`.

### 3. (Opcional) Instalar en dispositivo

Conecta el dispositivo por USB con depuración USB habilitada:

```bash
./android-build install
```

O compilar + instalar + abrir la app automáticamente:

```bash
./android-build run
```

---

## Variables de entorno

Puedes modificar el comportamiento del build con estas variables:

| Variable | Default | Descripción |
|---|---|---|
| `ANDROID_HOME` | — | Ruta al SDK de Android (obligatorio) |
| `TARGETAPI` | API level más alto instalado | API level de compilación (`android-34`, etc.) |
| `MINAPI` | `18` | API level mínima soportada |
| `APPNAME` | nombre del directorio del proyecto | Nombre del archivo `.apk` generado |
| `PACKAGE` | `app.$APPNAME` | Package name de la app |
| `KEYSTORE` | `android.keystore` | Archivo de keystore para firmar |
| `KEYSTORE_PASS` | `password` | Contraseña del keystore |
| `KEYSTORE_ALIAS` | `cert` | Alias del keystore |
| `JAVA_HOME` | `/usr/lib/jvm/java-11-openjdk/` | Ruta al JDK 11 |

Ejemplo:

```bash
TARGETAPI=33 APPNAME=Miapp ./android-build
```

---

## Estructura del proyecto para el build

```
webview/
├── android-build          ← script de compilación
├── AndroidManifest.xml    ← manifiesto de Android
├── Main.java              ← código fuente (entrypoint)
├── layout/
│   └── main.xml           ← layout XML
├── assets/                ← se empaqueta completo dentro del APK
│   ├── form.html
│   ├── login.html
│   ├── config.html
│   ├── welcome.html
│   ├── post.js
│   ├── style.css
│   ├── escudo_de_luz.png
│   └── LOGO ODONTOLOGIA.png
└── schema.sql             ← solo referencia, no va en el APK
```

> **Nota**: El script busca automáticamente `AndroidManifest.xml` subiendo desde `$PWD`. Ejecuta `./android-build` estando dentro de `webview/`.

---

## Solución de problemas comunes

| Problema | Causa | Solución |
|---|---|---|
| `javac: command not found` | JDK 11 no instalado | `sudo apt install openjdk-11-jdk` |
| `d8: command not found` | build-tools no están en PATH | Exportar `$ANDROID_HOME/build-tools/<version>/` al PATH |
| `android.jar: No such file or directory` | No hay platform instalada | `sdkmanager "platforms;android-34"` |
| `zip: command not found` | zip no instalado | `sudo apt install zip` |
| `Error: AAPT2 not found` | build-tools faltantes o versión incorrecta | Verificar que `aapt2` exista en build-tools |
| `java.lang.UnsupportedClassVersionError` | Versión de Java incorrecta | Asegurar que sea Java 11, no Java 17+ |
| No se genera `R.java` | No hay archivos XML en `layout/` o están vacíos | Verificar que `layout/main.xml` exista |
