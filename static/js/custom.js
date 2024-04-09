const ctx = document.getElementById("myChart");

new Chart(ctx, {
  type: "doughnut",
  data: {
    // labels: ["Red", "Blue", "Yellow"],
    labels: [
      "My First Dataset",
      "My Second Dataset",
      "My Third Dataset",
      "My Fourth Dataset",
      "My Fifth Dataset",
    ],
    datasets: [
      {
        data: [200, 50, 100, 40, 120],
        backgroundColor: [
          "#696cff",
          "#71dd37",
          "#03c3ec",
          "#ffab00",
          "#8592a3",
        ],
        hoverOffset: 4,
      },
    ],
  },
  options: {
    responsive: true,
    // maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        enabled: true,
      },
      datalabels: {
        display: false, // Menyembunyikan label
      },
    },
  },
});
