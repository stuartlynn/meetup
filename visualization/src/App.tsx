import { RecoilRoot } from 'recoil'
import React from 'react'
import './App.css'
import { MapView } from './components/MapView'
import { Provider, defaultTheme } from '@adobe/react-spectrum'
import { Sidebar } from './components/Sidebar'
import { Legend } from './components/Legend'

function App() {

  return (
    <Provider theme={defaultTheme}>
      <RecoilRoot>
        <React.Suspense fallback={<h1>Loading</h1>}>
          <MapView />
          <Sidebar />
          <Legend />
        </React.Suspense>
      </RecoilRoot>
    </Provider>
  )
}

export default App
