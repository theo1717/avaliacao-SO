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
    def process_table(processes: list, current_tick: int | None = None) -> None:
        if not processes:
            print("  (nenhum processo)")
            return
        print(
            f"\n{'PID':<5}{'Operacao':<16}{'Prior.':<7}{'Estado':<10}"
            f"{'Rest.':<5}{'Espera':<6}{'DL':<5}{'Resp.':<6}"
        )
        print("-" * 66)
        for p in processes:
            color = STATE_COLORS.get(p.state.value, "")
            resp = p.response_time if p.response_time is not None else "-"
            dl_marker = ""
            if current_tick is not None and p.deadline < current_tick and p.state.value != "TERMINATED":
                dl_marker = "!"
            elif p.deadline_missed:
                dl_marker = "X"
            print(
                f"{p.pid:<5}{p.operation_type:<16}{p.priority.name:<7}"
                f"{color}{p.state.value:<10}{Style.RESET_ALL}"
                f"{p.remaining_time:<5}{p.waiting_time:<6}"
                f"{p.deadline:<5}{dl_marker:<1}{str(resp):<6}"
            )
            if p.block_reason:
                print(f"      bloqueio: {p.block_reason}")

    @staticmethod
    def queue_display(ready_queue: list, label: str = "Fila de Execucao") -> None:
        print(f"\n{Fore.MAGENTA}{label}:{Style.RESET_ALL} ", end="")
        if not ready_queue:
            print("(vazia)")
        else:
            print(" -> ".join(f"PID-{pid}" for pid in ready_queue))

    @staticmethod
    def memory_map(memory_manager, max_rows: int = 16) -> None:
        print(f"\n{Fore.CYAN}--- Mapa de Memoria ---{Style.RESET_ALL}")
        summary = memory_manager.summary()
        print(
            f"  Quadros: {summary['used_frames']}/{summary['total_frames']} "
            f"| Page faults: {summary['page_faults']} "
            f"| Tamanho pagina: {summary['page_size_kb']} KB"
        )
        for frame in memory_manager.get_map()[:max_rows]:
            pid = frame["pid"] if frame["pid"] is not None else "-"
            print(f"  Frame {frame['frame']:>2}: PID={pid} | {frame['label']}")

    @staticmethod
    def metrics_report(metrics) -> None:
        summary = metrics.summary()
        print(f"\n{Fore.GREEN}--- Relatorio de Metricas ---{Style.RESET_ALL}")
        print(f"  Ticks totais:           {summary['total_ticks']}")
        print(f"  Processos concluidos:   {summary['completed_count']}")
        print(f"  Tempo medio espera:     {summary['avg_waiting_time']}")
        print(f"  Tempo medio resposta:   {summary['avg_response_time']}")
        print(f"  Tempo medio turnaround: {summary['avg_turnaround_time']}")
        print(f"  Deadlines perdidos:     {summary.get('deadline_misses', 0)}")
        mem = summary.get("memory", {})
        if mem:
            print(
                f"  Memoria: {mem.get('used_frames', 0)}/{mem.get('total_frames', 0)} "
                f"quadros | page faults: {mem.get('page_faults', 0)}"
            )

        completed = metrics.completed_report()
        if completed:
            print(
                f"\n{'PID':<5}{'Operacao':<16}{'Prior.':<7}{'Espera':<6}"
                f"{'Resp.':<6}{'Turn.':<6}{'DL':<5}{'Miss':<5}"
            )
            print("-" * 58)
            for row in completed:
                miss = "SIM" if row.get("deadline_missed") else "nao"
                print(
                    f"{row['pid']:<5}{row['operation']:<16}{row['priority']:<7}"
                    f"{row['waiting_time']:<6}{row['response_time']:<6}"
                    f"{row['turnaround_time']:<6}{row.get('deadline', '-'):<5}{miss:<5}"
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
