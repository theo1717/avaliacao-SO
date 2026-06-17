from datetime import datetime

from src.banking.accounts import AccountRegistry
from src.ui.banking_labels import (
    BANK_NAME,
    BRANCH,
    PRIORITY_LABELS,
    SCHEDULER_LABELS,
    STATE_LABELS,
    SYSTEM_TITLE,
    block_reason_label,
    format_account_id,
    format_currency,
)

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
    def bank_banner() -> None:
        line = "=" * 58
        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        print(f"\n{Fore.BLUE}{line}")
        print(f"  {BANK_NAME}  |  {BRANCH}")
        print(f"  {SYSTEM_TITLE}")
        print(f"  Sessao: {now}")
        print(f"{line}{Style.RESET_ALL}")

    @staticmethod
    def header(title: str, subtitle: str = "") -> None:
        line = "-" * 58
        print(f"\n{Fore.BLUE}{line}")
        print(f"  {title}")
        if subtitle:
            print(f"  {Fore.WHITE}{subtitle}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{line}{Style.RESET_ALL}")

    @staticmethod
    def accounts_panel(registry: AccountRegistry | None = None) -> None:
        if registry is None:
            registry = AccountRegistry()
            registry.setup_default_accounts()
        print(f"\n{Fore.CYAN}  Contas ativas nesta agencia:{Style.RESET_ALL}")
        for acc in registry.accounts.values():
            print(
                f"    {format_account_id(acc.account_id)}  "
                f"{acc.holder:<12}  Saldo: {format_currency(acc.balance)}"
            )

    @staticmethod
    def footer_hint(text: str = "") -> None:
        hint = text or "Digite o numero da opcao desejada"
        print(f"\n{Fore.WHITE}[{hint}]{Style.RESET_ALL}")

    @staticmethod
    def operation_table(processes: list, current_tick: int | None = None) -> None:
        if not processes:
            print("  (nenhuma operacao na fila)")
            return
        print(
            f"\n  {'Prot.':<6}{'Transacao':<18}{'Perfil':<10}{'Situacao':<12}"
            f"{'Rest.':<5}{'Fila':<5}{'Prazo':<6}{'Resp.':<5}"
        )
        print("  " + "-" * 72)
        for p in processes:
            color = STATE_COLORS.get(p.state.value, "")
            state_label = STATE_LABELS.get(p.state.value, p.state.value)
            profile = PRIORITY_LABELS.get(p.priority.name, p.priority.name)
            resp = p.response_time if p.response_time is not None else "-"
            deadline_flag = ""
            if current_tick is not None and p.deadline < current_tick and p.state.value != "TERMINATED":
                deadline_flag = " ATRASO"
            elif p.deadline_missed:
                deadline_flag = " PERDIDO"
            acc_info = f" | C/C {format_account_id(p.account_id)}"
            print(
                f"  {p.pid:<6}{p.operation_type:<18}{profile:<10}"
                f"{color}{state_label:<12}{Style.RESET_ALL}"
                f"{p.remaining_time:<5}{p.waiting_time:<5}"
                f"{p.deadline:<6}{str(resp):<5}{deadline_flag}"
            )
            print(f"         {acc_info}")
            if p.block_reason:
                print(f"         Motivo: {block_reason_label(p.block_reason)}")

    @staticmethod
    def queue_display(ready_queue: list, label: str = "Fila de atendimento") -> None:
        print(f"\n  {Fore.MAGENTA}{label}:{Style.RESET_ALL} ", end="")
        if not ready_queue:
            print("(vazia)")
        else:
            tickets = " -> ".join(f"#{pid:04d}" for pid in ready_queue)
            print(tickets)

    @staticmethod
    def memory_map(memory_manager, max_rows: int = 16) -> None:
        print(f"\n  {Fore.CYAN}Cache de dados em memoria (quadros):{Style.RESET_ALL}")
        summary = memory_manager.summary()
        print(
            f"  Ocupacao: {summary['used_frames']}/{summary['total_frames']} quadros  |  "
            f"Falhas de pagina: {summary['page_faults']}  |  "
            f"Pagina: {summary['page_size_kb']} KB"
        )
        for frame in memory_manager.get_map()[:max_rows]:
            pid = f"Op-{frame['pid']:04d}" if frame["pid"] is not None else "livre"
            print(f"    Quadro {frame['frame']:>2}: {pid}  |  {frame['label']}")

    @staticmethod
    def metrics_report(metrics) -> None:
        summary = metrics.summary()
        print(f"\n  {Fore.GREEN}--- Painel Gerencial ---{Style.RESET_ALL}")
        print(f"  Tempo de operacao:        {summary['total_ticks']} ciclos")
        print(f"  Transacoes concluidas:    {summary['completed_count']}")
        print(f"  Espera media na fila:     {summary['avg_waiting_time']}")
        print(f"  Tempo medio de resposta:  {summary['avg_response_time']}")
        print(f"  Tempo medio total:        {summary['avg_turnaround_time']}")
        print(f"  Prazos nao cumpridos:     {summary.get('deadline_misses', 0)}")
        mem = summary.get("memory", {})
        if mem:
            print(
                f"  Cache de memoria:         {mem.get('used_frames', 0)}/"
                f"{mem.get('total_frames', 0)} quadros  |  "
                f"falhas: {mem.get('page_faults', 0)}"
            )

        completed = metrics.completed_report()
        if completed:
            print(
                f"\n  {'Prot.':<6}{'Transacao':<18}{'Perfil':<10}{'Fila':<5}"
                f"{'Resp.':<6}{'Total':<6}{'Prazo':<6}{'Status':<8}"
            )
            print("  " + "-" * 68)
            for row in completed:
                profile = PRIORITY_LABELS.get(row["priority"], row["priority"])
                status = "ATRASO" if row.get("deadline_missed") else "OK"
                print(
                    f"  {row['pid']:<6}{row['operation']:<18}{profile:<10}"
                    f"{row['waiting_time']:<5}{row['response_time']:<6}"
                    f"{row['turnaround_time']:<6}{row.get('deadline', '-'):<6}{status:<8}"
                )

    @staticmethod
    def log_lines(lines: list[str], title: str = "Registro de eventos", max_lines: int = 20) -> None:
        print(f"\n  {Fore.CYAN}--- {title} ---{Style.RESET_ALL}")
        for line in lines[-max_lines:]:
            print(f"    {line}")

    @staticmethod
    def key_value(data: dict, title: str = "Resumo") -> None:
        print(f"\n  {Fore.CYAN}{title}:{Style.RESET_ALL}")
        labels = {
            "prevencao": "Prevencao ativa",
            "deadlock_detectado": "Travamento detectado",
            "transferencias_concluidas": "Transferencias concluidas",
            "saldos_finais": "Saldos finais",
            "saldo_conservado": "Integridade do saldo",
            "produced": "Transacoes enviadas pelos ATMs",
            "consumed": "Transacoes processadas",
            "buffer_size": "Transacoes no buffer",
            "capacity": "Capacidade do buffer",
            "expected_balance": "Saldo esperado",
            "actual_balance": "Saldo apurado",
            "correct": "Integridade verificada",
            "protected": "Protecao por trava (mutex)",
            "expected_lines": "Registros esperados",
            "actual_lines": "Registros gravados",
            "allocated_initial": "Operacoes alocadas",
            "blocked_initial": "Operacoes aguardando memoria",
            "unblocked_after_free": "Operacoes liberadas",
            "total_frames": "Total de quadros",
            "used_frames": "Quadros em uso",
            "free_frames": "Quadros livres",
            "page_faults": "Falhas de pagina",
        }
        for key, value in data.items():
            label = labels.get(key, key.replace("_", " ").capitalize())
            if key == "saldos_finais" and isinstance(value, dict):
                print(f"    {label}:")
                for acc_id, bal in value.items():
                    print(f"      C/C {format_account_id(acc_id)}: {format_currency(bal)}")
            elif key in ("actual_balance", "expected_balance") and isinstance(value, float):
                print(f"    {label}: {format_currency(value)}")
            else:
                print(f"    {label}: {value}")

    @staticmethod
    def press_enter(msg: str = "Pressione Enter para voltar ao menu principal...") -> None:
        input(f"\n  {msg}")
