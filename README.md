# Ticketing App 🎫

Aplicación de gestión de tickets desarrollada con Flask, MySQL y Docker.

## 🚀 Cómo ejecutar

1. Clona este repositorio:
   
   git clone https://github.com/AlvaroTorrado/ticketing_app.git
   cd ticketing_app

   docker compose down -v

   docker compose up --build

   Get-Content reordenar_ids_usuarios.sql | docker compose exec -T mysql mysql -u root tfg_tickets time="2025-06-06T18:43:27+02:00" level=warning msg="C:\\Users\\alvar\\Escritorio\\ticketing_app\\docker-compose.yaml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion"