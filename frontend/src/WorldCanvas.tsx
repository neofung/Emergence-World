import { useRef, useEffect, useCallback } from 'react'
import type { Agent, Landmark } from './types'

const GRID_SIZE = 240
const SCALE = 2.5  // 1 unit = 2.5px → 600px total
const CANVAS_SIZE = GRID_SIZE * SCALE

const CATEGORY_COLORS: Record<string, string> = {
  residential: '#4a6741',
  commercial: '#6b5b3e',
  municipal: '#3e5a6b',
  recreation: '#2d5a3d',
  entertainment: '#6b3e5a',
  landmark: '#5a5a3e',
}

const AGENT_COLORS = [
  '#ff6b6b', '#ffd93d', '#6bcb77', '#4d96ff', '#ff6bff',
  '#ff9f43', '#a29bfe', '#fd79a8', '#00cec9', '#e17055',
  '#74b9ff', '#55efc4', '#ffeaa7',
]

interface Props {
  landmarks: Landmark[]
  agents: Agent[]
  selectedAgent: string | null
  onSelectAgent: (name: string | null) => void
}

export default function WorldCanvas({ landmarks, agents, selectedAgent, onSelectAgent }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  const draw = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Background
    ctx.fillStyle = '#16213e'
    ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE)

    // Grid
    ctx.strokeStyle = '#1a1a3e'
    ctx.lineWidth = 0.5
    for (let i = 0; i <= GRID_SIZE; i += 20) {
      ctx.beginPath()
      ctx.moveTo(i * SCALE, 0)
      ctx.lineTo(i * SCALE, CANVAS_SIZE)
      ctx.stroke()
      ctx.beginPath()
      ctx.moveTo(0, i * SCALE)
      ctx.lineTo(CANVAS_SIZE, i * SCALE)
      ctx.stroke()
    }

    // Landmarks
    for (const lm of landmarks) {
      const x = lm.position.x * SCALE
      const y = lm.position.y * SCALE
      const size = lm.category === 'residential' ? 8 : 14
      ctx.fillStyle = lm.is_open
        ? (CATEGORY_COLORS[lm.category] || '#555')
        : '#ff4444'
      ctx.fillRect(x - size / 2, y - size / 2, size, size)
      ctx.strokeStyle = lm.is_open ? '#888' : '#ff0000'
      ctx.lineWidth = 1
      ctx.strokeRect(x - size / 2, y - size / 2, size, size)

      // Label
      if (lm.category !== 'residential') {
        ctx.fillStyle = '#aaa'
        ctx.font = '7px monospace'
        ctx.textAlign = 'center'
        ctx.fillText(lm.name, x, y + size / 2 + 9)
      }
    }

    // Agents
    agents.forEach((agent, i) => {
      const x = agent.position.x * SCALE
      const y = agent.position.y * SCALE
      const color = AGENT_COLORS[i % AGENT_COLORS.length]
      const isSelected = agent.name === selectedAgent

      // Glow for selected
      if (isSelected) {
        ctx.beginPath()
        ctx.arc(x, y, 8, 0, Math.PI * 2)
        ctx.fillStyle = color + '40'
        ctx.fill()
      }

      // Agent dot
      ctx.beginPath()
      ctx.arc(x, y, 5, 0, Math.PI * 2)
      ctx.fillStyle = agent.is_alive ? color : '#555'
      ctx.fill()
      ctx.strokeStyle = isSelected ? '#fff' : '#333'
      ctx.lineWidth = isSelected ? 2 : 1
      ctx.stroke()

      // Name
      ctx.fillStyle = '#fff'
      ctx.font = 'bold 8px monospace'
      ctx.textAlign = 'center'
      ctx.fillText(agent.name, x, y - 8)
    })
  }, [landmarks, agents, selectedAgent])

  useEffect(() => { draw() }, [draw])

  const handleClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = canvasRef.current!.getBoundingClientRect()
    const mx = (e.clientX - rect.left)
    const my = (e.clientY - rect.top)

    let closest: string | null = null
    let minDist = 15
    for (const agent of agents) {
      const ax = agent.position.x * SCALE
      const ay = agent.position.y * SCALE
      const dist = Math.sqrt((mx - ax) ** 2 + (my - ay) ** 2)
      if (dist < minDist) {
        minDist = dist
        closest = agent.name
      }
    }
    onSelectAgent(closest)
  }

  return (
    <canvas
      ref={canvasRef}
      width={CANVAS_SIZE}
      height={CANVAS_SIZE}
      onClick={handleClick}
      style={{ border: '1px solid #333', cursor: 'crosshair', borderRadius: 4 }}
    />
  )
}
