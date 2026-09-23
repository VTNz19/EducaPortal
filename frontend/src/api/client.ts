import axios from 'axios'
import type { InternalAxiosRequestConfig } from 'axios'

const API_URL = 'http://localhost:8000/api/v1'

const api = axios.create({ baseURL: API_URL })


let accessToken: string | null = null

export function setAccessToken(token: string | null) {
    accessToken = token
}

export function getAccessToken() {
    return accessToken
}

export const REFRESH_TOKEN_KEY = 'educaportal:refresh_token'

api.interceptors.request.use((config) => {
    if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`
    }
    return config
})

let renovandoToken: Promise<string | null> | null = null

async function renovarAccessToken(): Promise<string | null> {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
    if (!refreshToken) return null
    try {
        const response = await axios.post(`${API_URL}/auth/refresh/`, { refresh: refreshToken })
        setAccessToken(response.data.access)
        return response.data.access
    } catch {
        localStorage.removeItem(REFRESH_TOKEN_KEY)
        setAccessToken(null)
        return null
    }
}

interface ConfigComRetry extends InternalAxiosRequestConfig {
    _retry?: boolean
}

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const original = error.config as ConfigComRetry | undefined

        if (error.response?.status === 401 && original && !original._retry) {
            original._retry = true
            renovandoToken = renovandoToken ?? renovarAccessToken()
            const novoToken = await renovandoToken
            renovandoToken = null
            if (novoToken) {
                original.headers.Authorization = `Bearer ${novoToken}`
                return api(original)
            }
        }
        return Promise.reject(error)
    }
)

export default api
