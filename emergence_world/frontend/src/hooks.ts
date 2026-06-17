import { useState, useEffect, useCallback } from 'react'
import type { Agent, Landmark, SimStatus, ConsoleResponse } from './types'
import * as api from './api'

export function useAgents(interval = 2000) {
  const [agents, setAgents] = useState<Agent[]>([])
  useEffect(() => {
    const poll = () => api.fetchAgents().then(setAgents)
    poll()
    const id = setInterval(poll, interval)
    return () => clearInterval(id)
  }, [interval])
  return agents
}

export function useLandmarks() {
  const [landmarks, setLandmarks] = useState<Landmark[]>([])
  useEffect(() => {
    api.fetchLandmarks().then(setLandmarks)
  }, [])
  return landmarks
}

export function useSimStatus(interval = 1000) {
  const [status, setStatus] = useState<SimStatus>({ running: false, paused: false, day_count: 0, agents_in_queue: 0, boost_queue: 0 })
  useEffect(() => {
    const poll = () => api.fetchSimStatus().then(setStatus)
    poll()
    const id = setInterval(poll, interval)
    return () => clearInterval(id)
  }, [interval])
  return status
}

export function useConversations(interval = 3000) {
  const [convos, setConvos] = useState('')
  useEffect(() => {
    const poll = () => api.fetchConversations().then(r => setConvos(r.output))
    poll()
    const id = setInterval(poll, interval)
    return () => clearInterval(id)
  }, [interval])
  return convos
}

export function useAgentDetail(name: string | null) {
  const [detail, setDetail] = useState('')
  const refresh = useCallback(() => {
    if (name) api.fetchAgentDetail(name).then(r => setDetail(r.output))
  }, [name])
  useEffect(() => { refresh() }, [refresh])
  return { detail, refresh }
}
