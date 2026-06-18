import type { SimStatus } from './types'
import * as api from './api'

interface Props {
  status: SimStatus
  onRefresh: () => void
}

export default function ControlPanel({ status, onRefresh }: Props) {
  const btn = (label: string, action: () => Promise<unknown>, color: string) => (
    <button
      onClick={() => action().then(onRefresh)}
      style={{
        padding: '6px 16px',
        border: 'none',
        borderRadius: 4,
        background: color,
        color: '#fff',
        cursor: 'pointer',
        fontWeight: 'bold',
        fontSize: 12,
      }}
    >
      {label}
    </button>
  )

  // Format sim time
  const simTime = status.current_time
    ? new Date(status.current_time).toLocaleString('zh-CN', {
        timeZone: 'America/New_York',
        month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', hour12: false,
      })
    : '--'

  const simHour = status.current_time
    ? new Date(status.current_time).toLocaleString('en-US', { timeZone: 'America/New_York', hour: 'numeric', hour12: true })
    : ''

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: 12,
      padding: '8px 16px',
      background: '#16213e',
      borderRadius: 6,
    }}>
      <span style={{ fontSize: 14, fontWeight: 'bold', color: '#4d96ff' }}>
        Emergence World
      </span>
      <span style={{ color: '#888' }}>Day {status.day_count}/15</span>
      <span style={{ color: '#ccc', fontVariantNumeric: 'tabular-nums' }}>{simTime}</span>
      <span style={{ color: '#666', fontSize: 11 }}>{simHour}</span>
      <span style={{
        padding: '2px 8px',
        borderRadius: 10,
        fontSize: 11,
        background: status.running ? (status.paused ? '#ffd93d' : '#6bcb77') : '#555',
        color: '#000',
      }}>
        {status.running ? (status.paused ? 'PAUSED' : 'RUNNING') : 'STOPPED'}
      </span>
      <div style={{ flex: 1 }} />
      {!status.running && btn('Start', api.startSim, '#6bcb77')}
      {status.running && !status.paused && btn('Pause', api.pauseSim, '#ffd93d')}
      {status.running && status.paused && btn('Resume', api.resumeSim, '#6bcb77')}
      {status.running && btn('Stop', api.stopSim, '#ff6b6b')}
    </div>
  )
}
