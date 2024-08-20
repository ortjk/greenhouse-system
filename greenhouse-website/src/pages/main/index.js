import React, {useState, useEffect} from 'react'

import './index.css'

import Button from 'react-bootstrap/Button'
import ButtonGroup from 'react-bootstrap/ButtonGroup'
import ButtonToolbar from 'react-bootstrap/ButtonToolbar'

import WindowPanel from '../../components/window_panel'
import HistoryChart from '../../components/history_chart'

export default function Main() {
    const [timeframe, setTimeframe] = useState(0);
    const [period, setPeriod] = useState(0);
    const [arduConf, setArduConf] = useState({});
    const [graphData, setGraphData] = useState({});
    const [stacked, setStacked] = useState(false);

    const tf = [
        3600 * 60,
        3600 * 24,
        3600 * 24 * 7,
        3600 * 24 * 30
    ];

    const pd = [
        60,
        3600,
        3600 * 24
    ]

    const btnCondStyles = {
        false: "outline-primary",
        true: "primary"
    }

    const stackDict = {
        false: {
            gridTemplateColumns: '33% auto',
            gridTemplateRows: 'auto',
        },
        true: {
            gridTemplateColumns: 'auto',
            gridTemplateRows: 'auto auto',
        }
    };

    const toggleStacked = (width) => {
        if (width > 1100) {
            setStacked(false);
        }
        else {
            setStacked(true);
        }
    };

    useEffect(() => {
        fetch('/get-config').then(res => res.json()).then(data => {
            setArduConf(data);
        });
    }, []);

    useEffect(() => {
        fetch(`/graph?lookback=${tf[timeframe]}&period=${pd[period]}`).then(res => res.json()).then(data => {
            console.log(data);
            setGraphData(data);
        });
    }, [timeframe, period]);

    useEffect(() => {
        const handleResize = () => toggleStacked(window.innerWidth);
        window.addEventListener("resize", handleResize);
        return () => window.removeEventListener("resize", handleResize);
    }, []);

    // extra call for the beginning of rendering
    useEffect(() => {
        toggleStacked(window.innerWidth);
    }, []);

    return (
        <div className="main-container" style={stackDict[stacked]}>
            <div>
                <WindowPanel url="/set-config" entries={arduConf} />
            </div>
            <div>
                <h4>Climate History</h4>
                <HistoryChart data={graphData.data} />
                <div className='button-toolbar-center'>
                    <div>
                        <h5>Period: </h5>
                        <ButtonGroup className="me-4" size="sm">
                            <Button variant={btnCondStyles[timeframe === 0]} onClick={() => setTimeframe(0)}>Hour</Button>
                            <Button variant={btnCondStyles[timeframe === 1]} onClick={() => setTimeframe(1)}>Day</Button>
                            <Button variant={btnCondStyles[timeframe === 2]} onClick={() => setTimeframe(2)}>Week</Button>
                            <Button variant={btnCondStyles[timeframe === 3]} onClick={() => setTimeframe(3)}>Month</Button>
                        </ButtonGroup>
                    </div>
                    <div>
                        <h5>Step: </h5>
                        <ButtonGroup size="sm">
                            <Button variant={btnCondStyles[period === 0]} onClick={() => setPeriod(0)}>Minute</Button>
                            <Button variant={btnCondStyles[period === 1]} onClick={() => setPeriod(1)}>Hour</Button>
                            <Button variant={btnCondStyles[period === 2]} onClick={() => setPeriod(2)}>Day</Button>
                        </ButtonGroup>
                    </div>
                </div>
            </div>
        </div>
    )
}
