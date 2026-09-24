# Ruta de IA y Automatización

## Automatización inteligente del buzón corporativo de RIWI

### 1. Contexto empresarial

La empresa **RIWI Barranquilla** utiliza actualmente un único buzón de correo electrónico como uno de los principales canales de comunicación con clientes, proveedores y terceros:

**[info@riwi.io](mailto:info@riwi.io)**

A través de este buzón se reciben diariamente diferentes tipos de comunicaciones relacionadas con la operación de la organización.

Entre las comunicaciones más frecuentes se encuentran:

- Facturas electrónicas y documentos relacionados con cuentas por pagar.
- Órdenes de compra.
- Documentos asociados a órdenes de compra.
- Solicitudes relacionadas con productos o servicios.
- Peticiones, quejas, reclamos y solicitudes — PQRS.
- Comunicaciones generales de clientes y proveedores.
- Correos que pueden no corresponder a ninguno de los procesos anteriores.

El crecimiento de la operación ha provocado que este modelo de atención basado en un único buzón genere una importante carga operativa y dificultades para garantizar que cada comunicación sea atendida por el área correspondiente.

Actualmente, el equipo debe revisar manualmente los mensajes recibidos, interpretar su contenido, identificar qué tipo de solicitud corresponde a cada correo, revisar los archivos adjuntos y posteriormente direccionar la información al área responsable.

Esto genera un escenario en el que información crítica para la operación puede quedar mezclada dentro de cientos de conversaciones y documentos recibidos diariamente.

### 2. El problema

El buzón [info@riwi.io](mailto:info@riwi.io) se ha convertido en un punto único de entrada para diferentes procesos empresariales.

El principal problema no es únicamente el volumen de correos, sino la ausencia de un mecanismo inteligente que permita **interpretar, clasificar, priorizar, organizar y direccionar automáticamente la información recibida**.

Actualmente se presentan situaciones como:

- Facturas que permanecen dentro del buzón sin ser identificadas oportunamente.
- Órdenes de compra que requieren revisión manual.
- Documentos adjuntos que deben ser abiertos e interpretados por una persona.
- PQRS que pueden terminar mezcladas con comunicaciones comerciales o administrativas.
- Correos enviados al área incorrecta.
- Información que debe ser digitada nuevamente en otros sistemas.
- Dificultad para conocer rápidamente cuántas facturas fueron recibidas durante un día.
- Dificultad para identificar qué facturas ya fueron procesadas y cuáles están pendientes.
- Falta de trazabilidad sobre el responsable que recibió o procesó determinada comunicación.
- Riesgo de que una comunicación importante no sea atendida oportunamente.
- Dependencia de personas para realizar tareas repetitivas de clasificación y distribución.

La situación puede representarse conceptualmente de la siguiente manera:

**Clientes / Proveedores / Terceros**

↓

**[info@riwi.io](mailto:info@riwi.io)**

↓

**Gran volumen de correos**

↓

**Revisión manual**

↓

**Interpretación humana**

↓

**Clasificación**

↓

**Descarga/revisión de documentos**

↓

**Direccionamiento**

↓

**Procesamiento por cada área**

Este flujo genera una carga operativa que se pretende reducir mediante el uso de **inteligencia artificial y automatización**.

### 3. Restricción empresarial

Una de las principales condiciones del reto es que **NO se puede solucionar simplemente creando nuevos buzones de correo**.

Por ejemplo, no es viable plantear como solución principal:

- facturas@riwi.io
- compras@riwi.io
- pqrs@riwi.io

La razón es que durante años diferentes clientes, proveedores y terceros han utilizado **info@riwi.io** como dirección de contacto.

La organización cuenta con aproximadamente **dos millones de clientes registrados**, además de una cantidad significativa de proveedores y terceros que conocen y utilizan actualmente esta dirección.

Cambiar masivamente el canal de recepción implicaría costos y riesgos operativos importantes, tales como:

- Actualización de información de contacto.
- Comunicación con clientes y proveedores.
- Modificación de documentos y procesos existentes.
- Riesgo de pérdida de comunicaciones.
- Dependencia de terceros para adoptar el nuevo mecanismo.
- Posibles errores durante el período de transición.

Por esta razón, la solución propuesta debe asumir que:

**info@riwi.io continuará siendo el punto único de entrada.**

El reto consiste en construir una capa inteligente alrededor de este buzón que permita organizar automáticamente la información sin exigir que los clientes o proveedores cambien su comportamiento.

### 4. Procesos que deben ser automatizados

La solución deberá contemplar como mínimo los siguientes tres grandes procesos.

#### 4.1. Facturas

Cuando llegue un correo asociado a una factura, el sistema deberá ser capaz de identificarlo automáticamente.

La solución deberá considerar elementos como:

- Remitente.
- Asunto.
- Cuerpo del correo.
- Archivos adjuntos.
- Tipo de archivo.
- Contenido del documento.
- Número de factura.
- Proveedor.
- Fecha de emisión.
- Fecha de vencimiento, cuando exista.
- Valor de la factura.
- Identificación tributaria del proveedor.
- Orden de compra relacionada, cuando exista.

Una vez identificada una factura, el sistema deberá generar una clasificación y direccionarla hacia el proceso correspondiente de **Tesorería / Cuentas por Pagar**.

La organización necesita además poder consultar diariamente información como:

- Número de facturas recibidas.
- Proveedores que enviaron facturas.
- Valor total de las facturas recibidas.
- Facturas con información incompleta.
- Facturas que requieren intervención humana.
- Facturas procesadas automáticamente.
- Facturas pendientes.
- Facturas que presentan inconsistencias.
- Facturas duplicadas, si el sistema puede identificarlas.

El objetivo no es únicamente mover un correo de una carpeta a otra.

El objetivo es convertir una comunicación no estructurada en **información estructurada y accionable**.

### 5. Órdenes de compra

El segundo proceso corresponde a las órdenes de compra.

Los correos asociados a este proceso deberán ser identificados y posteriormente clasificados de acuerdo con su naturaleza.

Como mínimo deberán contemplarse dos categorías:

**Producto**

Órdenes de compra relacionadas con adquisición de productos, materiales, equipos, suministros u otros bienes físicos.

**Servicio**

Órdenes de compra relacionadas con contratación o adquisición de servicios.

Una vez realizada la clasificación, la información deberá ser direccionada al área de **Servicios Internos**, responsable de continuar con el procesamiento correspondiente.

La solución deberá considerar que una orden de compra puede venir acompañada de diferentes documentos.

Por ejemplo:

- Orden de compra.
- Cotización.
- Factura.
- Documento contractual.
- Soportes adicionales.

El sistema deberá ser capaz de determinar cuál es el documento principal y cuál es información complementaria.

### 6. PQRS

El tercer proceso corresponde a las **Petición, Quejas, Reclamos y Solicitudes — PQRS**.

Cuando un cliente o tercero envíe una comunicación que corresponda a una PQRS, el sistema deberá identificar la naturaleza de la comunicación y direccionarla automáticamente al área de **Servicio al Cliente — SAC**.

El sistema debería poder identificar, cuando sea posible:

- Tipo de solicitud.
- Cliente.
- Número de identificación.
- Asunto.
- Descripción del caso.
- Productos o servicios involucrados.
- Archivos adjuntos.
- Nivel de prioridad.
- Fecha de recepción.

La solución deberá considerar especialmente el lenguaje natural.

Por ejemplo, un usuario podría escribir:

"Buenas tardes, llevo varios días esperando respuesta sobre mi solicitud y nadie me ha informado qué está pasando."

Aunque el correo no contenga literalmente la palabra "PQRS", el sistema debería ser capaz de interpretar que probablemente corresponde a una comunicación que debe ser atendida por SAC.

### 7. Comunicaciones que no correspondan a las categorías anteriores

La solución no deberá asumir que todos los correos corresponden necesariamente a una factura, una orden de compra o una PQRS.

También pueden existir:

- Solicitudes generales.
- Comunicaciones administrativas.
- Comunicaciones comerciales.
- Correos informativos.
- Notificaciones automáticas.
- Spam.
- Correos enviados por error.
- Comunicaciones que requieren análisis humano.

Por esta razón, la arquitectura propuesta deberá contemplar una categoría de:

**"Requiere revisión humana"**

Esta categoría es fundamental.

Una solución de IA empresarial no debería intentar tomar decisiones de manera forzada cuando la información disponible no sea suficiente.

### 8. El reto de la propuesta

El equipo deberá diseñar una **propuesta técnica de automatización inteligente** que permita transformar el actual buzón info@riwi.io en un punto de entrada automatizado para los procesos empresariales.

La propuesta deberá responder como mínimo a la siguiente pregunta:

**¿Cómo implementarían una solución basada en IA y automatización que permita recibir, interpretar, clasificar, extraer información, validar y direccionar automáticamente los correos recibidos en [info@riwi.io](mailto:info@riwi.io), reduciendo significativamente la intervención humana sin perder trazabilidad ni control?**

No se espera que el equipo construya la solución.

Se espera que diseñe y documente una **propuesta técnica viable**.

### 9. Uso de Inteligencia Artificial

La propuesta deberá explicar claramente **dónde utilizaría IA y dónde utilizaría automatización tradicional**.

No se busca utilizar IA para absolutamente todo.

Por el contrario, uno de los objetivos de la prueba es determinar si el equipo es capaz de identificar correctamente cuándo utilizar:

- Automatizaciones basadas en reglas.
- Flujos de trabajo.
- Procesamiento de documentos.
- OCR.
- Modelos de lenguaje.
- Clasificación mediante IA.
- Extracción de información.
- Agentes inteligentes.
- Validaciones determinísticas.
- Bases de conocimiento.
- Integraciones mediante API.
- Servicios de correo.
- Sistemas de almacenamiento.
- Sistemas de gestión empresarial.

La propuesta deberá justificar técnicamente las decisiones.

Por ejemplo:

¿Qué parte del proceso resolverían mediante reglas?

¿Qué parte mediante IA generativa?

¿Qué parte mediante extracción estructurada?

¿Dónde utilizarían un agente?

¿Dónde no permitirían que una IA tome decisiones autónomas?

### 10. Posible arquitectura

El equipo deberá proponer una arquitectura tecnológica.

No existe una tecnología obligatoria.

Podrían utilizarse, dependiendo de la propuesta, herramientas como:

- Microsoft Power Automate.
- Microsoft Azure.
- OpenAI.
- APIs de modelos de lenguaje.
- Servicios de OCR.
- Make.
- n8n.
- Zapier.
- Google Cloud.
- AWS.
- Servicios propios desarrollados mediante Node.js.
- Bases de datos.
- Sistemas de gestión documental.
- APIs empresariales.
- Webhooks.
- Agentes de IA.

Estas tecnologías son únicamente ejemplos.

El equipo puede proponer otras alternativas siempre que pueda justificar su elección.

La arquitectura deberá mostrar como mínimo:

**Correo**

↓

**Captura del mensaje**

↓

**Clasificación**

↓

**Extracción de información**

↓

**Validación**

↓

**Decisión**

↓

**Direccionamiento**

↓

**Registro**

↓

**Reporte / seguimiento**

El diagrama deberá identificar qué componentes utilizan IA y cuáles corresponden a automatización tradicional.

### 11. Agentes de IA

Uno de los objetivos de la prueba es evaluar la capacidad del equipo para identificar oportunidades reales de utilización de **agentes de IA**.

El equipo podrá proponer uno o varios agentes.

Por ejemplo, podría existir conceptualmente un:

**Agente clasificador**

Responsable de analizar el correo y determinar a qué proceso pertenece.

**Agente extractor**

Responsable de identificar información relevante de documentos adjuntos.

**Agente validador**

Responsable de verificar que la información mínima necesaria esté presente.

**Agente de direccionamiento**

Responsable de determinar el área o flujo al cual debe enviarse la información.

Sin embargo, el equipo deberá justificar si realmente es necesario utilizar varios agentes o si un flujo más sencillo y controlado sería suficiente.

No se evaluará positivamente la utilización de IA simplemente por utilizar IA.

Se evaluará la capacidad de **resolver el problema empresarial de manera eficiente, controlada y sostenible**.

### 12. Manejo de excepciones

Uno de los aspectos más importantes de la propuesta deberá ser el manejo de situaciones en las cuales la automatización no tenga suficiente información para tomar una decisión.

Por ejemplo:

- Una factura ilegible.
- Una factura sin proveedor identificado.
- Un documento sin número de factura.
- Una orden de compra que no permita determinar si corresponde a producto o servicio.
- Un correo que pueda ser simultáneamente una PQRS y una factura.
- Un documento con información contradictoria.
- Un archivo adjunto protegido con contraseña.
- Un formato no soportado.
- Una factura posiblemente duplicada.
- Un correo que no corresponda a ninguna categoría conocida.

La solución deberá definir qué sucede en estos casos.

No es suficiente indicar:

"Se envía a un humano."

La propuesta deberá explicar:

- Cómo se identifica la excepción.
- Dónde queda registrada.
- Quién la recibe.
- Qué información recibe el responsable.
- Cómo se continúa el proceso.
- Cómo se registra la decisión humana.
- Cómo se evita volver a procesar innecesariamente el mismo correo.

### 13. Trazabilidad

Toda solución propuesta deberá considerar trazabilidad.

La empresa debe poder responder preguntas como:

- ¿Cuándo llegó el correo?
- ¿Qué clasificación recibió?
- ¿Por qué fue clasificado de esa manera?
- ¿Qué información fue extraída?
- ¿Qué nivel de confianza tuvo la clasificación?
- ¿Qué área recibió la información?
- ¿Cuándo fue procesada?
- ¿Hubo intervención humana?
- ¿Quién realizó la intervención?
- ¿Cuál fue el resultado?
- ¿Cuánto tiempo tardó el procesamiento?

El equipo deberá explicar cómo conservaría esta información.

### 14. Reporte diario

Uno de los resultados esperados de la solución es contar con un mecanismo que permita obtener diariamente una visión clara de lo ocurrido en el buzón.

Por ejemplo:

**Resumen diario**

**Fecha:** 21/09/2026

| Categoría | Recibidos | Procesados automáticamente | Excepciones | Pendientes |
|---|---|---|---|---|
| Facturas | 185 | 171 | 8 | 6 |
| Órdenes de compra | 74 | 69 | 3 | 2 |
| PQRS | 43 | 40 | 2 | 1 |
| Otros | 31 | 18 | 9 | 4 |

El reporte anterior es únicamente ilustrativo.

La propuesta deberá definir qué indicadores considera relevantes y cómo serían obtenidos automáticamente.

La intención es que un responsable pueda conocer rápidamente el estado de la operación **sin tener que revisar manualmente el buzón completo**.

### 15. Principio fundamental: no trasladar la carga

Existe una condición especialmente importante para esta prueba:

**La solución no puede simplemente cambiar la carga de trabajo de una persona hacia otra.**

Por ejemplo, no sería suficiente implementar un sistema que:

1. Lea los correos.
2. Los clasifique.
3. Genere una lista de 300 tareas.
4. Le entregue esa lista a una persona para que las procese manualmente.

Aunque técnicamente exista automatización, el problema empresarial no estaría realmente solucionado.

La solución deberá buscar que la intervención humana ocurra principalmente cuando:

- Exista una excepción.
- Exista incertidumbre.
- Sea necesaria una decisión empresarial.
- Se requiera aprobación.
- Exista información inconsistente.

El objetivo es que la mayor cantidad posible de tareas repetitivas sean ejecutadas automáticamente.

### 16. Entregable

El equipo deberá entregar un **documento de propuesta técnica de mínimo cuatro (4) páginas**, sin incluir portada ni anexos.

La propuesta deberá contener como mínimo:

**1. Resumen ejecutivo**

Explicar brevemente el problema y la solución propuesta.

**2. Análisis del problema**

Describir las causas, impactos y riesgos del modelo actual.

**3. Solución propuesta**

Explicar detalladamente cómo funcionaría la solución.

**4. Arquitectura**

Presentar un diagrama de arquitectura y explicar cada componente.

**5. Automatización vs. IA**

Identificar qué actividades serían resueltas mediante reglas, automatización tradicional, IA, agentes u otros mecanismos.

**6. Flujo de procesamiento**

Mostrar el flujo desde la llegada del correo hasta su direccionamiento.

**7. Manejo de excepciones**

Explicar qué sucede cuando la IA no puede tomar una decisión confiable.

**8. Trazabilidad**

Explicar cómo se registrarán las decisiones y acciones realizadas.

**9. Reportes e indicadores**

Proponer el mecanismo para conocer diariamente el estado de la operación.

**10. Propuesta tecnológica**

Indicar las tecnologías, servicios, plataformas o herramientas recomendadas y justificar su selección.

**11. Roadmap**

Proponer una estrategia de implementación por fases.

### 12. Restricciones

La propuesta deberá respetar las siguientes restricciones:

1. info@riwi.io continuará siendo el buzón principal de entrada.
2. No se debe asumir que clientes o proveedores modificarán inmediatamente sus procesos.
3. La solución deberá minimizar la intervención humana.
4. No se deberá depender de una persona para clasificar manualmente todos los correos.
5. Toda decisión automatizada deberá ser trazable.
6. La solución deberá contemplar excepciones.
7. La información sensible deberá manejarse bajo criterios de seguridad.
8. La solución deberá poder crecer hacia nuevos procesos.
9. Se deberá justificar cuándo utilizar IA y cuándo una automatización tradicional.
10. No se deberá proponer IA únicamente por moda tecnológica; cada componente deberá responder a una necesidad concreta.

### 13. Resultado esperado

El resultado de esta prueba no debe ser simplemente un diagrama de una automatización.

Se espera que el equipo piense como un **equipo de arquitectura y automatización empresarial**.

La solución deberá demostrar cómo transformar un buzón actualmente desorganizado en un **canal inteligente de entrada de información**, capaz de interpretar comunicaciones, extraer datos, tomar decisiones automatizadas, direccionar procesos, generar información para la gestión y solicitar intervención humana únicamente cuando realmente sea necesario.

El éxito de la propuesta deberá medirse por su capacidad para responder al siguiente objetivo:

**Recibir la información en el mismo buzón que la organización utiliza actualmente, pero convertir automáticamente ese caos de correos y documentos en procesos organizados, trazables, medibles y accionables, reduciendo la carga operativa de las personas y aumentando la velocidad de respuesta de la organización.**

La propuesta debe demostrar no solamente **qué tecnología utilizarían**, sino principalmente **cómo resolverían el problema empresarial utilizando tecnología de manera inteligente**.
