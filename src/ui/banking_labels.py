"""Rotulos e textos do sistema bancario para a interface."""

BANK_NAME = "BANCO NEXUS"
BRANCH = "Agencia Digital 001"
SYSTEM_TITLE = "Sistema de Operacoes em Tempo Real"

STATE_LABELS = {
    "NEW": "Entrada",
    "READY": "Na fila",
    "RUNNING": "Processando",
    "BLOCKED": "Suspensa",
    "TERMINATED": "Concluida",
}

PRIORITY_LABELS = {
    "VIP": "Private",
    "NORMAL": "Corrente",
    "BATCH": "Backoffice",
}

BLOCK_REASON_LABELS = {
    "memoria": "Aguardando memoria de cache",
}

SCHEDULER_LABELS = {
    "RR": "Fila justa (Round Robin)",
    "PRIORITY": "Clientes prioritarios",
    "EDF": "Operacoes urgentes (EDF)",
}


def format_account_id(account_id: int) -> str:
    return f"{account_id:04d}-{account_id * 7 % 10000:04d}-{account_id * 13 % 10000:04d}"


def format_currency(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def block_reason_label(reason: str) -> str:
    if not reason:
        return ""
    if reason in BLOCK_REASON_LABELS:
        return BLOCK_REASON_LABELS[reason]
    if reason.startswith("conta_"):
        acc = reason.split("_", 1)[1]
        return f"Conta {format_account_id(int(acc))} em uso"
    return reason
