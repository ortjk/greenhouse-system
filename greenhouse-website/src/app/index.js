import React from 'react'
import {Routes, Route} from 'react-router-dom'

import Main from '../pages/main'

export default ({...props}) => {
    return (
        <div className="app-container">
            <Routes>
                <Route path='/' element={Main} />
            </Routes>
        </div>
    )
}

