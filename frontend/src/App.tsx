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

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', gap: 8, padding: 8 }}>
      <ControlPanel status={simStatus} onRefresh={() => {}} />
      <div style={{ display: 'flex', flex: 1, gap: 8, overflow: 'hidden' }}>
        <WorldCanvas
          landmarks={landmarks}
          agents={agents}
          selectedAgent={selectedAgent}
          onSelectAgent={setSelectedAgent}
        />
        <Sidebar
          agents={agents}
          selectedAgent={selectedAgent}
          onSelectAgent={setSelectedAgent}
        />
      </div>
    </div>
  )
}
