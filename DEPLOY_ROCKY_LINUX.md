---
description: Guía de despliegue para Rocky Linux 8/9
---

# Guía de Despliegue en Rocky Linux

Sigue estos pasos en tu servidor Rocky Linux.

## 1. Instalar Dependencias del Sistema

Actualiza el sistema e instala Python, Git y las librerías necesarias para PostgreSQL.

```bash
sudo dnf update -y
sudo dnf install -y python39 python3-pip git postgresql-devel gcc python3-devel nginx
```

## 2. Clonar el Repositorio

Navega a la carpeta donde vivirán las aplicaciones (ej. `/var/www`).

```bash
cd /var/www
sudo git clone <URL_DE_TU_REPO> dle_app
cd dle_app
```

## 3. Configurar Entorno Virtual

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

## 4. Crear Directorios de Logs

```bash
sudo mkdir -p /var/log/dle_app
sudo chown -R $USER:$USER /var/log/dle_app
```

## 5. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto (`/var/www/dle_app/.env`) con tus credenciales de producción.

```ini
DB_HOST=localhost
DB_NAME=nombre_base_datos
DB_USER=usuario
DB_PASS=contraseña
FLASK_ENV=production
SECRET_KEY=tu_clave_secreta_generada
```

## 6. Configurar Systemd (Servicio)

Crea el archivo de servicio para que la app arranque sola.

`sudo nano /etc/systemd/system/dle_app.service`

```ini
[Unit]
Description=Gunicorn instance to serve DLE App
After=network.target

[Service]
User=rocky
Group=nginx
WorkingDirectory=/var/www/dle_app
Environment="PATH=/var/www/dle_app/venv/bin"
EnvironmentFile=/var/www/dle_app/.env
ExecStart=/var/www/dle_app/venv/bin/gunicorn --config gunicorn_config.py run:app

[Install]
WantedBy=multi-user.target
```

Arranca el servicio:

```bash
sudo systemctl start dle_app
sudo systemctl enable dle_app
```

## 7. Configurar Nginx (Proxy Inverso)

Edita la configuración de Nginx:
`sudo nano /etc/nginx/conf.d/dle_app.conf`

```nginx
server {
    listen 80;
    server_name tu_dominio_o_ip;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /var/www/dle_app/app/static;
    }
}
```

Reinicia Nginx:

```bash
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## 8. Firewall

Si tienes firewalld activo, permite el tráfico HTTP.

```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
```
