import type { Agent, Landmark, SimStatus, ConsoleResponse } from './types'

const BASE = '/api/v1'

export async function fetchAgents(): Promise<Agent[]> {
  const res = await fetch(`${BASE}/agents`)
  return res.json()
}

export async function fetchLandmarks(): Promise<Landmark[]> {
  const res = await fetch(`${BASE}/landmarks`)
  return res.json()
}

export async function fetchSimStatus(): Promise<SimStatus> {
  const res = await fetch(`${BASE}/simulation/status`)
  return res.json()
}

export async function startSim(): Promise<unknown> {
  const res = await fetch(`${BASE}/simulation/start`, { method: 'POST' })
  return res.json()
}

export async function pauseSim(): Promise<unknown> {
  const res = await fetch(`${BASE}/simulation/pause`, { method: 'POST' })
  return res.json()
}

export async function resumeSim(): Promise<unknown> {
  const res = await fetch(`${BASE}/simulation/resume`, { method: 'POST' })
  return res.json()
}

export async function stopSim(): Promise<unknown> {
  const res = await fetch(`${BASE}/simulation/stop`, { method: 'POST' })
  return res.json()
}

export async function fetchConversations(): Promise<ConsoleResponse> {
  const res = await fetch(`${BASE}/console/conversations`)
  return res.json()
}

export async function fetchAgentDetail(name: string): Promise<ConsoleResponse> {
  const res = await fetch(`${BASE}/console/agent/${encodeURIComponent(name)}`)
  return res.json()
}
