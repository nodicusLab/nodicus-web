---
permalink: /casos/migracion-aplicaciones-servidor-propio/
title: "Llevar aplicaciones internas a un servidor propio | nódicus"
description: "Dos aplicaciones internas repartidas en la nube, con la base de datos de facturación expuesta. Las llevamos al servidor de la propia empresa."
eyebrow: "Caso · Instalaciones y obra"
h1: "Dos aplicaciones internas, de vuelta al servidor de la empresa"
crumbName: "Migración a servidor propio"
published: "2026-09-24"
lead: "Una empresa de instalaciones de unos 80 empleados usaba dos aplicaciones internas, una de facturación y otra de seguimiento de obras, repartidas entre varios servicios en la nube. Al revisarlas encontramos su base de datos de facturación accesible desde internet."
aside: |
  <p class="eyebrow"><span class="tick"></span> Qué se hizo</p>
  <p>Cierre del acceso público a la base de datos, migración de las dos aplicaciones al servidor de la empresa con una base de datos común, acceso seguro desde fuera y despliegue automático.</p>
---

## El problema

Las dos aplicaciones funcionaban y el equipo las usaba a diario, pero su infraestructura tenía varios problemas:

- **Datos expuestos.** La base de datos de la aplicación de facturación estaba accesible de forma pública por una configuración de permisos desactivada en el servicio que la alojaba. Fue lo primero que cerramos.
- **Datos sensibles fuera de casa.** La aplicación de obras guardaba información de trabajadores (nóminas, salarios, bajas, vacaciones) y financiera (márgenes, facturación, clientes) en servidores de terceros.
- **Varias suscripciones y dependencia.** Cada aplicación dependía de varios servicios externos, cada uno con su cuota y su panel. Si uno sube el precio o cambia las condiciones, la empresa queda a merced de ello.
- **Sin copias completas ni orden.** No había un mecanismo ordenado para actualizar la base de datos ni copias de seguridad completas.
- **Datos por duplicado.** Obras, usuarios y proveedores se mantenían en las dos aplicaciones a la vez, con el trabajo doble y las incoherencias que eso trae.

La empresa ya tenía un servidor propio con copias de seguridad diarias, así que la solución era centralizarlo todo ahí.

## Qué hicimos

1. **Cerrar la exposición** de la base de datos de facturación en cuanto la detectamos.
2. **Migrar la aplicación de facturación** al servidor de la empresa, dentro de una máquina virtual y en contenedores, con sus archivos trasladados del almacenamiento en la nube a un directorio del propio servidor.
3. **Migrar la aplicación de obras** volcando sus datos en una **base de datos común** a las dos aplicaciones, de modo que obras, usuarios y proveedores existan una sola vez.
4. **Acceso seguro desde fuera.** La aplicación de obras se tiene que poder usar desde la calle sin VPN, así que se publicó con conexión cifrada y dominio propio, exponiendo solo lo imprescindible, con protección frente a accesos no autorizados y un cortafuegos delante. La base de datos y la administración se quedan dentro de la red.
5. **Despliegue automático** desde un repositorio, con versión de pruebas y versión en uso, para que seguir modificando las aplicaciones sea tan sencillo como antes.

## Resultado

Las dos aplicaciones funcionan en el servidor de la empresa, detrás de su cortafuegos y dentro de sus copias de seguridad diarias, con una única fuente de datos. La empresa ha dejado de pagar varios servicios externos y controla dónde está su información. Y la base común facilita cualquier proyecto que venga después.
