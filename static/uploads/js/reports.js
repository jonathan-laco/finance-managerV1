document.addEventListener("DOMContentLoaded", () => {
  // Gráfico de Categorias de Despesas
  const expenseCategoryElement = document.getElementById(
    "expenseCategoryChart"
  );
  if (expenseCategoryElement) {
    const expenseCategoryCtx = expenseCategoryElement.getContext("2d");
    new Chart(expenseCategoryCtx, {
      type: "doughnut",
      data: {
        labels: Object.keys(expenseCategories),
        datasets: [
          {
            data: Object.values(expenseCategories),
            backgroundColor: Object.keys(expenseCategories).map(
              (category) => expenseColors[category]
            ),
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "right",
          },
          tooltip: {
            callbacks: {
              label: (context) => {
                const label = context.label || "";
                const value = context.raw || 0;
                return `${label}: R$ ${value.toFixed(2)}`;
              },
            },
          },
        },
      },
    });
  }

  // Gráfico de Evolução Diária
  const dailyChartElement = document.getElementById("dailyChart");
  if (dailyChartElement) {
    const dailyCtx = dailyChartElement.getContext("2d");
    new Chart(dailyCtx, {
      type: "line",
      data: {
        labels: Object.keys(dailyData),
        datasets: [
          {
            label: "Receitas",
            borderColor: "#28a745",
            backgroundColor: "rgba(40, 167, 69, 0.2)",
            data: Object.values(dailyData).map((values) => values["receita"]),
            fill: true,
            tension: 0.4,
          },
          {
            label: "Despesas",
            borderColor: "#dc3545",
            backgroundColor: "rgba(220, 53, 69, 0.2)",
            data: Object.values(dailyData).map((values) => values["despesa"]),
            fill: true,
            tension: 0.4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: (value) => `R$ ${value.toFixed(2)}`,
            },
          },
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: (context) => {
                const label = context.dataset.label || "";
                const value = context.raw || 0;
                return `${label}: R$ ${value.toFixed(2)}`;
              },
            },
          },
        },
      },
    });
  }

  // Gráfico de Evolução Mensal
  const monthlyChartElement = document.getElementById("monthlyChart");
  if (monthlyChartElement) {
    const monthlyCtx = monthlyChartElement.getContext("2d");
    new Chart(monthlyCtx, {
      type: "line",
      data: {
        labels: Object.keys(monthlyData),
        datasets: [
          {
            label: "Receitas",
            borderColor: "#28a745",
            backgroundColor: "rgba(40, 167, 69, 0.2)",
            data: Object.values(monthlyData).map((values) => values["receita"]),
            fill: true,
            tension: 0.4,
          },
          {
            label: "Despesas",
            borderColor: "#dc3545",
            backgroundColor: "rgba(220, 53, 69, 0.2)",
            data: Object.values(monthlyData).map((values) => values["despesa"]),
            fill: true,
            tension: 0.4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: (value) => `R$ ${value.toFixed(2)}`,
            },
          },
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: (context) => {
                const label = context.dataset.label || "";
                const value = context.raw || 0;
                return `${label}: R$ ${value.toFixed(2)}`;
              },
            },
          },
        },
      },
    });
  }
});
