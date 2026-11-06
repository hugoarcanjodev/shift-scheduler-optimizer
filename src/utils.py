import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def plot_gantt_schedule():
    # 1. Carregar os dados da escala otimizada e o perfil dos funcionários
    schedule_path = "output/optimal_schedule.csv"
    workers_path = "data/workers_profile.csv"

    if not os.path.exists(schedule_path) or not os.path.exists(workers_path):
        raise FileNotFoundError(
            "Certifique-se de rodar src/generate_data.py e src/model.py antes de gerar o gráfico."
        )

    df_schedule = pd.read_csv(schedule_path)
    df_workers = pd.read_csv(workers_path)

    # Mapeamentos para o gráfico
    days_labels = [
        "Segunda",
        "Terça",
        "Quarta",
        "Quinta",
        "Sexta",
        "Sábado",
        "Domingo",
    ]
    shift_hours = {
        "A": (0, 8, "Noturno (00h-08h)"),
        "B": (8, 16, "Matutino (08h-16h)"),
        "C": (16, 24, "Vespertino (16h-24h)"),
    }

    # Definir paleta de cores elegantes para os turnos usando Seaborn
    colors = {"A": "#1f77b4", "B": "#ff7f0e", "C": "#2ca02c"}  # Azul  # Laranja  # Verde

    # Configuração da figura do Matplotlib
    workers_list = sorted(df_workers["worker_id"].tolist(), reverse=True)
    fig, ax = plt.subplots(figsize=(14, 7))

    # 2. Plotar as barras do Gantt
    for _, row in df_schedule.iterrows():
        worker = row["Worker_ID"]
        day = row["Day_of_Week"]
        shift = row["Shift"]

        # Calcular os tempos no eixo X (Tempo Contínuo na Semana em Horas)
        # Cada dia tem 24h. O dia 0 começa em 0h, o dia 1 começa em 24h, etc.
        start_hour = (day * 24) + shift_hours[shift][0]
        duration = 8

        # Encontrar a posição do trabalhador no eixo Y
        y_pos = workers_list.index(worker)

        # Desenhar a barra horizontal do turno
        ax.broken_barh(
            [(start_hour, duration)],
            (y_pos - 0.35, 0.7),
            facecolors=colors[shift],
            edgecolor="black",
            linewidth=0.5,
            alpha=0.85,
        )

    # 3. Estilização do Gráfico
    ax.set_title(
        "Shift Scheduler Optimizer - Escala Semanal de Trabalho Otimizada",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )
    ax.set_ylabel("Código do Colaborador (Força de Trabalho)", fontsize=12)
    ax.set_xlabel("Cronograma Semanal (Dias da Semana)", fontsize=12)

    # Configurar o eixo Y (Trabalhadores)
    ax.set_yticks(range(len(workers_list)))
    ax.set_yticklabels(
        [
            f"{w} - {df_workers[df_workers['worker_id']==w]['name'].values[0]}"
            for w in workers_list
        ]
    )

    # Configurar o eixo X (Divisão perfeita por dias da semana)
    day_ticks = np.arange(0, 7 * 24, 24)
    ax.set_xticks(day_ticks)
    ax.set_xticklabels(days_labels, fontsize=10)

    # Adicionar linhas de grade verticais pontilhadas para separar visualmente os dias
    ax.grid(axis="x", linestyle="--", alpha=0.7)

    # Criar legenda customizada de turnos
    legend_elements = [
        plt.Line2D(,
 ,
            marker="o",
            color="w",
            label=shift_hours[s][2],
            markerfacecolor=colors[s],
            markersize=10,
        )
        for s in ["A", "B", "C"]
    ]
    ax.legend(
        handles=legend_elements,
        title="Turnos Operacionais",
        loc="upper right",
        bbox_to_anchor=(1.15, 1),
    )

    plt.tight_layout()

    # 4. Salvar o output visual
    os.makedirs("output", exist_ok=True)
    output_img_path = "output/gantt_schedule.png"
    plt.savefig(output_img_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(
        f"📊 Gráfico de Gantt gerado com sucesso e salvo em '{output_img_path}'!"
    )


if __name__ == "__main__":
    plot_gantt_schedule()
