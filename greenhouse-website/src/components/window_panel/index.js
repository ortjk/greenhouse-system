import React, {useState} from 'react'

import Card from 'react-bootstrap/Card'
import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'

import './index.css'

export default function WindowPanel({url}) {
    const [manualEnabled, setManualEnabled] = useState(false);

    const toggleManualEnable = () => {
        setManualEnabled(!manualEnabled);
    }

    const clickableStyles = {
        false: {
            backgroundColor: 'grey',
            textColor: 'darkgrey',
            cursor: 'pointer',
        },
        true: {}
    }

    return (
        <Card style={{width: '40rem'}}>
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
                            />
                        </div>
                        <div className='switch-field-container'>
                            <span className='switch-label'>Manually Open Window</span>
                            <Form.Check
                                type="switch"
                                id="open-switch"
                                name="open-switch-value"
                                style={clickableStyles[manualEnabled]}
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
                                style={clickableStyles[!manualEnabled]}
                            />
                            <span className='switch-label'>°C</span>
                        </div>
                        <div className='numeric-field-container'>
                            <span className='switch-label'>Temperature to Close Window</span>
                            <Form.Control
                                id="close-temperature"
                                name="close-temperature-value"
                                style={clickableStyles[!manualEnabled]}
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
