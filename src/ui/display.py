try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False

    class _NoColor:
        def __getattr__(self, name: str) -> str:
            return ""

    Fore = _NoColor()
    Style = _NoColor()


STATE_COLORS = {
    "NEW": Fore.CYAN,
    "READY": Fore.YELLOW,
    "RUNNING": Fore.GREEN,
    "BLOCKED": Fore.RED,
    "TERMINATED": Fore.WHITE,
}


class Display:
    @staticmethod
    def header(title: str) -> None:
        line = "=" * 50
        print(f"\n{Fore.BLUE}{line}")
        print(f"  {title}")
        print(f"{line}{Style.RESET_ALL}")

    @staticmethod
    def process_table(processes: list) -> None:
        if not processes:
            print("  (nenhum processo)")
            return
        print(f"\n{'PID':<6}{'Operacao':<20}{'Prior.':<8}{'Estado':<12}{'Rest.':<6}{'Espera':<8}")
        print("-" * 60)
        for p in processes:
            color = STATE_COLORS.get(p.state.value, "")
            print(
                f"{p.pid:<6}{p.operation_type:<20}{p.priority.name:<8}"
                f"{color}{p.state.value:<12}{Style.RESET_ALL}"
                f"{p.remaining_time:<6}{p.waiting_time:<8}"
            )

    @staticmethod
    def queue_display(ready_queue: list, label: str = "Fila de Execucao") -> None:
        print(f"\n{Fore.MAGENTA}{label}:{Style.RESET_ALL} ", end="")
        if not ready_queue:
            print("(vazia)")
        else:
            print(" -> ".join(f"PID-{pid}" for pid in ready_queue))

    @staticmethod
    def metrics_report(metrics) -> None:
        summary = metrics.summary()
        print(f"\n{Fore.GREEN}--- Relatorio de Metricas ---{Style.RESET_ALL}")
        print(f"  Ticks totais:        {summary['total_ticks']}")
        print(f"  Processos concluidos: {summary['completed_count']}")
        print(f"  Tempo medio espera:  {summary['avg_waiting_time']}")
        print(f"  Tempo medio resposta: {summary['avg_response_time']}")
        print(f"  Tempo medio turnaround: {summary['avg_turnaround_time']}")

        completed = metrics.completed_report()
        if completed:
            print(f"\n{'PID':<6}{'Operacao':<20}{'Prior.':<8}{'Espera':<8}{'Resp.':<8}{'Turn.':<8}")
            print("-" * 58)
            for row in completed:
                print(
                    f"{row['pid']:<6}{row['operation']:<20}{row['priority']:<8}"
                    f"{row['waiting_time']:<8}{row['response_time']:<8}"
                    f"{row['turnaround_time']:<8}"
                )

    @staticmethod
    def log_lines(lines: list[str], max_lines: int = 20) -> None:
        print(f"\n{Fore.CYAN}--- Log ---{Style.RESET_ALL}")
        for line in lines[-max_lines:]:
            print(f"  {line}")

    @staticmethod
    def key_value(data: dict) -> None:
        for key, value in data.items():
            print(f"  {key}: {value}")
