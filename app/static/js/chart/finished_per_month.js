// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';



$.getJSON("/json/terminados_por_mes", function (data) {

  january = '0'
  february = '0'
  march = '0'
  april = '0'
  may = '0'
  june = '0'
  july = '0'
  august = '0'
  september = '0'
  october = '0'
  november = '0'
  december = '0'

  tmp_max_value = 0

  for (i = 0; i < data.data.length; i++) {

    if (data.data[i].count > tmp_max_value) {
      tmp_max_value = data.data[i].count
    }

    switch (data.data[i].month) {
      case '01':
        january = data.data[i].count;
        break;
      case '02':
        february = data.data[i].count;
        break;
      case '03':
        march = data.data[i].count;
        break;
      case '04':
        april = data.data[i].count;
        break;
      case '05':
        may = data.data[i].count;
        break;
      case '06':
        june = data.data[i].count;
        break;
      case '07':
        july = data.data[i].count;
        break;
      case '08':
        august = data.data[i].count;
        break;
      case '09':
        september = data.data[i].count;
        break;
      case '10':
        october = data.data[i].count;
        break;
      case '11':
        november = data.data[i].count;
        break;
      case '12':
        december = data.data[i].count;
        break;
    }
  }

  // Bar Chart Example
  var ctx = document.getElementById("chartBar");
  var chartBar = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
      datasets: [{
        label: "Terminados",
        backgroundColor: "#4e73df",
        hoverBackgroundColor: "#2e59d9",
        borderColor: "#4e73df",
        data: [january, february, march, april, may, june, july, august, september, october, november, december],
      }],
    },
    options: {
      maintainAspectRatio: false,
      layout: {
        padding: {
          left: 10,
          right: 25,
          top: 25,
          bottom: 0
        }
      },
      scales: {
        xAxes: [{
          time: {
            unit: 'month'
          },
          gridLines: {
            display: true,
            drawBorder: true
          },
          ticks: {
            maxTicksLimit: 12
          },
          maxBarThickness: 25,
        }],
        yAxes: [{
          ticks: {
            min: 0,
            max: tmp_max_value,
            maxTicksLimit: 6,
            padding: 10,
            // Include a dollar sign in the ticks
            callback: function (value, index, values) {
              //return '$' + number_format(value);
              return number_format(value);
            }
          },
          gridLines: {
            color: "rgb(234, 236, 244)",
            zeroLineColor: "rgb(234, 236, 244)",
            drawBorder: false,
            borderDash: [2],
            zeroLineBorderDash: [2]
          }
        }],
      },
      legend: {
        display: true
      },
      tooltips: {
        titleMarginBottom: 10,
        titleFontColor: '#6e707e',
        titleFontSize: 14,
        backgroundColor: "rgb(255,255,255)",
        bodyFontColor: "#858796",
        borderColor: '#dddfeb',
        borderWidth: 1,
        xPadding: 15,
        yPadding: 15,
        displayColors: false,
        caretPadding: 10,
        callbacks: {
          label: function (tooltipItem, chart) {
            var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
            //return datasetLabel + ': $' + number_format(tooltipItem.yLabel);
            return datasetLabel + ': ' + number_format(tooltipItem.yLabel);
          }
        }
      },
    }
  });
});

$.getJSON("/json/terminados_por_mes_y_clientes", function (data) {

  var data = data.data
  var dataset_test = []
  var random_color = [];
  var dynamicColors = function () {
    var r = Math.floor(Math.random() * 255);
    var g = Math.floor(Math.random() * 255);
    var b = Math.floor(Math.random() * 255);
    return "rgb(" + r + "," + g + "," + b + ")";
  };

  for (i = 0; i < Object.keys(data).length; i++) {

    label = data[i]['client']
    values = []
    values_per_months = []

    january = 0
    february = 0
    march = 0
    april = 0
    may = 0
    june = 0
    july = 0
    august = 0
    september = 0
    october = 0
    november = 0
    december = 0

    for (x = 0; x < Object.keys(data[i]['data']).length; x++) {

      month = data[i]['data'][x]['month']
      count = data[i]['data'][x]['count']

      switch (month) {
        case '01':
          january = count;
          break;
        case '02':
          february = count;
          break;
        case '03':
          march = count;
          break;
        case '04':
          april = count;
          break;
        case '05':
          may = count;
          break;
        case '06':
          june = count;
          break;
        case '07':
          july = count;
          break;
        case '08':
          august = count;
          break;
        case '09':
          september = count;
          break;
        case '10':
          october = count;
          break;
        case '11':
          november = count;
          break;
        case '12':
          december = count;
          break;
      } // switch case
    } // for datos por mes

    values_per_months = [january, february, march, april, may, june, july, august, september, october, november, december]

    random_color = dynamicColors()

    dataset_test.push(
      {
        label: label,
        data: values_per_months,
        backgroundColor: [
          random_color,
          random_color,
          random_color,
          random_color,
          random_color,
          random_color,
          random_color,
          random_color,
          random_color,
          random_color,
          random_color,
          random_color
        ]
      })
  } // fin buble clientes

  // Bar Chart
  var ctx = document.getElementById("chartBar2").getContext('2d');
  var chartBar2 = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
      datasets: dataset_test
    },
    options: {
      maintainAspectRatio: false,
      scales: {
        yAxes: [{
          ticks: { 
            beginAtZero: true,
            callback: function(value) {if (value % 1 === 0) {return value;}} },
          stacked: true
        }],
        xAxes: [{
          stacked: true
        }]
      }
    }
  })

})