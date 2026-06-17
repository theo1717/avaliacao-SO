# Simulador Bancário de Sistema Operacional

Avaliação apresentada ao sétimo período de Engenharia de Software, na disciplina de Sistemas Operacionais.

Simulador de SO em tempo real com temática bancária, desenvolvido em Python. Demonstra gerência de processos, escalonamento, concorrência, sincronização, gerenciamento de memória e prevenção de deadlock.

## Como executar

```bash
pip install -r requirements.txt
python main.py
```

Para rodar os testes:

```bash
python -m pytest tests/ -v
```

## Documentação

| Documento | Descrição |
|---|---|
| [Guia de Uso](docs/GUIA_DE_USO.md) | Manual completo: fluxos passo a passo, o que observar em cada tela e mapeamento aos requisitos do item 3 |
| [Roteiro de Apresentação](docs/ROTEIRO_APRESENTACAO.md) | Script cronometrado (~17 min) para demonstração oral à banca |
| [Perguntas Técnicas](docs/perguntasTecnicas.md) | Respostas preparadas para perguntas da banca sobre escalonamento, sincronização, deadlock, memória, etc. |

## Mapa: Conceito SO → Temática Bancária

| Conceito SO | Implementação no projeto |
|---|---|
| Processo (PCB) | Operação bancária: transferência, saque, depósito, etc. |
| Thread | ATM, processador backend, monitor de auditoria |
| Escalonamento RR | Fila circular com quantum configurável |
| Escalonamento por Prioridade | Clientes VIP executam antes (com aging) |
| Escalonamento EDF | Operações com deadline mais próximo executam primeiro |
| Memória | Quadros alocados para cache de dados de cada operação |
| Mutex | Proteção de saldo compartilhado e log de transações |
| Semáforo | Limite de ATMs simultâneos e buffer produtor-consumidor |
| Produtor-Consumidor | ATMs produzem transações, backend consome |
| Deadlock | Transferências cruzadas entre contas A e B |
| Prevenção de deadlock | Ordenação de recursos (menor ID de conta primeiro) |
| Bloqueio por conta | Processo aguarda liberação da conta bancária |

## Estrutura do projeto

```
src/
├── core/           # PCB, ProcessManager, Schedulers, Métricas, Memória
├── banking/        # Contas, transações, locks de conta
├── concurrency/    # Mutex, semáforos, produtor-consumidor, deadlock
├── simulation/     # Engine de simulação e threads
└── ui/             # Menus e exibição no terminal
```

## Funcionalidades do menu

Ao iniciar, o sistema exibe o painel do **Banco Nexus** com contas ativas e saldos.

| Opção | Nome no sistema | Conceito SO (para apresentação) |
|---|---|---|
| 1 | Central de Processamento de Transações | Escalonamento RR / Prioridade / EDF |
| 2 | Rede de Caixas Eletrônicos | Threads ATM + monitor |
| 3 | Auditoria de Integridade | Condição de corrida (saldo e log) |
| 4 | Gestão de Transferências Simultâneas | Deadlock e prevenção |
| 5 | Cache de Dados em Memória | Gerenciamento de memória |
| 6 | Esteira de Transações | Produtor-consumidor |
| 7 | Parâmetros do Sistema | Configurações |
| 8 | Painel Gerencial | Métricas de desempenho |

## Bibliotecas utilizadas

| Biblioteca | Uso | Justificativa |
|---|---|---|
| `threading` | Lock, Semaphore, Thread | Primitivas de concorrência do Python |
| `colorama` | Cores no terminal | Apenas visualização |
| `pytest` | Testes unitários | Validação dos algoritmos |
| `collections`, `dataclasses`, `enum` | Estruturas de dados | Implementação própria |

**Importante:** Os algoritmos de escalonamento, gerência de processos, memória, buffer produtor-consumidor e cenários de deadlock são implementação própria.

## Requisitos atendidos

- [x] Criação, finalização, bloqueio/desbloqueio e prioridades de processos
- [x] PCB com PID, prioridade, burst, estado, quantum e deadline
- [x] Múltiplas threads reais (`threading.Thread`)
- [x] Três algoritmos de escalonamento: Round Robin, Prioridade e EDF
- [x] Métricas: fila, tempo de espera, resposta, processos concluídos, deadlines
- [x] Gerenciamento de memória com alocação, liberação e page faults
- [x] Mutex e semáforos com demonstração de condição de corrida (saldo e log)
- [x] Cenário produtor-consumidor
- [x] Simulação e prevenção de deadlock
- [x] Bloqueio de processos por conta bancária em uso
- [x] Interface terminal com menus navegáveis
- [x] Código modularizado em arquivos e classes
