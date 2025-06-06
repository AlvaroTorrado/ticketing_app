# Ticketing App 🎫

Aplicación de gestión de tickets desarrollada con Flask, MySQL y Docker.

## 🚀 Cómo ejecutar

1. Clona este repositorio:
   
   git clone https://github.com/AlvaroTorrado/ticketing_app.git
   cd ticketing_app

   docker compose down -v

   docker compose up --build

   Get-Content reordenar_ids_usuarios.sql | docker compose exec -T mysql mysql -u root tfg_tickets