# RAW

```md
A técnica Ralph-Wiggun Loop é baseada em iterações com uma chamada de sessão para cada tasks, até a conclusão total.
Desenvolva um plano de implementação de um projeto, separado em 7 partes distintas mas com a mesma densidade de obrigação, não use como critério de divisão campos relacionados, cada parte tem que ter a mesma complexidade de execução.
Cada parte tem que ser separada em tasks seguindo a estrutura RALPH, as tasks não devem ser simples e nem complexas, a densidade de realização tem que ser média, (Imagine o loading de um contexto geral para cada task, se forem simples irá realizar muitos loadings, se for complexo, irá ter problemas de context rot).

ESTRUTURA {
   RALPH {
      ## (High|Medium|Low) Priority
      - [ ] task 

      ## Notes
      - Notas
   }
}

REQUISITOS {
   MACRO {
      objetivo final,
      dataset + schema,
      técnicas de análise usadas,
      tech-stack,
      modelos de predição usados,
      clusters usados.
   }   
   MICRO {
      objetivo final (DO PLANO MICRO),
      dataframes utilizados + schemas,
      lista de tasks a serem implementadas seguindo o padrão da estrutura RALPH.
   }
}

OUTPUT {
   macro.md -> PLANEJAMENTO MACRO
   (part).md -> PLANEJAMENTO MICRO (Cada parte)
}
```

# OTIMIZED
```md
# ROLE: Project Architect / AI Engineer
# FRAMEWORK: Ralph-Wiggum Loop (Iterative session-per-task execution)

OBJECTIVE:
Develop a project implementation plan divided into 7 distinct parts. Each part must have identical execution complexity and workload density, regardless of thematic area (do not group by related fields; group by effort/processing load).

TASK GRANULARITY:
Tasks must be of Medium Density. 
- Avoid "Simple" tasks (prevents excessive context loading overhead).
- Avoid "Complex" tasks (prevents Context Rot/memory degradation).

STRUCTURE:
RALPH {
   ## (High|Medium|Low) Priority
   - [ ] task 

   ## Notes
   - [Implementation notes/technical details]
}

REQUIREMENTS:
1. MACRO Level:
   - Final Objective.
   - Dataset + Schema definition.
   - Analysis techniques.
   - Tech-stack.
   - Prediction models.
   - Clustering strategies.

2. MICRO Level (Per Part):
   - Micro-plan objective.
   - Specific Dataframes + Schemas.
   - List of medium-density tasks following the RALPH structure.

OUTPUT:
- macro.md -> MACRO PLANNING
- part_1.md through part_7.md -> MICRO PLANNING (One for each of the 7 equal-density segments)
```