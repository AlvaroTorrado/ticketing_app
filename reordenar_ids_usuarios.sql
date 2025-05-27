-- Desactivar temporalmente las restricciones de claves foráneas
SET FOREIGN_KEY_CHECKS = 0;

-- Eliminar tabla temporal si ya existe
DROP TABLE IF EXISTS user_tmp;

-- 1. Crear tabla temporal con mismo esquema
CREATE TABLE user_tmp LIKE user;
ALTER TABLE user_tmp AUTO_INCREMENT = 1;

-- 2. Insertar los datos ordenados por ID original
INSERT INTO user_tmp (username, password_hash, role, last_login, mfa_enabled, mfa_secret, mfa_confirmed)
SELECT username, password_hash, role, last_login, mfa_enabled, mfa_secret, mfa_confirmed
FROM user
ORDER BY id;

-- 3. Crear tabla de equivalencias entre IDs antiguos y nuevos
DROP TABLE IF EXISTS id_map;
CREATE TABLE id_map AS
SELECT old.id AS old_id, new.id AS new_id
FROM user AS old
JOIN user_tmp AS new ON old.username = new.username;

-- 4. Actualizar claves foráneas

-- ticket.assigned_to_id
UPDATE ticket t
JOIN id_map m ON t.assigned_to_id = m.old_id
SET t.assigned_to_id = m.new_id;

-- ticket_history.changed_by_id
UPDATE ticket_history th
JOIN id_map m ON th.changed_by_id = m.old_id
SET th.changed_by_id = m.new_id;

-- role_change_history.user_id
UPDATE role_change_history rh
JOIN id_map m ON rh.user_id = m.old_id
SET rh.user_id = m.new_id;

-- role_change_history.changed_by_id
UPDATE role_change_history rh
JOIN id_map m ON rh.changed_by_id = m.old_id
SET rh.changed_by_id = m.new_id;

-- 5. Reemplazar la tabla original
DROP TABLE user;
RENAME TABLE user_tmp TO user;

-- 6. Limpiar tabla de equivalencias
DROP TABLE id_map;

-- Reactivar restricciones de claves foráneas
SET FOREIGN_KEY_CHECKS = 1;
