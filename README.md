# plugin.video.robinhood

---

## English

A Kodi addon to access video streams from a backend compatible with [rh-server](https://github.com/wetdreams69/rh-server).

### Features

- 🔄 Automatic source refresh
- 📡 Connects to a remote backend compatible with [rh-server](https://github.com/wetdreams69/rh-server)
- 🎬 Supports M3U8 streams
- ⚡ Robust error and timeout handling
- 🌐 English interface

### Installation

1. Download the addon ZIP file
2. In Kodi, go to **System > Settings > Add-ons > Install from ZIP file**
3. Select the downloaded ZIP file
4. The addon will install automatically

### Configuration

1. Go to **System > Settings > Add-ons > Video Add-ons > Robinhood**
2. Set the **Backend Base URL** (default: `http://localhost:8080`)
3. Save the settings

### Usage

1. Go to **Videos > Add-ons > Robinhood**
2. Select **[Refresh sources 📡]** to update the available channels
3. Choose a site from the list
4. Select the channel you want to watch
5. The stream will start automatically

### Backend API

This addon is designed to work with the [rh-server](https://github.com/wetdreams69/rh-server) backend, which must be running and accessible from Kodi. The backend provides the following endpoints:

- `GET /assets/metadata` - List of available sites and channels
- `GET /assets/{endpoint}` - M3U8 stream for a specific channel
- `POST /assets/refresh` - Triggers a source refresh
- `GET /status` - Scraping status

For more information on installing and configuring the backend, visit the official repository: [wetdreams69/rh-server](https://github.com/wetdreams69/rh-server)

### Requirements

- Kodi 19+ (Matrix) or newer
- Python 3.0.0
- Internet connection
- [rh-server](https://github.com/wetdreams69/rh-server) backend running and configured

### Author

**wetdreams69**

### License

MIT License - See [LICENSE](LICENSE) for details.

### Version

1.1.0

---

## Español

Un addon para Kodi que permite acceder a streams de video desde un backend compatible con [rh-server](https://github.com/wetdreams69/rh-server).

### Características

- 🔄 Actualización automática de fuentes
- 📡 Conexión a backend remoto compatible con [rh-server](https://github.com/wetdreams69/rh-server)
- 🎬 Soporte para streams M3U8
- ⚡ Manejo robusto de errores y timeouts
- 🌐 Interfaz en inglés

### Instalación

1. Descarga el archivo ZIP del addon
2. En Kodi, ve a **Sistema > Configuración > Add-ons > Instalar desde archivo ZIP**
3. Selecciona el archivo ZIP descargado
4. El addon se instalará automáticamente

### Configuración

1. Ve a **Sistema > Configuración > Add-ons > Add-ons de video > Robinhood**
2. Configura la **Base URL del backend** (por defecto: `http://localhost:8080`)
3. Guarda la configuración

### Uso

1. Navega a **Videos > Add-ons > Robinhood**
2. Selecciona **[Actualizar fuentes 📡]** para refrescar los canales disponibles
3. Elige un sitio de la lista
4. Selecciona el canal que deseas ver
5. El stream comenzará automáticamente

### Backend API

El addon está diseñado para funcionar con el backend [rh-server](https://github.com/wetdreams69/rh-server), que debe estar corriendo y accesible desde Kodi. El backend proporciona los siguientes endpoints:

- `GET /assets/metadata` - Lista de sitios y canales disponibles
- `GET /assets/{endpoint}` - Stream M3U8 para un canal específico
- `POST /assets/refresh` - Inicia actualización de fuentes
- `GET /status` - Estado del scraping

Para más información sobre cómo instalar y configurar el backend, visita el repositorio oficial: [wetdreams69/rh-server](https://github.com/wetdreams69/rh-server)

### Requisitos

- Kodi 19+ (Matrix) o superior
- Python 3.0.0
- Conexión a internet
- Backend [rh-server](https://github.com/wetdreams69/rh-server) configurado y funcionando

### Autor

**wetdreams69**

### Licencia

MIT License - Ver archivo [LICENSE](LICENSE) para más detalles.

### Versión

1.1.0