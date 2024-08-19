import React, {useState} from 'react'

import WindowPanel from '../../components/window_panel'

export default function Main() {
    return (
        <div className="main-container">
            <WindowPanel url="/set-config" />
        </div>
    )
}
