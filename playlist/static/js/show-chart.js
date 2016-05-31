Chart.defaults.global.responsive = true;
Chart.defaults.global.legend.display =false
var ctx = document.getElementById("showStats").getContext("2d");
var options = {
    type: 'bar', 
    data: statsData, 
    options: {
        scales: {
            yAxes: [
                { 
                    ticks: {beginAtZero: true}
                }
            ]
        }
    }
}
var statsChart = new Chart(ctx, options);
