import type { Agent } from './types'
import { useConversations, useAgentDetail } from './hooks'

interface Props {
  agents: Agent[]
  selectedAgent: string | null
  onSelectAgent: (name: string | null) => void
}

function NeedBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 11 }}>
      <span style={{ width: 14 }}>{label}</span>
      <div style={{ flex: 1, height: 6, background: '#2a2a4e', borderRadius: 3 }}>
        <div style={{ width: `${value}%`, height: '100%', background: color, borderRadius: 3 }} />
      </div>
      <span style={{ width: 28, textAlign: 'right' }}>{value.toFixed(0)}</span>
    </div>
  )
}

export default function Sidebar({ agents, selectedAgent, onSelectAgent }: Props) {
  const convos = useConversations()
  const { detail } = useAgentDetail(selectedAgent)

  return (
    <div style={{ width: 320, display: 'flex', flexDirection: 'column', gap: 8, fontSize: 12 }}>
      {/* Agent List */}
      <div style={{ background: '#16213e', borderRadius: 6, padding: 8 }}>
        <h3 style={{ fontSize: 13, marginBottom: 6, color: '#4d96ff' }}>Agents ({agents.filter(a => a.is_alive).length})</h3>
        {agents.map((a, i) => (
          <div
            key={a.id}
            onClick={() => onSelectAgent(a.name)}
            style={{
              padding: '4px 6px',
              borderRadius: 4,
              cursor: 'pointer',
              background: selectedAgent === a.name ? '#2a2a5e' : 'transparent',
              opacity: a.is_alive ? 1 : 0.4,
              marginBottom: 2,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ fontWeight: 'bold' }}>{a.name}</span>
              <span style={{ color: '#888' }}>{a.agent_type === 'system' ? '⚙' : '●'}</span>
            </div>
            <NeedBar label="E" value={a.energy} color="#6bcb77" />
            <NeedBar label="K" value={a.knowledge} color="#4d96ff" />
            <NeedBar label="I" value={a.influence} color="#ffd93d" />
          </div>
        ))}
      </div>

      {/* Selected Agent Detail */}
      {selectedAgent && detail && (
        <div style={{ background: '#16213e', borderRadius: 6, padding: 8 }}>
          <h3 style={{ fontSize: 13, marginBottom: 6, color: '#4d96ff' }}>{selectedAgent}</h3>
          <pre style={{ fontSize: 10, whiteSpace: 'pre-wrap', color: '#ccc', lineHeight: 1.4 }}>{detail}</pre>
        </div>
      )}

      {/* Conversations */}
      <div style={{ background: '#16213e', borderRadius: 6, padding: 8, flex: 1, overflow: 'auto' }}>
        <h3 style={{ fontSize: 13, marginBottom: 6, color: '#4d96ff' }}>Conversations</h3>
        <pre style={{ fontSize: 10, whiteSpace: 'pre-wrap', color: '#aaa', lineHeight: 1.4 }}>{convos || '(none yet)'}</pre>
      </div>
    </div>
  )
}
