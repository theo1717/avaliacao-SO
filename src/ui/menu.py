from src.banking.accounts import AccountRegistry
from src.concurrency.deadlock import DeadlockDemo
from src.concurrency.producer_consumer import run_producer_consumer_demo
from src.concurrency.sync_primitives import run_log_race_demo, run_race_condition_demo
from src.simulation.engine import SimulationConfig, SimulationEngine
from src.ui.banking_labels import SCHEDULER_LABELS
from src.ui.display import Display


class MainMenu:
    def __init__(self) -> None:
        self.config = SimulationConfig()
        self.last_metrics = None
        self.display = Display()
        self.accounts = AccountRegistry()
        self.accounts.setup_default_accounts()

    def run(self) -> None:
        self.display.bank_banner()
        print("\n  Bem-vindo ao terminal de operacoes do Banco Nexus.")
        self.display.accounts_panel(self.accounts)

        while True:
            self._show_main_menu()
            choice = input("\n  Opcao: ").strip()

            routes = {
                "1": self._transaction_center_menu,
                "2": self._atm_network_menu,
                "3": self._integrity_audit_menu,
                "4": self._transfer_management_menu,
                "5": self._memory_cache_menu,
                "6": self._transaction_pipeline_menu,
                "7": self._config_menu,
                "8": self._show_dashboard,
            }
            if choice == "0":
                print("\n  Encerrando sessao. Obrigado por utilizar o Banco Nexus.")
                break
            handler = routes.get(choice)
            if handler:
                handler()
            else:
                print("  Opcao invalida. Tente novamente.")

    def _show_main_menu(self) -> None:
        self.display.header("Menu Principal", "Terminal de Operacoes")
        print("\n  ATENDIMENTO")
        print("  1. Central de Processamento de Transacoes")
        print("  2. Rede de Caixas Eletronicos (ATMs)")
        print("\n  SEGURANCA E CONFORMIDADE")
        print("  3. Auditoria de Integridade (saldos e registros)")
        print("  4. Gestao de Transferencias Simultaneas")
        print("\n  INFRAESTRUTURA")
        print("  5. Cache de Dados em Memoria")
        print("  6. Esteira de Transacoes (ATMs -> Backend)")
        print("\n  ADMINISTRACAO")
        print("  7. Parametros do Sistema")
        print("  8. Painel Gerencial")
        print("\n  0. Encerrar sessao")
        policy = SCHEDULER_LABELS.get(self.config.scheduler_type, self.config.scheduler_type)
        print(
            f"\n  Politica ativa: {policy}  |  "
            f"Fila: {self.config.num_processes} ops  |  "
            f"Cache: {self.config.memory_frames} quadros"
        )
        self.display.footer_hint()

    def _transaction_center_menu(self) -> None:
        self.display.header(
            "Central de Processamento de Transacoes",
            "Define como as operacoes na fila serao atendidas",
        )
        print("\n  Escolha a politica de atendimento:")
        print("  1. Fila justa — todos com tempo igual (Round Robin)")
        print("  2. Clientes Private / prioritarios primeiro")
        print("  3. Operacoes urgentes — menor prazo primeiro (EDF)")
        print("  4. Voltar")
        sub = input("\n  Opcao: ").strip()
        if sub == "4":
            return

        scheduler_map = {"1": "RR", "2": "PRIORITY", "3": "EDF"}
        if sub not in scheduler_map:
            print("  Opcao invalida.")
            return
        self.config.scheduler_type = scheduler_map[sub]

        print("\n  Modo de acompanhamento:")
        print("  1. Tempo real (automatico)")
        print("  2. Passo a passo (supervisao manual)")
        mode = input("  Opcao: ").strip()
        step = mode == "2"

        engine = SimulationEngine(config=self.config)
        engine.setup()

        policy_name = SCHEDULER_LABELS[self.config.scheduler_type]

        def on_tick(tick, pm, metrics):
            if tick % 2 == 0 or step:
                print(f"\n  --- Ciclo operacional {tick} ---")
                self.display.queue_display(pm.ready_queue)
                if pm.blocked_queue:
                    suspended = ", ".join(f"#{p:04d}" for p in pm.blocked_queue)
                    print(f"  Operacoes suspensas: {suspended}")
                running = [pm.get_process(pid) for pid in pm.ready_queue]
                if engine.scheduler and engine.scheduler.current_process:
                    running.insert(0, engine.scheduler.current_process)
                self.display.operation_table(running[:8], current_tick=tick)
                self.display.memory_map(engine.memory, max_rows=6)

        self.display.header(f"Processando fila — {policy_name}")
        print(f"  Iniciando processamento de {self.config.num_processes} operacoes...")
        self.last_metrics = engine.run(step_by_step=step, on_tick=on_tick)
        self.display.metrics_report(self.last_metrics)
        self.display.press_enter()

    def _atm_network_menu(self) -> None:
        self.display.header(
            "Rede de Caixas Eletronicos",
            "ATMs enviando transacoes em paralelo com monitoramento",
        )
        engine = SimulationEngine(config=self.config)
        results = engine.run_concurrent_atm_demo()
        self.display.key_value(results.get("buffer_stats", {}), title="Movimentacao da rede")
        self.display.log_lines(
            results.get("monitor_log", []),
            title="Monitor de auditoria",
        )
        self.display.press_enter()

    def _integrity_audit_menu(self) -> None:
        self.display.header(
            "Auditoria de Integridade",
            "Verificacao de concorrencia em recursos compartilhados",
        )
        print("\n  Selecione o tipo de auditoria:")
        print("  1. Saldo da conta — sem trava de seguranca")
        print("  2. Saldo da conta — com trava de seguranca (mutex)")
        print("  3. Livro-razao (log) — gravacao simultanea sem protecao")
        print("  4. Livro-razao (log) — gravacao protegida")
        print("  5. Voltar")
        sub = input("\n  Opcao: ").strip()
        if sub == "5":
            return

        if sub in ("1", "2"):
            use_mutex = sub == "2"
            self.display.header(
                "Auditoria de Saldo",
                "Varios caixas creditando a mesma conta simultaneamente",
            )
            result = run_race_condition_demo(
                num_threads=4, iterations=100, use_mutex=use_mutex
            )
            self.display.key_value({
                "expected_balance": result["expected_balance"],
                "actual_balance": result["actual_balance"],
                "correct": result["correct"],
                "protected": result["protected"],
            }, title="Resultado da auditoria")
            if result["correct"]:
                print("\n  \033[92m  Integridade confirmada — saldo correto.\033[0m")
            else:
                print("\n  \033[91m  FALHA — divergencia detectada (condicao de corrida).\033[0m")
        elif sub in ("3", "4"):
            use_mutex = sub == "4"
            self.display.header(
                "Auditoria do Livro-Razao",
                "Multiplos operadores gravando registros ao mesmo tempo",
            )
            result = run_log_race_demo(
                num_threads=4, lines_per_thread=50, use_mutex=use_mutex
            )
            self.display.key_value({
                "expected_lines": result["expected_lines"],
                "actual_lines": result["actual_lines"],
                "correct": result["correct"],
                "protected": result["protected"],
            }, title="Resultado da auditoria")
            print(f"    Arquivo analisado: {result['log_path']}")
            if result["correct"]:
                print("\n  \033[92m  Registro integro — todas as linhas presentes.\033[0m")
            else:
                print("\n  \033[91m  FALHA — registros perdidos ou corrompidos.\033[0m")
        else:
            print("  Opcao invalida.")
        self.display.press_enter()

    def _transfer_management_menu(self) -> None:
        self.display.header(
            "Gestao de Transferencias Simultaneas",
            "Transferencias cruzadas entre contas da agencia",
        )
        self.display.accounts_panel(self.accounts)
        print("\n  Cenario: duas transferencias cruzadas (A->B e B->A) ao mesmo tempo.")
        print("\n  1. Sem protocolo anti-travamento (pode bloquear)")
        print("  2. Com protocolo de ordenacao de contas (prevencao)")
        print("  3. Voltar")
        sub = input("\n  Opcao: ").strip()
        if sub == "3":
            return
        if sub not in ("1", "2"):
            print("  Opcao invalida.")
            return

        demo = DeadlockDemo(registry=self.accounts)
        result = demo.run_deadlock_scenario(use_prevention=sub == "2")
        self.display.key_value({
            "prevencao": result["prevention_enabled"],
            "deadlock_detectado": result["deadlock_detected"],
            "transferencias_concluidas": result["completed_transfers"],
            "saldos_finais": result["final_balances"],
            "saldo_conservado": result["balance_conserved"],
        }, title="Resultado das transferencias")
        self.display.log_lines(result["log"], title="Historico da operacao")
        self.display.press_enter()

    def _memory_cache_menu(self) -> None:
        self.display.header(
            "Cache de Dados em Memoria",
            "Alocacao de quadros para cache de operacoes bancarias",
        )
        engine = SimulationEngine(config=self.config)
        result = engine.run_memory_pressure_demo()
        self.display.key_value({
            "allocated_initial": result["allocated_initial"],
            "blocked_initial": result["blocked_initial"],
            "unblocked_after_free": result["unblocked_after_free"],
            **result["memory"],
        }, title="Resumo da alocacao")
        self.display.memory_map(engine.memory)
        self.display.log_lines(result["log"], title="Historico de alocacao")
        self.display.press_enter()

    def _transaction_pipeline_menu(self) -> None:
        self.display.header(
            "Esteira de Transacoes",
            "ATMs produzem operacoes; backend processa em fila limitada",
        )
        print("  Simulando 2 ATMs enviando transacoes para o processador central...")
        result = run_producer_consumer_demo(
            num_producers=2,
            num_consumers=1,
            items_per_producer=5,
            capacity=3,
        )
        self.display.key_value(result["stats"], title="Fluxo da esteira")
        self.display.log_lines(result["log"], title="Movimentacao em tempo real")
        self.display.press_enter()

    def _config_menu(self) -> None:
        self.display.header("Parametros do Sistema", "Ajustes da agencia digital")
        print(f"\n  Tempo por operacao (quantum): {self.config.quantum}")
        q = input("  Novo valor (Enter para manter): ").strip()
        if q.isdigit():
            self.config.quantum = int(q)

        print(f"  Operacoes na fila padrao: {self.config.num_processes}")
        n = input("  Novo valor (Enter para manter): ").strip()
        if n.isdigit():
            self.config.num_processes = int(n)

        print(f"  Quadros de cache de memoria: {self.config.memory_frames}")
        m = input("  Novo valor (Enter para manter): ").strip()
        if m.isdigit():
            self.config.memory_frames = int(m)

        print(f"  Intervalo entre ciclos: {self.config.tick_delay}s")
        d = input("  Novo valor em segundos (Enter para manter): ").strip()
        try:
            if d:
                self.config.tick_delay = float(d)
        except ValueError:
            pass

        print(f"  Modo expediente (sem delay): {self.config.fast_mode}")
        f = input("  Ativar? (s/n, Enter para manter): ").strip().lower()
        if f == "s":
            self.config.fast_mode = True
        elif f == "n":
            self.config.fast_mode = False

        print(f"  Caixas eletronicos na rede: {self.config.num_atm_threads}")
        a = input("  Novo valor (Enter para manter): ").strip()
        if a.isdigit():
            self.config.num_atm_threads = int(a)

        print("\n  Parametros atualizados com sucesso.")
        self.display.press_enter()

    def _show_dashboard(self) -> None:
        self.display.header("Painel Gerencial", "Indicadores da ultima sessao de processamento")
        if self.last_metrics is None:
            print("\n  Nenhuma sessao registrada ainda.")
            print("  Acesse a Central de Processamento (opcao 1) para gerar dados.")
        else:
            self.display.metrics_report(self.last_metrics)
        self.display.press_enter()
