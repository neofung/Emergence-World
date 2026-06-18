export interface Agent {
  id: string
  name: string
  display_name: string
  role: string
  agent_type: string
  energy: number
  knowledge: number
  influence: number
  compute_credits: number
  is_alive: boolean
  mood?: string
  position: { x: number; y: number; z: number }
}

export interface Landmark {
  id: string
  name: string
  tagline: string
  category: string
  position: { x: number; y: number; z: number }
  is_open: boolean
  location_gated_tools: string[]
}

export interface SimStatus {
  running: boolean
  paused: boolean
  day_count: number
  agents_in_queue: number
  boost_queue: number
}

export interface ConsoleResponse {
  output: string
}
