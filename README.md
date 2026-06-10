# Simulador Bancário de Sistema Operacional

Avaliação apresentada ao sétimo período de Engenharia de Software, na disciplina de Sistemas Operacionais.

Simulador de SO em tempo real com temática bancária, desenvolvido em Python. Demonstra gerência de processos, escalonamento, concorrência, sincronização e prevenção de deadlock.

## Como executar

```bash
pip install -r requirements.txt
python main.py
```

Para rodar os testes:

```bash
python -m pytest tests/ -v
```

## Mapa: Conceito SO → Temática Bancária

| Conceito SO | Implementação no projeto |
|---|---|
| Processo (PCB) | Operação bancária: transferência, saque, depósito, etc. |
| Thread | ATM, processador backend, monitor de auditoria |
| Escalonamento RR | Fila circular com quantum configurável |
| Escalonamento por Prioridade | Clientes VIP executam antes (com aging) |
| Mutex | Proteção de saldo compartilhado e log de transações |
| Semáforo | Limite de ATMs simultâneos e buffer produtor-consumidor |
| Produtor-Consumidor | ATMs produzem transações, backend consome |
| Deadlock | Transferências cruzadas entre contas A e B |
| Prevenção de deadlock | Ordenação de recursos (menor ID de conta primeiro) |

## Estrutura do projeto

```
src/
├── core/           # PCB, ProcessManager, Schedulers, Métricas
├── banking/        # Contas, transações, operações
├── concurrency/    # Mutex, semáforos, produtor-consumidor, deadlock
├── simulation/     # Engine de simulação e threads
└── ui/             # Menus e exibição no terminal
```

## Funcionalidades do menu

1. **Simulação de Escalonamento** — Round Robin ou Prioridade, modo contínuo ou passo a passo
2. **Condição de Corrida** — compara saldo com e sem mutex
3. **Produtor-Consumidor** — buffer limitado com semáforos
4. **Deadlock e Prevenção** — demonstra e resolve deadlock em transferências
5. **Configurações** — quantum, número de processos, delay, modo rápido
6. **Relatório de métricas** — tempo de espera, resposta e turnaround

## Bibliotecas utilizadas

| Biblioteca | Uso | Justificativa |
|---|---|---|
| `threading` | Lock, Semaphore, Thread | Primitivas de concorrência do Python (mutex/semáforo nativos) |
| `colorama` | Cores no terminal | Apenas visualização |
| `pytest` | Testes unitários | Validação dos algoritmos |
| `collections`, `heapq`, `dataclasses`, `enum` | Estruturas de dados | Implementação própria dos algoritmos |

**Importante:** Os algoritmos de escalonamento (RR e Prioridade), gerência de processos, buffer produtor-consumidor e cenários de deadlock são implementação própria. `threading.Lock` é o mutex da linguagem, não um simulador de SO pronto.

## Roteiro sugerido para apresentação

1. **Escalonamento (5 min)** — Executar RR e Prioridade, mostrar fila, estados e métricas
2. **Concorrência (3 min)** — Demo sem mutex (saldo errado) vs com mutex (saldo correto)
3. **Produtor-Consumidor (3 min)** — ATMs produzindo, backend consumindo, buffer limitado
4. **Deadlock (4 min)** — Mostrar timeout sem prevenção, depois prevenção por ordenação
5. **Arquitetura (2 min)** — Explicar módulos e bibliotecas usadas

## Requisitos atendidos

- [x] Criação, finalização, bloqueio/desbloqueio e prioridades de processos
- [x] PCB com PID, prioridade, burst, estado, quantum e deadline
- [x] Múltiplas threads reais (`threading.Thread`)
- [x] Dois algoritmos de escalonamento: Round Robin e Prioridade
- [x] Métricas: fila, tempo de espera, resposta, processos concluídos
- [x] Mutex e semáforos com demonstração de condição de corrida
- [x] Cenário produtor-consumidor
- [x] Simulação e prevenção de deadlock
- [x] Interface terminal com menus navegáveis
- [x] Código modularizado em arquivos e classes
