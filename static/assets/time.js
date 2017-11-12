var chart = AmCharts.makeChart( "chartdiv", {
    "type": "gantt",
    "theme": "light",
    "marginRight": 70,
    "period": "ss",
    "dataDateFormat":"YYYY-MM-DD",
    "balloonDateFormat": "JJ:NN:SS",
    "columnWidth": 0.5,
    "valueAxis": {
        "type": "date"
    },
    "brightnessStep": 10,
    "graph": {
        "fillAlphas": 1,
        "balloonText": "<b>[[task]]</b>: [[open]] [[value]]"
    },
    "rotate": true,
    "categoryField": "category",
    "segmentsField": "segments",
    "colorField": "color",
    "startDate": "2017-10-01",
    "startField": "start",
    "endField": "end",
    "durationField": "duration",
    "dataProvider": [  ],
        "valueScrollbar": {
            "autoGridCount":true
        },
        "chartCursor": {
            "cursorColor":"#55bb76",
            "valueBalloonsEnabled": false,
            "cursorAlpha": 0,
            "valueLineAlpha":0.5,
            "valueLineBalloonEnabled": true,
            "valueLineEnabled": true,
            "zoomable":false,
            "valueZoomable":true
        },
        "export": {
            "enabled": true
         }
    } );