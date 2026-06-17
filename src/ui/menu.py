from src.concurrency.deadlock import DeadlockDemo
from src.concurrency.producer_consumer import run_producer_consumer_demo
from src.concurrency.sync_primitives import run_log_race_demo, run_race_condition_demo
from src.simulation.engine import SimulationConfig, SimulationEngine
from src.ui.display import Display


class MainMenu:
    def __init__(self) -> None:
        self.config = SimulationConfig()
        self.last_metrics = None
        self.display = Display()

    def run(self) -> None:
        while True:
            self._show_main_menu()
            choice = input("\nEscolha uma opcao: ").strip()

            if choice == "1":
                self._scheduling_menu()
            elif choice == "2":
                self._race_condition_menu()
            elif choice == "3":
                self._producer_consumer_menu()
            elif choice == "4":
                self._deadlock_menu()
            elif choice == "5":
                self._memory_menu()
            elif choice == "6":
                self._config_menu()
            elif choice == "7":
                self._show_last_metrics()
            elif choice == "0":
                print("\nEncerrando simulador. Ate logo!")
                break
            else:
                print("Opcao invalida.")

    def _show_main_menu(self) -> None:
        self.display.header("Simulador Bancario SO")
        print("1. Simulacao de Escalonamento (RR / Prioridade / EDF)")
        print("2. Demo: Condicao de Corrida (saldo e log)")
        print("3. Demo: Produtor-Consumidor")
        print("4. Demo: Deadlock e Prevencao")
        print("5. Demo: Gerenciamento de Memoria")
        print("6. Configuracoes")
        print("7. Ver relatorio de metricas")
        print("0. Sair")
        print(
            f"\n[Config: scheduler={self.config.scheduler_type}, "
            f"quantum={self.config.quantum}, processos={self.config.num_processes}, "
            f"memoria={self.config.memory_frames} quadros, "
            f"delay={self.config.tick_delay}s, fast={self.config.fast_mode}]"
        )

    def _scheduling_menu(self) -> None:
        self.display.header("Simulacao de Escalonamento")
        print("1. Round Robin")
        print("2. Prioridade")
        print("3. EDF (Earliest Deadline First)")
        print("4. Threads ATM + Monitor (concorrencia)")
        sub = input("Escolha: ").strip()

        if sub == "4":
            self._run_atm_demo()
            return

        scheduler_map = {"1": "RR", "2": "PRIORITY", "3": "EDF"}
        if sub not in scheduler_map:
            print("Opcao invalida.")
            return
        self.config.scheduler_type = scheduler_map[sub]

        mode = input("Modo (1=continuo, 2=passo a passo): ").strip()
        step = mode == "2"

        engine = SimulationEngine(config=self.config)
        engine.setup()

        scheduler_names = {
            "RR": "Round Robin",
            "PRIORITY": "Prioridade",
            "EDF": "EDF (Earliest Deadline First)",
        }

        def on_tick(tick, pm, metrics):
            if tick % 2 == 0 or step:
                print(f"\n--- Tick {tick} ---")
                self.display.queue_display(pm.ready_queue)
                if pm.blocked_queue:
                    print(f"  Bloqueados: {pm.blocked_queue}")
                running = [pm.get_process(pid) for pid in pm.ready_queue]
                if engine.scheduler and engine.scheduler.current_process:
                    running.insert(0, engine.scheduler.current_process)
                self.display.process_table(running[:8], current_tick=tick)
                self.display.memory_map(engine.memory, max_rows=8)

        self.display.header(f"Executando {scheduler_names[self.config.scheduler_type]}")
        self.last_metrics = engine.run(step_by_step=step, on_tick=on_tick)
        self.display.metrics_report(self.last_metrics)
        input("\nPressione Enter para voltar...")

    def _run_atm_demo(self) -> None:
        self.display.header("Demo: Threads ATM + Monitor")
        engine = SimulationEngine(config=self.config)
        results = engine.run_concurrent_atm_demo()
        self.display.key_value(results.get("buffer_stats", {}))
        self.display.log_lines(results.get("monitor_log", []))
        input("\nPressione Enter para voltar...")

    def _race_condition_menu(self) -> None:
        self.display.header("Demo: Condicao de Corrida")
        print("1. Saldo compartilhado - sem mutex")
        print("2. Saldo compartilhado - com mutex")
        print("3. Log de transacoes - sem mutex")
        print("4. Log de transacoes - com mutex")
        sub = input("Escolha: ").strip()

        if sub in ("1", "2"):
            use_mutex = sub == "2"
            result = run_race_condition_demo(
                num_threads=4, iterations=100, use_mutex=use_mutex
            )
            print(f"\n  Threads:           {result['threads']}")
            print(f"  Iteracoes/thread:  {result['iterations_per_thread']}")
            print(f"  Saldo esperado:    {result['expected_balance']}")
            print(f"  Saldo obtido:      {result['actual_balance']}")
            print(f"  Protegido:         {result['protected']}")
            status = "CORRETO" if result["correct"] else "INCORRETO (race condition!)"
            color = "\033[92m" if result["correct"] else "\033[91m"
            print(f"  Resultado:         {color}{status}\033[0m")
        elif sub in ("3", "4"):
            use_mutex = sub == "4"
            result = run_log_race_demo(
                num_threads=4, lines_per_thread=50, use_mutex=use_mutex
            )
            print(f"\n  Threads:           {result['threads']}")
            print(f"  Linhas/thread:     {result['lines_per_thread']}")
            print(f"  Linhas esperadas:  {result['expected_lines']}")
            print(f"  Linhas no arquivo: {result['actual_lines']}")
            print(f"  Protegido:         {result['protected']}")
            status = "CORRETO" if result["correct"] else "INCORRETO (log corrompido!)"
            color = "\033[92m" if result["correct"] else "\033[91m"
            print(f"  Resultado:         {color}{status}\033[0m")
            print(f"  Arquivo:           {result['log_path']}")
        else:
            print("Opcao invalida.")
        input("\nPressione Enter para voltar...")

    def _producer_consumer_menu(self) -> None:
        self.display.header("Demo: Produtor-Consumidor")
        result = run_producer_consumer_demo(
            num_producers=2,
            num_consumers=1,
            items_per_producer=5,
            capacity=3,
        )
        self.display.key_value(result["stats"])
        self.display.log_lines(result["log"])
        input("\nPressione Enter para voltar...")

    def _deadlock_menu(self) -> None:
        self.display.header("Demo: Deadlock e Prevencao")
        print("1. Sem prevencao (pode ocorrer deadlock)")
        print("2. Com prevencao (ordenacao de recursos)")
        sub = input("Escolha: ").strip()

        if sub not in ("1", "2"):
            print("Opcao invalida.")
            return

        demo = DeadlockDemo()
        result = demo.run_deadlock_scenario(use_prevention=sub == "2")
        self.display.key_value({
            "prevencao": result["prevention_enabled"],
            "deadlock_detectado": result["deadlock_detected"],
            "transferencias_concluidas": result["completed_transfers"],
            "saldos_finais": result["final_balances"],
            "saldo_conservado": result["balance_conserved"],
        })
        self.display.log_lines(result["log"])
        input("\nPressione Enter para voltar...")

    def _memory_menu(self) -> None:
        self.display.header("Demo: Gerenciamento de Memoria")
        engine = SimulationEngine(config=self.config)
        result = engine.run_memory_pressure_demo()
        self.display.key_value({
            "alocados_inicialmente": result["allocated_initial"],
            "bloqueados_inicialmente": result["blocked_initial"],
            "desbloqueados_apos_free": result["unblocked_after_free"],
            **result["memory"],
        })
        self.display.memory_map(engine.memory)
        self.display.log_lines(result["log"])
        input("\nPressione Enter para voltar...")

    def _config_menu(self) -> None:
        self.display.header("Configuracoes")
        print(f"Quantum atual: {self.config.quantum}")
        q = input("Novo quantum (Enter para manter): ").strip()
        if q.isdigit():
            self.config.quantum = int(q)

        print(f"Processos atual: {self.config.num_processes}")
        n = input("Novo numero de processos (Enter para manter): ").strip()
        if n.isdigit():
            self.config.num_processes = int(n)

        print(f"Quadros de memoria: {self.config.memory_frames}")
        m = input("Novo total de quadros (Enter para manter): ").strip()
        if m.isdigit():
            self.config.memory_frames = int(m)

        print(f"Delay por tick: {self.config.tick_delay}s")
        d = input("Novo delay em segundos (Enter para manter): ").strip()
        try:
            if d:
                self.config.tick_delay = float(d)
        except ValueError:
            pass

        print(f"Modo rapido: {self.config.fast_mode}")
        f = input("Ativar modo rapido? (s/n, Enter para manter): ").strip().lower()
        if f == "s":
            self.config.fast_mode = True
        elif f == "n":
            self.config.fast_mode = False

        print(f"Threads ATM: {self.config.num_atm_threads}")
        a = input("Novo numero de threads ATM (Enter para manter): ").strip()
        if a.isdigit():
            self.config.num_atm_threads = int(a)

        print("\nConfiguracoes atualizadas.")
        input("Pressione Enter para voltar...")

    def _show_last_metrics(self) -> None:
        self.display.header("Relatorio de Metricas")
        if self.last_metrics is None:
            print("  Nenhuma simulacao executada ainda. Use opcao 1 primeiro.")
        else:
            self.display.metrics_report(self.last_metrics)
        input("\nPressione Enter para voltar...")
