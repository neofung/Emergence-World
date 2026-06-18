import { useState, useMemo } from 'react'
import type { Agent, Landmark } from './types'
import { useConversations, useAgentDetail } from './hooks'
import { AGENT_COLORS } from './colors'

interface Props {
  agents: Agent[]
  landmarks: Landmark[]
  selectedAgent: string | null
  selectedLandmark: string | null
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

function colorize(text: string, colorMap: Record<string, string>, nameMap: Record<string, string>): string {
  // Sort names by length descending to avoid partial matches
  const names = Object.keys(colorMap).sort((a, b) => b.length - a.length)
  if (names.length === 0) return text
  const re = new RegExp(`\\b(${names.map(n => n.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})\\b`, 'g')
  return text.replace(re, (name) => {
    const color = colorMap[name]
    const display = nameMap[name] || name
    return `<span style="color:${color};font-weight:bold">${display}</span>`
  })
}

export default function Sidebar({ agents, landmarks, selectedAgent, selectedLandmark, onSelectAgent }: Props) {
  const convos = useConversations()
  const { detail } = useAgentDetail(selectedAgent)
  const [agentsOpen, setAgentsOpen] = useState(true)

  const colorMap = useMemo(() => {
    const map: Record<string, string> = {}
    agents.forEach((a, i) => { map[a.name] = AGENT_COLORS[i % AGENT_COLORS.length] })
    return map
  }, [agents])

  const displayNameMap = useMemo(() => {
    const map: Record<string, string> = {}
    agents.forEach(a => { map[a.name] = a.display_name || a.name })
    return map
  }, [agents])

  return (
    <div style={{ width: 320, display: 'flex', flexDirection: 'column', gap: 8, fontSize: 12, overflow: 'hidden' }}>
      {/* Agent List — collapsible */}
      <div style={{ background: '#16213e', borderRadius: 6, padding: 8, flexShrink: 0 }}>
        <h3
          onClick={() => setAgentsOpen(v => !v)}
          style={{ fontSize: 13, marginBottom: agentsOpen ? 6 : 0, color: '#4d96ff', cursor: 'pointer', userSelect: 'none', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
        >
          <span>Agents ({agents.filter(a => a.is_alive).length})</span>
          <span style={{ fontSize: 11, color: '#666' }}>{agentsOpen ? '▼' : '▶'}</span>
        </h3>
        {agentsOpen && (
          <div style={{ maxHeight: '35vh', overflow: 'auto' }}>
            {agents.map((a) => (
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
                  <span style={{ fontWeight: 'bold', color: colorMap[a.name] || '#fff' }}>{a.display_name || a.name}</span>
                  <span style={{ color: '#888' }}>{a.agent_type === 'system' ? '⚙' : '●'}</span>
                </div>
                <NeedBar label="E" value={a.energy} color="#6bcb77" />
                <NeedBar label="K" value={a.knowledge} color="#4d96ff" />
                <NeedBar label="I" value={a.influence} color="#ffd93d" />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Selected Agent Detail */}
      {selectedAgent && detail && (
        <div style={{ background: '#16213e', borderRadius: 6, padding: 8, flexShrink: 0 }}>
          <h3 style={{ fontSize: 13, marginBottom: 6, color: '#4d96ff' }}>{displayNameMap[selectedAgent] || selectedAgent}</h3>
          <pre style={{ fontSize: 10, whiteSpace: 'pre-wrap', color: '#ccc', lineHeight: 1.4, maxHeight: 120, overflow: 'auto' }}>{detail}</pre>
        </div>
      )}

      {/* Selected Landmark Detail */}
      {selectedLandmark && (() => {
        const lm = landmarks.find(l => l.name === selectedLandmark)
        if (!lm) return null
        return (
          <div style={{ background: '#16213e', borderRadius: 6, padding: 8, flexShrink: 0 }}>
            <h3 style={{ fontSize: 13, marginBottom: 4, color: '#4d96ff' }}>{lm.display_name || lm.name}</h3>
            <div style={{ fontSize: 11, color: '#888', marginBottom: 4 }}>{lm.tagline}</div>
            <div style={{ fontSize: 10, color: lm.is_open ? '#6bcb77' : '#ff6b6b', marginBottom: 4 }}>{lm.is_open ? '开放' : '关闭'} · {lm.category}</div>
            {lm.description && <div style={{ fontSize: 10, color: '#ccc', lineHeight: 1.4, marginBottom: 4 }}>{lm.description}</div>}
            {lm.folklore && <div style={{ fontSize: 10, color: '#aaa', lineHeight: 1.4, fontStyle: 'italic', marginBottom: 4 }}>「{lm.folklore}」</div>}
            {lm.fun_fact && <div style={{ fontSize: 10, color: '#ffd93d', lineHeight: 1.4 }}>💡 {lm.fun_fact}</div>}
            {lm.location_gated_tools.length > 0 && (
              <div style={{ fontSize: 10, color: '#666', marginTop: 4 }}>可用工具: {lm.location_gated_tools.length} 个</div>
            )}
          </div>
        )
      })()}

      {/* Conversations — fills remaining space, always visible */}
      <div style={{ background: '#16213e', borderRadius: 6, padding: 8, flex: 1, overflow: 'auto', minHeight: 0 }}>
        <h3 style={{ fontSize: 13, marginBottom: 6, color: '#4d96ff', position: 'sticky', top: 0, background: '#16213e', paddingBottom: 4 }}>
          Conversations
        </h3>
        <div
          style={{ fontSize: 10, whiteSpace: 'pre-wrap', color: '#aaa', lineHeight: 1.4 }}
          dangerouslySetInnerHTML={{ __html: convos ? colorize(convos, colorMap, displayNameMap) : '(暂无对话)' }}
        />
      </div>
    </div>
  )
}
