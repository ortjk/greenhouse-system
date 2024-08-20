import React, {useState, useEffect} from 'react'

import Card from 'react-bootstrap/Card'
import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'

import './index.css'

export default function WindowPanel({url, entries}) {
    const [manualEnabled, setManualEnabled] = useState(false);

    const toggleManualEnable = () => {
        setManualEnabled(!manualEnabled);
    }

    useEffect(() => {
        if (entries.enable_manual) {
            setManualEnabled(true);
        }
    }, [entries]);

    const switchFieldStyles = {
        false: "blanked-switch",
        true: ""
    };

    const textFieldStyles = {
        false: {
            backgroundColor: 'grey',
            textColor: 'darkgrey',
            cursor: 'pointer',
        },
        true: {}
    };


    return (
        <Card>
            <Card.Body>
                <Card.Title>Window Control</Card.Title>
                <form className='form-container' method="POST" action={url}>
                    <div className='form-group'>
                        <Card.Subtitle>Manual Control</Card.Subtitle>
                        <div className='switch-field-container'>
                            <span className='switch-label'>Enable Manual Control</span>
                            <Form.Check
                                checked={manualEnabled}
                                onChange={toggleManualEnable}
                                type="switch"
                                id="enable-switch"
                                name="enable-switch-value"
                                defaultChecked={entries.enable_manual}
                            />
                        </div>
                        <div className='switch-field-container'>
                            <span className='switch-label'>Manually Open Window</span>
                            <Form.Check
                                type="switch"
                                id="open-switch"
                                name="open-switch-value"
                                defaultChecked={entries.open_manual}
                                className={switchFieldStyles[manualEnabled]}
                            />
                        </div>
                    </div>
                    <div className='form-group'>
                        <Card.Subtitle>Temperature Setpoints</Card.Subtitle>
                        <div className='numeric-field-container'>
                            <span className='switch-label'>Temperature to Open Window</span>
                            <Form.Control
                                id="open-temperature"
                                name="open-temperature-value"
                                defaultValue={entries.open_temperature}
                                style={textFieldStyles[!manualEnabled]}
                            />
                            <span className='switch-label'>°C</span>
                        </div>
                        <div className='numeric-field-container'>
                            <span className='switch-label'>Temperature to Close Window</span>
                            <Form.Control
                                id="close-temperature"
                                name="close-temperature-value"
                                defaultValue={entries.close_temperature}
                                style={textFieldStyles[!manualEnabled]}
                            />
                            <span className='switch-label'>°C</span>
                        </div>
                    </div>
                    <Button className='submit-button' type='submit' >Submit</Button>
                </form>
            </Card.Body>
        </Card>
    )
}
