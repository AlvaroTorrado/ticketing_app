DROP TABLE IF EXISTS ticket_history;
DROP TABLE IF EXISTS ticket;
DROP TABLE IF EXISTS role_change_history;
DROP TABLE IF EXISTS user;



-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 21-05-2025 a las 20:38:22
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `tfg_tickets`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `role_change_history`
--

CREATE TABLE `role_change_history` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `changed_by_id` int(11) DEFAULT NULL,
  `old_role` varchar(20) DEFAULT NULL,
  `new_role` varchar(20) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `role_change_history`
--

INSERT INTO `role_change_history` (`id`, `user_id`, `changed_by_id`, `old_role`, `new_role`, `timestamp`) VALUES
(1, NULL, 4, 'usuario', 'manager', '2025-05-20 20:33:36'),
(2, 10, 4, 'usuario', 'manager', '2025-05-20 20:44:06'),
(3, 11, 4, 'usuario', 'admin', '2025-05-20 21:42:13'),
(4, 11, 4, 'admin', 'usuario', '2025-05-20 21:42:16'),
(5, 11, 4, 'usuario', 'manager', '2025-05-20 21:54:35'),
(6, 11, 4, 'manager', 'usuario', '2025-05-20 21:55:00'),
(7, 11, 4, 'usuario', 'admin', '2025-05-20 21:55:50'),
(8, 11, 4, 'admin', 'manager', '2025-05-20 21:55:53'),
(9, 11, 4, 'manager', 'usuario', '2025-05-20 21:55:54');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ticket`
--

CREATE TABLE `ticket` (
  `id` int(11) NOT NULL,
  `title` varchar(100) NOT NULL,
  `description` text NOT NULL,
  `status` varchar(20) DEFAULT NULL,
  `assigned_to_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `ticket`
--

INSERT INTO `ticket` (`id`, `title`, `description`, `status`, `assigned_to_id`) VALUES
(1, 'Fallo de red', 'Se detecta una interrupción en la red. No hay acceso a servicios internos ni conexión a Internet desde algunos equipos. Se ha verificado el cableado y reiniciado los dispositivos de red, pero el problema persiste.\r\n\r\nSe requiere revisión para identificar y resolver la causa del fallo.', 'abierto', 11),
(2, 'Problema con la impresora', 'La impresora no responde al enviar trabajos desde ningún equipo. Ya se ha reiniciado, revisado el cableado y verificado el estado de papel y tinta. Sigue sin imprimir.', 'pendiente', NULL),
(3, 'Error al iniciar sesión', 'No es posible iniciar sesión en el sistema. Aparece un mensaje de error indicando \"credenciales incorrectas\", pero los datos ingresados son correctos. Se requiere revisión del usuario o desbloqueo.', 'abierto', 12),
(4, 'Aplicación (Microsoft Teams)', 'La aplicación Microsoft Teams no inicia correctamente. Al ejecutarla, se cierra de inmediato sin mostrar mensajes de error. Ya se intentó reiniciar el equipo.', 'completado', 12),
(5, 'Equipo lento', 'El equipo presenta lentitud general en el uso, especialmente al abrir programas o navegar. Se revisó el uso de recursos y hay picos altos de CPU y memoria.', 'pendiente', NULL),
(6, 'Problemas con conexión Wi-Fi', 'El equipo no logra conectarse a la red Wi-Fi. Aparece como \"conectado sin acceso a Internet\". Ya se intentó olvidar la red y reconectar, sin éxito.', 'pendiente', NULL),
(7, 'Monitor sin señal', 'El monitor muestra “Sin señal” al encender el equipo. Se ha verificado la conexión del cable y reiniciado la máquina. Todo parece conectado correctamente.', 'pendiente', 12),
(8, 'Solicitud de instalación de software', 'Se solicita la instalación del software [nombre y versión], necesario para tareas operativas. El equipo cumple con los requisitos.', 'pendiente', NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ticket_history`
--

CREATE TABLE `ticket_history` (
  `id` int(11) NOT NULL,
  `ticket_id` int(11) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `old_status` varchar(20) DEFAULT NULL,
  `new_status` varchar(20) DEFAULT NULL,
  `changed_by_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `ticket_history`
--

INSERT INTO `ticket_history` (`id`, `ticket_id`, `timestamp`, `old_status`, `new_status`, `changed_by_id`) VALUES
(1, 1, '2025-05-20 21:00:45', 'pendiente', 'abierto', 11),
(2, 4, '2025-05-20 21:07:54', 'pendiente', 'completado', 12),
(3, 5, '2025-05-20 21:27:15', '-', 'pendiente', 10),
(4, 6, '2025-05-20 21:27:35', '-', 'pendiente', 10),
(5, 7, '2025-05-20 21:27:49', '-', 'pendiente', 10),
(6, 8, '2025-05-20 21:28:01', '-', 'pendiente', 10),
(7, 3, '2025-05-20 22:51:27', 'pendiente', 'abierto', 12);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `username` varchar(64) NOT NULL,
  `password_hash` varchar(128) NOT NULL,
  `role` varchar(20) NOT NULL,
  `last_login` datetime DEFAULT NULL,
  `mfa_enabled` tinyint(1) DEFAULT 0,
  `mfa_secret` varchar(32) DEFAULT NULL,
  `mfa_confirmed` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `user`
--

INSERT INTO `user` (`id`, `username`, `password_hash`, `role`, `last_login`, `mfa_enabled`, `mfa_secret`, `mfa_confirmed`) VALUES
(4, 'admin', 'pbkdf2:sha256:1000000$NBpVLjuxgRYUL5OT$a8ae9adb29d93ee6e12d92b48ac9fdb332a9b4e74519dd6fe9b4dca0b0a96a70', 'admin', '2025-05-21 18:30:05', 1, 'HBW7EYGTU7663ZWD4FHJWF7PKCZRY6RZ', 1),
(10, 'torrado', 'pbkdf2:sha256:1000000$v5bPlVvCIQxvbaQX$72f6c54dcbdbbbfe349677962aaa308576d9b36b58a01bf8f27eb3838f900a94', 'manager', '2025-05-21 18:15:50', 1, 'A2QAC5KEYKUM475XX3L4MGYGQD74LVWW', 1),
(11, 'pepe', 'pbkdf2:sha256:1000000$rgRNAYa4Z5Eq2nKQ$ad037005cb8ba4cb77246c405f7f4ad8e4c68c09020a6f1e0b49cd148a3f18b4', 'usuario', '2025-05-21 18:18:10', 1, '7RGX24OM7CC2FZR34U7B7WA35SFOXGZC', 1),
(12, 'manolo', 'pbkdf2:sha256:1000000$B36s2LuyIdzry2OA$e8e83a29f5ef36824dccd0f319e4268ceff04f22d76abbe673b4a8cddc8726ff', 'usuario', '2025-05-20 21:01:29', 0, NULL, 0),
(13, 'jose', 'pbkdf2:sha256:1000000$CmVXEj94oUXc3nw1$e173cb43d1de0b292e71c390f495fb2d7fa45831a3d7611606adedb09858a3ef', 'usuario', NULL, 0, NULL, 0),
(14, 'claudia', 'pbkdf2:sha256:1000000$dn3fLE8Qx5oDD4K7$fa956119b9e799ab68b13ddbac6996cb212f3d010336f0ae71c5525380766012', 'usuario', '2025-05-21 17:53:39', 0, NULL, 0);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `role_change_history`
--
ALTER TABLE `role_change_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `changed_by_id` (`changed_by_id`);

--
-- Indices de la tabla `ticket`
--
ALTER TABLE `ticket`
  ADD PRIMARY KEY (`id`),
  ADD KEY `assigned_to_id` (`assigned_to_id`);

--
-- Indices de la tabla `ticket_history`
--
ALTER TABLE `ticket_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ticket_id` (`ticket_id`),
  ADD KEY `changed_by_id` (`changed_by_id`);

--
-- Indices de la tabla `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `role_change_history`
--
ALTER TABLE `role_change_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT de la tabla `ticket`
--
ALTER TABLE `ticket`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT de la tabla `ticket_history`
--
ALTER TABLE `ticket_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `role_change_history`
--
ALTER TABLE `role_change_history`
  ADD CONSTRAINT `role_change_history_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  ADD CONSTRAINT `role_change_history_ibfk_2` FOREIGN KEY (`changed_by_id`) REFERENCES `user` (`id`);

--
-- Filtros para la tabla `ticket`
--
ALTER TABLE `ticket`
  ADD CONSTRAINT `ticket_ibfk_1` FOREIGN KEY (`assigned_to_id`) REFERENCES `user` (`id`);

--
-- Filtros para la tabla `ticket_history`
--
ALTER TABLE `ticket_history`
  ADD CONSTRAINT `ticket_history_ibfk_1` FOREIGN KEY (`ticket_id`) REFERENCES `ticket` (`id`),
  ADD CONSTRAINT `ticket_history_ibfk_2` FOREIGN KEY (`changed_by_id`) REFERENCES `user` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
