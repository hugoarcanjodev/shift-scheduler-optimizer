import os
import pandas as pd
import pulp

def solve_shift_scheduling():
    # 1. Carregar os dados de entrada
    if not os.path.exists("data/demand_shifts.csv") or not os.path.exists("data/workers_profile.csv"):
        raise FileNotFoundError("Por favor, rode o script de geração de dados primeiro.")
        
    df_demand = pd.read_csv("data/demand_shifts.csv")
    df_workers = pd.read_csv("data/workers_profile.csv")

    # 2. Definir Conjuntos e Índices
    workers = df_workers["worker_id"].tolist()
    days = sorted(df_demand["day_of_week"].unique())
    shifts = ["A", "B", "C"]  # A=Noturno, B=Matutino, C=Vespertino

    # Dicionários auxiliares para busca rápida de parâmetros
    worker_costs = pd.series(df_workers.hourly_rate.values, index=df_workers.worker_id).to_dict()
    worker_night_pct = pd.series(df_workers.night_premium_pct.values, index=df_workers.worker_id).to_dict()
    
    # Criar dicionário de demanda indexado por (dia, turno)
    demand_dict = df_demand.set_index(["day_of_week", "shift"])["min_workers"].to_dict()

    # 3. Inicializar o Modelo de Otimização no PuLP
    model = pulp.LpProblem("Shift_Scheduler_Optimization", pulp.LpMinimize)

    # 4. Variáveis de Decisão
    # x[i, d, t] = 1 se o trabalhador 'i' trabalha no dia 'd' no turno 't'; 0 caso contrário
    x = pulp.LpVariable.dicts("assign", 
                              ((i, d, t) for i in workers for d in days for t in shifts), 
                              cat=pulp.LpBinary)

    # 5. Função Objetivo: Minimizar o Custo Total da Escala (Considerando Adicional Noturno no Turno A)
    # Turno A (Noturno) recebe um acréscimo de custo baseado no night_premium_pct
    total_cost = []
    for i in workers:
        for d in days:
            for t in shifts:
                base_cost = worker_costs[i] * 8  # 8 horas por turno
                if t == "A":
                    base_cost *= (1 + worker_night_pct[i])
                total_cost.append(x[i, d, t] * base_cost)
                
    model += pulp.lpSum(total_cost), "Total_Operational_Cost"

    # 6. Restrições do Modelo (Constraints)

    # R1: Atender à demanda mínima de cada turno/dia (Garantia de Cobertura Logística)
    for d in days:
        for t in shifts:
            model += pulp.lpSum(x[i, d, t] for i in workers) >= demand_dict[(d, t)], f"Demand_D{d}_S{t}"

    # R2: Ergonomia - Máximo de 1 turno de trabalho por dia para cada colaborador
    for i in workers:
        for d in days:
            model += pulp.lpSum(x[i, d, t] for t in shifts) <= 1, f"Max_1_Shift_Per_Day_W{i}_D{d}"

    # R3: Descanso Interjornada (CLT) - Se trabalhou no Turno C (Vespertino), não pode trabalhar no Turno A (Noturno) do dia seguinte
    # Nota: d=6 é Domingo, o dia seguinte (d=0) volta a ser Segunda-feira no ciclo semanal
    for i in workers:
        for d in days:
            next_day = (d + 1) % 7
            model += x[i, d, "C"] + x[i, next_day, "A"] <= 1, f"CLT_Interjornada_W{i}_D{d}"

    # R4: Jornada Máxima Semanal (Limite de Horas) - Máximo de 44 horas regulares na semana (5.5 turnos de 8h)
    for i in workers:
        model += pulp.lpSum(x[i, d, t] * 8 for d in days for t in shifts) <= 44, f"Max_Hours_W{i}"

    # R5: Garantia de Folga Semanal - Colaborador deve folgar pelo menos 1 dia na semana
    for i in workers:
        model += pulp.lpSum(x[i, d, t] for d in days for t in shifts) <= 6, f"Min_1_Day_Off_W{i}"

    # 7. Resolver o Modelo Matemático
    print("🤖 Executando o Solver CBC do PuLP...")
    status = model.solve(pulp.PULP_CBC_CMD(msg=False))
    
    print(f"📊 Status da Solução: {pulp.LpStatus[status]}")
    
    if pulp.LpStatus[status] != "Optimal":
        print("❌ Não foi possível encontrar uma escala viável com as restrições atuais.")
        return

    # 8. Processar e Exportar os Resultados Otimizados
    output_rows = []
    for d in days:
        for t in shifts:
            for i in workers:
                if pulp.value(x[i, d, t]) == 1:
                    worker_name = df_workers[df_workers["worker_id"] == i]["name"].values[0]
                    output_rows.append({
                        "Day_of_Week": d,
                        "Shift": t,
                        "Worker_ID": i,
                        "Worker_Name": worker_name
                    })

    df_output = pd.DataFrame(output_rows)
    
    # Ordenar para melhor leitura do planejador de logística
    df_output = df_output.sort_values(by=["Day_of_Week", "Shift"])
    
    os.makedirs("output", exist_ok=True)
    df_output.to_csv("output/optimal_schedule.csv", index=False)
    print("✅ Escala otimizada gerada e salva com sucesso em 'output/optimal_schedule.csv'!")

if __name__ == "__main__":
    solve_shift_scheduling()
