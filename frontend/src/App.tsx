import { Routes, Route } from 'react-router-dom'
import { PaginaInicial } from './pages/PaginaInicial'
import { Login } from './pages/Login'
import { MuralAvisos } from './pages/MuralAvisos'
import { TermoDeUso } from './pages/TermoDeUso'
import { PoliticaDePrivacidade } from './pages/PoliticaDePrivacidade'
import { EsqueciSenha } from './pages/EsqueciSenha'
import { RedefinirSenha } from './pages/RedefinirSenha'
import { ProtectedRoute } from './routes/ProtectedRoute'

function App() {
  return (
    <Routes>
      <Route path="/" element={<PaginaInicial />} />
      <Route path="/login" element={<Login />} />
      <Route path="/termo-de-uso" element={<TermoDeUso />} />
      <Route path="/politica-de-privacidade" element={<PoliticaDePrivacidade />} />
      <Route path="/esqueci-senha" element={<EsqueciSenha />} />
      <Route path="/redefinir-senha" element={<RedefinirSenha />} />
      <Route
        path="/mural"
        element={
          <ProtectedRoute>
            <MuralAvisos />
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}

export default App
