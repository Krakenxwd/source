Highcharts.setOptions({
	colors: [
        '#5089fb',
		'#1e68fa',
		'#3778fb',
		"#699afc",
		"#9bbcfd",
		"#82abfc",
	],
});

let splineChartDocumentsData = document.querySelector('#splineChartDocuments').textContent;
let splineChartDocuments = JSON.parse(splineChartDocumentsData);
let datesArray = []
let uploadedArray = []
splineChartDocuments.forEach((obj) => {
    if (Object.keys(obj.data).length > 0) {
        Object.keys(obj.data).forEach(function (dateStr) {
            let parts = dateStr.split("/");
            let year = parseInt(parts[0]);
            let month = parseInt(parts[1]) - 1; // Months are zero-based in Date.UTC
            let day = parseInt(parts[2]);
            datesArray.push(Date.UTC(year, month, day))
        });
    }
    if (Object.values(obj.data).length > 0) {
        Object.values(obj.data).forEach((value) => {
            uploadedArray.push(value)
        })
    }
})

if (datesArray.length > 0) {
    Highcharts.chart("spline-chart", {
        legend: {
            enabled: true,
        },
        credits: {
            enabled: false,
        },
        chart: {
            type: "column",
        },
        title: {
            text: "",
        },
        xAxis: {
            type: "datetime",
            useUTC: true,
            categories: datesArray,
            labels: {
                formatter: function () {
                    return Highcharts.dateFormat("%d-%m-%Y", this.value);
                },
            },
        },
        yAxis: {
            title: {
                text: "Documents Uploaded",
            },
        },
        tooltip: {
            formatter: function () {
                return `${Highcharts.dateFormat(
                    "%Y-%b-%d",
                    this.x
                )} Documents Uploaded: ${this.y}`;
            },
        },
        plotOptions: {
            areaspline: {
                pointWidth: 5,
                marker: {
                    enabled: false,
                    symbol: "circle",
                    radius: 2,
                    states: {
                        hover: {
                            enabled: true,
                        },
                    },
                },
                color: "#3778FB",
            },
        },
        series: [
            {
                name: "Success",
                data: uploadedArray,
            },
            {
                name: "Queued",
                data: [],
            }
        ]
    });
} else {
    document.querySelector('#spline-chart').innerHTML = document.querySelector('.placeholder-div').innerHTML
}


let userWisePieChartData = document.querySelector('#pieChartUserDocuments').textContent;
let userWisePieChart = JSON.parse(userWisePieChartData);
if ( userWisePieChart.length > 0 ) {
    Highcharts.chart("container-pie-chart-1", {
        credits: {
            enabled: false,
        },
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: "pie",
        },
        title: {
            text: "",
            align: "left",
        },
        tooltip: {
            pointFormat: "<b>{point.percentage:.1f}%</b><br>Count:{point.y}",
        },
        accessibility: {
            point: {
                valueSuffix: "%",
            },
        },
        plotOptions: {
            pie: {
                innerSize: "50%",
                allowPointSelect: true,
                cursor: "pointer",
                dataLabels: {
                    enabled: false,
                },
                showInLegend: true,
            },
        },
        series: [
            {
                name: "Mode",
                colorByPoint: true,
                data: userWisePieChart,
            },
        ],
    });
} else {
    document.querySelector('#container-pie-chart-1').innerHTML = document.querySelector('.placeholder-div').innerHTML
}

let pieChartDocumentStatusData = document.querySelector('#pieChartDocumentStatus').textContent;
let pieChartDocumentStatus = JSON.parse(pieChartDocumentStatusData);
if ( pieChartDocumentStatus.length > 0 ) {
    Highcharts.chart("container-pie-chart-2", {
        credits: {
            enabled: false,
        },
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: "pie",
        },
        title: {
            text: "",
            align: "left",
        },
        tooltip: {
            pointFormat: "<b>{point.percentage:.1f}%</b><br>Count:{point.y}",
        },
        accessibility: {
            point: {
                valueSuffix: "%",
            },
        },
        plotOptions: {
            pie: {
                innerSize: "50%",
                allowPointSelect: true,
                cursor: "pointer",
                dataLabels: {
                    enabled: false,
                },
                showInLegend: true,
            },
        },
        series: [
            {
                name: "Mode",
                colorByPoint: true,
                data: pieChartDocumentStatus,
            },
        ],
    });
} else {
    document.querySelector('#container-pie-chart-2').innerHTML = document.querySelector('.placeholder-div').innerHTML
}

let pieChartDocumentAppTypeData = document.querySelector('#pieChartDocumentAppType').textContent;
let pieChartDocumentAppType = JSON.parse(pieChartDocumentAppTypeData);
if ( pieChartDocumentAppType.length > 0 ) {
    Highcharts.chart("container-pie-chart-3", {
        credits: {
            enabled: false,
        },
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: "pie",
        },
        title: {
            text: "",
            align: "left",
        },
        tooltip: {
            pointFormat: "<b>{point.percentage:.1f}%</b><br>Count:{point.y}",
        },
        accessibility: {
            point: {
                valueSuffix: "%",
            },
        },
        plotOptions: {
            pie: {
                innerSize: "50%",
                allowPointSelect: true,
                cursor: "pointer",
                dataLabels: {
                    enabled: false,
                },
                showInLegend: true,
            },
        },
        series: [
            {
                name: "Mode",
                colorByPoint: true,
                data: pieChartDocumentAppType,
            },
        ],
    });
} else {
    document.querySelector('#container-pie-chart-3').innerHTML = document.querySelector('.placeholder-div').innerHTML
}

let pieChartDocumentPageLabelData = document.querySelector('#pieChartPageLabels').textContent;
let pieChartDocumentPageLabel = JSON.parse(pieChartDocumentPageLabelData);
if ( pieChartDocumentPageLabel.length > 0 ) {
    Highcharts.chart("container-pie-chart-4", {
        credits: {
            enabled: false,
        },
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: "pie",
        },
        title: {
            text: "",
            align: "left",
        },
        tooltip: {
            pointFormat: "<b>{point.percentage:.1f}%</b><br>Count:{point.y}",
        },
        accessibility: {
            point: {
                valueSuffix: "%",
            },
        },
        plotOptions: {
            pie: {
                innerSize: "50%",
                allowPointSelect: true,
                cursor: "pointer",
                dataLabels: {
                    enabled: false,
                },
                showInLegend: true,
            },
        },
        series: [
            {
                name: "Mode",
                colorByPoint: true,
                data: pieChartDocumentPageLabel,
            },
        ],
    });
} else {
    document.querySelector('#container-pie-chart-4').innerHTML = document.querySelector('.placeholder-div').innerHTML
}