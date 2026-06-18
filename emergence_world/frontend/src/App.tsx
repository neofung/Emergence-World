import { useState } from 'react'
import WorldCanvas from './WorldCanvas'
import Sidebar from './Sidebar'
import ControlPanel from './ControlPanel'
import { useAgents, useLandmarks, useSimStatus } from './hooks'

export default function App() {
  const agents = useAgents()
  const landmarks = useLandmarks()
  const simStatus = useSimStatus()
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const [selectedLandmark, setSelectedLandmark] = useState<string | null>(null)

  const handleSelectAgent = (name: string | null) => {
    setSelectedAgent(name)
    if (name) setSelectedLandmark(null)
  }
  const handleSelectLandmark = (name: string | null) => {
    setSelectedLandmark(name)
    if (name) setSelectedAgent(null)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', gap: 8, padding: 8 }}>
      <ControlPanel status={simStatus} onRefresh={() => {}} />
      <div style={{ display: 'flex', flex: 1, gap: 8, overflow: 'hidden' }}>
        <WorldCanvas
          landmarks={landmarks}
          agents={agents}
          selectedAgent={selectedAgent}
          selectedLandmark={selectedLandmark}
          onSelectAgent={handleSelectAgent}
          onSelectLandmark={handleSelectLandmark}
        />
        <Sidebar
          agents={agents}
          landmarks={landmarks}
          selectedAgent={selectedAgent}
          selectedLandmark={selectedLandmark}
          onSelectAgent={handleSelectAgent}
        />
      </div>
    </div>
  )
}
