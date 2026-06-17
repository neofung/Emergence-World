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
