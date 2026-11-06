import os
import pandas as pd


def audit_schedule_compliance():
    print("🔍 Iniciando Auditoria de Compliance Trabalhista (CLT)...")

    # 1. Carregar os arquivos
    schedule_path = "output/optimal_schedule.csv"
    if not os.path.exists(schedule_path):
        raise FileNotFoundError(
            "Arquivo de escala não encontrado. Execute o otimizador primeiro."
        )

    df_schedule = pd.read_csv(schedule_path)

    # Inicializar contadores de erros/alertas
    violations_found = 0
    workers = df_schedule["Worker_ID"].unique()

    # --- AUDITORIA 1: Descanso Interjornada (Mínimo de 11h pela CLT) ---
    # Tradução operacional: Quem trabalha no Turno C (termina às 24h) não pode entrar no Turno A (começa às 00h) do dia seguinte.
    print("\n➡️ Checando descanso interjornada (Regra Turno C -> Turno A)...")
    for worker in workers:
        df_worker = df_schedule[df_schedule["Worker_ID"] == worker]

        for _, row in df_worker.iterrows():
            day = row["Day_of_Week"]
            shift = row["Shift"]

            if shift == "C":
                next_day = (day + 1) % 7
                # Verificar se o mesmo funcionário está escalado no Turno A do dia seguinte
                has_violation = df_worker[
                    (df_worker["Day_of_Week"] == next_day)
                    & (df_worker["Shift"] == "A")
                ]

                if not has_violation.empty:
                    print(
                        f"❌ VIOLAÇÃO CLT: Colaborador {worker} trabalhou no Turno C no Dia {day} e entrou no Turno A no Dia {next_day}!"
                    )
                    violations_found += 1

    # --- AUDITORIA 2: Limite de Jornada Diária ---
    # Regulamento interno/CLT: Máximo de 1 turno alocado por dia por pessoa.
    print("➡️ Checando limite de turnos diários...")
    daily_shifts = (
        df_schedule.groupby(["Worker_ID", "Day_of_Week"])["Shift"]
        .count()
        .reset_index()
    )
    overworked_days = daily_shifts[daily_shifts["Shift"] > 1]

    if not overworked_days.empty:
        for _, row in overworked_days.iterrows():
            print(
                f"❌ VIOLAÇÃO OPERACIONAL: Colaborador {row['Worker_ID']} possui {row['Shift']} turnos no mesmo Dia ({row['Day_of_Week']})!"
            )
            violations_found += 1

    # --- AUDITORIA 3: Jornada Máxima Semanal (44 Horas Máximas) ---
    print("➡️ Checando limite de 44 horas semanais por contrato...")
    # Cada turno mapeado no MVP equivale a 8 horas de trabalho regular
    weekly_hours = (
        df_schedule.groupby("Worker_ID")["Shift"].count().reset_index()
    )
    weekly_hours["Total_Hours"] = weekly_hours["Shift"] * 8

    hours_violations = weekly_hours[weekly_hours["Total_Hours"] > 44]
    if not hours_violations.empty:
        for _, row in hours_violations.iterrows():
            print(
                f"❌ VIOLAÇÃO CONTRATUAL: Colaborador {row['Worker_ID']} extrapolou o limite semanal com {row['Total_Hours']}h!"
            )
            violations_found += 1

    # --- AUDITORIA 4: Garantia de Folga Semanal ---
    # Regulamento: Ninguém pode trabalhar os 7 dias da semana seguidos (mínimo de 1 dia de folga).
    print("➡️ Checando garantia de folga semanal...")
    days_worked = (
        df_schedule.groupby("Worker_ID")["Day_of_Week"].nunique().reset_index()
    )

    no_rest_days = days_worked[days_worked["Day_of_Week"] >= 7]
    if not no_rest_days.empty:
        for _, row in no_rest_days.iterrows():
            print(
                f"❌ VIOLAÇÃO BIOLÓGICA/CLT: Colaborador {row['Worker_ID']} trabalhou os 7 dias da semana sem folga!"
            )
            violations_found += 1

    # 2. Resumo Executivo da Auditoria
    print("\n" + "=" * 50)
    print("📊 RESULTADO FINAL DA AUDITORIA DE COMPLIANCE")
    print("=" * 50)
    if violations_found == 0:
        print(
            "🟢 PARABÉNS! Escala 100% em Compliance. Zero inconformidades detectadas."
        )
        print("💡 Status do Risco Trabalhista: Controlado (0%)")
    else:
        print(
            f"🔴 ATENÇÃO: Foram encontradas {violations_found} inconformidades na escala atual."
        )
        print("💡 Status do Risco Trabalhista: CRÍTICO (Ajustes necessários)")
    print("=" * 50)


if __name__ == "__main__":
    audit_schedule_compliance()
