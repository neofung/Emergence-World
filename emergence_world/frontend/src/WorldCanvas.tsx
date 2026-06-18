import { useRef, useEffect, useCallback, useState } from 'react'
import type { Agent, Landmark } from './types'
import { AGENT_COLORS } from './colors'

const GRID_SIZE = 240
const ZOOM_MIN = 0.5
const ZOOM_MAX = 10

const CATEGORY_COLORS: Record<string, string> = {
  residential: '#4a6741',
  commercial: '#6b5b3e',
  municipal: '#3e5a6b',
  recreation: '#2d5a3d',
  entertainment: '#6b3e5a',
  landmark: '#5a5a3e',
}

const zoomBtnStyle: React.CSSProperties = {
  width: 22, height: 22, border: 'none', borderRadius: 4,
  background: '#2a2a4e', color: '#fff', fontSize: 14,
  cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
  padding: 0, lineHeight: 1,
}

interface Props {
  landmarks: Landmark[]
  agents: Agent[]
  selectedAgent: string | null
  onSelectAgent: (name: string | null) => void
}

export default function WorldCanvas({ landmarks, agents, selectedAgent, onSelectAgent }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [canvasSize, setCanvasSize] = useState({ w: 600, h: 600 })
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const [dragging, setDragging] = useState(false)
  const dragRef = useRef<{ startX: number; startY: number; panX: number; panY: number; moved: boolean } | null>(null)

  // Observe container size
  useEffect(() => {
    const el = containerRef.current
    if (!el) return
    const ro = new ResizeObserver((entries) => {
      const { width, height } = entries[0].contentRect
      setCanvasSize({ w: Math.floor(width), h: Math.floor(height) })
    })
    ro.observe(el)
    return () => ro.disconnect()
  }, [])

  const draw = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const dpr = window.devicePixelRatio || 1
    const { w: cssW, h: cssH } = canvasSize
    canvas.width = cssW * dpr
    canvas.height = cssH * dpr
    canvas.style.width = `${cssW}px`
    canvas.style.height = `${cssH}px`
    ctx.scale(dpr, dpr)

    const baseScale = Math.min(cssW, cssH) / GRID_SIZE
    const offsetX = (cssW - GRID_SIZE * baseScale) / 2
    const offsetY = (cssH - GRID_SIZE * baseScale) / 2

    // Background
    ctx.fillStyle = '#16213e'
    ctx.fillRect(0, 0, cssW, cssH)

    // Apply zoom + pan
    ctx.save()
    ctx.translate(pan.x + offsetX, pan.y + offsetY)
    ctx.scale(zoom, zoom)

    // Grid
    const worldPx = GRID_SIZE * baseScale
    ctx.strokeStyle = '#1a1a3e'
    ctx.lineWidth = 0.5 / zoom
    for (let i = 0; i <= GRID_SIZE; i += 20) {
      ctx.beginPath()
      ctx.moveTo(i * baseScale, 0)
      ctx.lineTo(i * baseScale, worldPx)
      ctx.stroke()
      ctx.beginPath()
      ctx.moveTo(0, i * baseScale)
      ctx.lineTo(worldPx, i * baseScale)
      ctx.stroke()
    }

    // Landmarks — draw markers first, collect labels
    const lmLabels: { x: number; y: number; text: string; color: string; font: string }[] = []
    for (const lm of landmarks) {
      const x = lm.position.x * baseScale
      const y = lm.position.y * baseScale
      const sz = (lm.category === 'residential' ? 8 : 14) * (baseScale / 2.5)
      ctx.fillStyle = lm.is_open
        ? (CATEGORY_COLORS[lm.category] || '#555')
        : '#ff4444'
      ctx.fillRect(x - sz / 2, y - sz / 2, sz, sz)
      ctx.strokeStyle = lm.is_open ? '#888' : '#ff0000'
      ctx.lineWidth = 1 / zoom
      ctx.strokeRect(x - sz / 2, y - sz / 2, sz, sz)

      if (lm.category !== 'residential') {
        const fontSize = Math.max(7, 7 * baseScale / 2.5)
        const font = `${fontSize}px monospace`
        const text = lm.display_name || lm.name
        lmLabels.push({ x, y: y + sz / 2 + Math.max(9, 9 * baseScale / 2.5), text, color: '#aaa', font })
      }
    }

    // Agents — draw dots first, collect labels
    const agentLabels: { x: number; y: number; text: string; color: string; font: string }[] = []
    agents.forEach((agent, i) => {
      const x = agent.position.x * baseScale
      const y = agent.position.y * baseScale
      const color = AGENT_COLORS[i % AGENT_COLORS.length]
      const isSelected = agent.name === selectedAgent
      const dotR = 5 * (baseScale / 2.5)

      if (isSelected) {
        ctx.beginPath()
        ctx.arc(x, y, dotR * 1.6, 0, Math.PI * 2)
        ctx.fillStyle = color + '40'
        ctx.fill()
      }

      ctx.beginPath()
      ctx.arc(x, y, dotR, 0, Math.PI * 2)
      ctx.fillStyle = agent.is_alive ? color : '#555'
      ctx.fill()
      ctx.strokeStyle = isSelected ? '#fff' : '#333'
      ctx.lineWidth = (isSelected ? 2 : 1) / zoom
      ctx.stroke()

      const fontSize = Math.max(8, 8 * baseScale / 2.5)
      const font = `bold ${fontSize}px monospace`
      const text = agent.display_name || agent.name
      agentLabels.push({ x, y: y - dotR - 2, text, color: '#fff', font })
    })

    // Resolve label collisions with iterative repulsion
    const allLabels = [...lmLabels, ...agentLabels]
    type LabelRect = { x: number; y: number; w: number; h: number; anchorX: number; anchorY: number; label: typeof allLabels[0] }
    const rects: LabelRect[] = allLabels.map(label => {
      ctx.font = label.font
      const textW = ctx.measureText(label.text).width
      const fontSize = parseFloat(label.font.split(' ').find(s => s.endsWith('px'))!) || 8
      const textH = fontSize * 1.2
      return {
        x: label.x - textW / 2 - 2,
        y: label.y - textH,
        w: textW + 4,
        h: textH + 2,
        anchorX: label.x,
        anchorY: label.y,
        label,
      }
    })

    // Iterative repulsion — push overlapping labels apart
    const maxIter = 30
    const maxDrift = 60 // max px a label can drift from its anchor
    for (let iter = 0; iter < maxIter; iter++) {
      let moved = false
      for (let i = 0; i < rects.length; i++) {
        for (let j = i + 1; j < rects.length; j++) {
          const a = rects[i], b = rects[j]
          const overlapX = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x)
          const overlapY = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y)
          if (overlapX > 0 && overlapY > 0) {
            moved = true
            if (overlapX < overlapY) {
              const push = overlapX / 2 + 1
              const dir = (a.x + a.w / 2) < (b.x + b.w / 2) ? -1 : 1
              a.x += dir * push
              b.x -= dir * push
            } else {
              const push = overlapY / 2 + 1
              const dir = (a.y + a.h / 2) < (b.y + b.h / 2) ? -1 : 1
              a.y += dir * push
              b.y -= dir * push
            }
          }
        }
      }
      // Clamp drift so labels stay near their anchors
      for (const r of rects) {
        const cx = r.x + r.w / 2
        const cy = r.y + r.h / 2
        const dx = cx - r.anchorX
        const dy = cy - r.anchorY
        const dist = Math.sqrt(dx * dx + dy * dy)
        if (dist > maxDrift) {
          const scale = maxDrift / dist
          r.x = r.anchorX + dx * scale - r.w / 2
          r.y = r.anchorY + dy * scale - r.h / 2
        }
      }
      if (!moved) break
    }

    // Draw all labels
    for (const r of rects) {
      ctx.fillStyle = r.label.color
      ctx.font = r.label.font
      ctx.textAlign = 'center'
      ctx.fillText(r.label.text, r.x + r.w / 2, r.y + r.h - 2)
    }

    ctx.restore()
  }, [landmarks, agents, selectedAgent, canvasSize, zoom, pan])

  useEffect(() => { draw() }, [draw])

  // Zoom with mouse wheel
  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault()
    const rect = canvasRef.current!.getBoundingClientRect()
    const mx = e.clientX - rect.left
    const my = e.clientY - rect.top

    setZoom(prev => {
      const factor = e.deltaY < 0 ? 1.15 : 1 / 1.15
      const next = Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, prev * factor))
      // Zoom towards mouse position
      const ratio = next / prev
      setPan(p => ({
        x: mx - ratio * (mx - p.x),
        y: my - ratio * (my - p.y),
      }))
      return next
    })
  }, [])

  // Pan with mouse drag
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button !== 0) return
    dragRef.current = { startX: e.clientX, startY: e.clientY, panX: pan.x, panY: pan.y, moved: false }
    setDragging(true)
  }, [pan])

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!dragRef.current) return
    const dx = e.clientX - dragRef.current.startX
    const dy = e.clientY - dragRef.current.startY
    if (Math.abs(dx) > 3 || Math.abs(dy) > 3) dragRef.current.moved = true
    setPan({
      x: dragRef.current.panX + dx,
      y: dragRef.current.panY + dy,
    })
  }, [])

  const handleMouseUp = useCallback(() => {
    // Delay clearing so click handler can detect a drag
    setTimeout(() => { dragRef.current = null }, 0)
    setDragging(false)
  }, [])

  // Click to select agent (only if not dragging)
  const handleClick = useCallback((e: React.MouseEvent) => {
    if (dragRef.current?.moved) return

    const rect = canvasRef.current!.getBoundingClientRect()
    const baseScale = Math.min(canvasSize.w, canvasSize.h) / GRID_SIZE
    const offsetX = (canvasSize.w - GRID_SIZE * baseScale) / 2
    const offsetY = (canvasSize.h - GRID_SIZE * baseScale) / 2
    const mx = (e.clientX - rect.left - pan.x - offsetX) / zoom
    const my = (e.clientY - rect.top - pan.y - offsetY) / zoom

    let closest: string | null = null
    let minDist = 15 * (baseScale / 2.5)
    for (const agent of agents) {
      const ax = agent.position.x * baseScale
      const ay = agent.position.y * baseScale
      const dist = Math.sqrt((mx - ax) ** 2 + (my - ay) ** 2)
      if (dist < minDist) {
        minDist = dist
        closest = agent.name
      }
    }
    onSelectAgent(closest)
  }, [agents, onSelectAgent, canvasSize, zoom, pan])

  // Zoom helpers
  const zoomTo = useCallback((target: number, center?: { x: number; y: number }) => {
    const clamped = Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, target))
    if (center) {
      const ratio = clamped / zoom
      setPan(p => ({
        x: center.x - ratio * (center.x - p.x),
        y: center.y - ratio * (center.y - p.y),
      }))
    }
    setZoom(clamped)
  }, [zoom])

  // Double-click to reset view
  const handleDoubleClick = useCallback(() => {
    setZoom(1)
    setPan({ x: 0, y: 0 })
  }, [])

  // Slider: map y-position to zoom (log scale)
  const sliderToZoom = useCallback((t: number) => ZOOM_MIN * (ZOOM_MAX / ZOOM_MIN) ** t, [])
  const zoomToSlider = useCallback((z: number) => Math.log(z / ZOOM_MIN) / Math.log(ZOOM_MAX / ZOOM_MIN), [])

  const handleSliderClick = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const t = 1 - (e.clientY - rect.top) / rect.height // top = max zoom
    zoomTo(sliderToZoom(Math.max(0, Math.min(1, t))))
  }, [zoomTo, sliderToZoom])

  return (
    <div ref={containerRef} style={{ flex: 1, minWidth: 0, minHeight: 0, position: 'relative', overflow: 'hidden' }}>
      <canvas
        ref={canvasRef}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onClick={handleClick}
        onDoubleClick={handleDoubleClick}
        style={{ border: '1px solid #333', cursor: dragging ? 'grabbing' : 'crosshair', borderRadius: 4 }}
      />

      {/* Zoom controls — bottom-right corner */}
      <div style={{
        position: 'absolute', right: 8, bottom: 8,
        display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2,
        background: 'rgba(22,33,62,0.85)', borderRadius: 6, padding: '6px 4px',
        border: '1px solid #333', userSelect: 'none',
      }}>
        {/* + button */}
        <button
          onClick={() => zoomTo(zoom * 1.3)}
          style={zoomBtnStyle}
          title="Zoom in"
        >+</button>

        {/* Slider track */}
        <div
          onClick={handleSliderClick}
          style={{
            width: 6, height: 100, background: '#2a2a4e', borderRadius: 3,
            position: 'relative', cursor: 'pointer', margin: '4px 0',
          }}
        >
          {/* Fill */}
          <div style={{
            position: 'absolute', bottom: 0, width: '100%',
            height: `${zoomToSlider(zoom) * 100}%`,
            background: '#4d96ff', borderRadius: 3,
          }} />
          {/* Thumb */}
          <div style={{
            position: 'absolute',
            bottom: `${zoomToSlider(zoom) * 100}%`,
            left: '50%', transform: 'translate(-50%, 50%)',
            width: 14, height: 14, background: '#fff', borderRadius: '50%',
            border: '2px solid #4d96ff', boxShadow: '0 0 4px rgba(0,0,0,0.5)',
          }} />
        </div>

        {/* - button */}
        <button
          onClick={() => zoomTo(zoom / 1.3)}
          style={zoomBtnStyle}
          title="Zoom out"
        >−</button>

        {/* Percentage label */}
        <div style={{ fontSize: 10, color: '#aaa', marginTop: 2 }}>{(zoom * 100).toFixed(0)}%</div>

        {/* Reset button */}
        <button
          onClick={handleDoubleClick}
          style={{ ...zoomBtnStyle, fontSize: 9, width: 22, height: 18, marginTop: 2 }}
          title="Reset view"
        >1:1</button>
      </div>
    </div>
  )
}
