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
    "dataProvider": [ {
        "category": "ff",
        "segments": [ ]
        },{
        "category": "light",
        "segments": [ {
                        "start": 12
,
                        "duration": 1,
                        "color": "#33CCFF"
                    },{
                        "start": 13
,
                        "duration": 1,
                        "color": "#33CCFF"
                    },{
                        "start": 14
,
                        "duration": 1,
                        "color": "#33CCFF"
                    },{
                        "start": 15
,
                        "duration": 1,
                        "color": "#33CCFF"
                    },{
                        "start": 17
,
                        "duration": 1,
                        "color": "#33CCFF"
                    },{
                        "start": 18
,
                        "duration": 1,
                        "color": "#33CCFF"
                    },{
                        "start": 25
,
                        "duration": 1,
                        "color": "#33CCFF"
                    },{
                        "start": 28
,
                        "duration": 1,
                        "color": "#33CCFF"
                    },]
        }, ],
        "valueScrollbar": {
            "autoGridCount":false
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