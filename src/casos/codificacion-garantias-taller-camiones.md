---
permalink: /casos/codificacion-garantias-taller-camiones/
title: "Codificación de garantías con IA en un taller | nódicus"
description: "Un taller de camiones debía codificar cada garantía entre más de 12.000 códigos. Un asistente de IA los propone en menos de 80 segundos."
eyebrow: "Caso · Talleres de vehículos industriales"
h1: "Codificación de garantías en un taller de camiones"
crumbName: "Codificación de garantías"
published: "2026-09-24"
lead: "Para cobrar una reparación en garantía, el fabricante no acepta una explicación escrita: exige clasificar el trabajo entre más de 12.000 códigos por camión. Hacerlo a mano llevaba mucho tiempo y a menudo salía mal."
aside: |
  <p class="eyebrow"><span class="tick"></span> Resultados medidos</p>
  <dl class="case-metrics">
    <div class="metric"><dt>72 %</dt><dd>de los códigos correctos encontrados (objetivo: 65 %)</dd></div>
    <div class="metric"><dt>100 %</dt><dd>de acierto en los códigos propuestos con confianza del 90 % o más</dd></div>
    <div class="metric"><dt>40-80 s</dt><dd>por aviso (objetivo: 2 minutos)</dd></div>
    <div class="metric"><dt>&lt; 0,10 €</dt><dd>de coste por aviso</dd></div>
  </dl>
  <p>Métricas de la evaluación con casos reales. Con modelos de lenguaje pueden variar, así que se vuelven a medir.</p>
---

## El problema

El cliente es un grupo de talleres de reparación de vehículos industriales. Cuando reparan un camión en garantía, el fabricante no paga a partir de una descripción del trabajo: pide que cada reparación se clasifique en un árbol de códigos (los llaman *metacodes*) con carpetas y subcarpetas, más de 12.000 posibles por camión. Si la clasificación no es correcta, la garantía no se cobra. En las reparaciones que no son de garantía no es obligatorio, pero el fabricante presiona para que se haga.

Buscar los códigos a mano en ese árbol lleva mucho tiempo y, con esa cantidad de opciones, es fácil equivocarse.

## Qué construimos

Un asistente que lee cada aviso de taller y propone los códigos y las unidades de trabajo, cada uno con su nivel de confianza. El revisor ya no parte de cero: confirma los acertados, descarta los que no proceden y añade los que falten. La decisión sigue siendo suya.

La idea de partida es sencilla: la mayoría de los trabajos de un taller ya se han hecho, y codificado, antes. Una revisión periódica de hoy lleva casi los mismos códigos que las anteriores de ese vehículo. Sobre esa base, el sistema:

- **Busca precedentes** en el histórico de codificaciones que el propio taller ya validó, dando prioridad a lo que se ha confirmado muchas veces.
- **Lee el relato del trabajo** con tres modelos de lenguaje distintos en paralelo: la descripción, los comentarios del mecánico, la mano de obra y los recambios. Solo pesan los códigos en los que varios modelos coinciden.
- **Filtra por evidencia.** Cada código propuesto tiene que estar respaldado por un precedente, por el consenso de los modelos o por pertenecer al paquete habitual de ese tipo de trabajo. Un verificador final descarta lo que no encaja. Es mejor proponer ocho códigos útiles que veinte entre los que elegir.
- **Asigna una confianza calibrada** con datos reales, para que el revisor sepa qué puede aceptar sin más y dónde conviene detenerse.

Se conectó a la pantalla que el taller ya usaba, sin cambiarla, y mejora con el uso: cada aviso que el equipo valida pasa al histórico que alimenta al sistema, sin necesidad de reentrenar nada.

## Cómo lo medimos

Antes de dar el sistema por bueno fijamos con el cliente unos objetivos y lo evaluamos con avisos reales ya codificados. Por el camino apareció lo habitual en estos proyectos: casos de prueba con el número de trabajo equivocado, códigos que no existían en el árbol o duplicados. Se corrigieron o se descartaron de la medición, con criterio acordado, antes de calcular nada.

| Indicador | Objetivo | Resultado |
|---|---|---|
| Códigos correctos encontrados (recall medio) | más del 65 % | 72 % |
| Propuestas que son correctas (precisión) | más del 50 % | 57 % |
| Acierto de los códigos con confianza del 90 % o más | más del 90 % | 100 % |
| Tiempo de respuesta por aviso | 120 s | 40-80 s |
| Peor caso (recall mínimo por aviso) | 45 % | 52 % |

El objetivo nunca fue acertar el 100 %, sino ahorrar tiempo neto al revisor con una base sólida en segundos. El sistema está en producción.
