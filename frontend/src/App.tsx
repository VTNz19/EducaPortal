import { Routes, Route } from 'react-router-dom'
import { PaginaInicial } from './pages/PaginaInicial'
import { Login } from './pages/Login'
import { MuralAvisos } from './pages/MuralAvisos'
import { PainelSecretaria } from './pages/PainelSecretaria'
import { PerfilUsuario } from './pages/PerfilUsuario'
import { TermoDeUso } from './pages/TermoDeUso'
import { PoliticaDePrivacidade } from './pages/PoliticaDePrivacidade'
import { EsqueciSenha } from './pages/EsqueciSenha'
import { RedefinirSenha } from './pages/RedefinirSenha'
import { ProtectedRoute } from './routes/ProtectedRoute'
import { PlanoDeRetencao } from './pages/PlanoDeRetencao'
import { AceiteTermos } from './pages/AceiteTermos'


function App() {
  return (
    <Routes>
      <Route path="/" element={<PaginaInicial />} />
      <Route path="/login" element={<Login />} />
      <Route path="/termo-de-uso" element={<TermoDeUso />} />
      <Route path="/politica-de-privacidade" element={<PoliticaDePrivacidade />} />
      <Route path="/plano-de-retencao" element={<PlanoDeRetencao />} />
      <Route path="/aceite-termos" element={<AceiteTermos />} />
      <Route path="/esqueci-senha" element={<EsqueciSenha />} />
      <Route path="/primeiro-acesso" element={<EsqueciSenha primeiroAcesso />} />
      <Route path="/redefinir-senha" element={<RedefinirSenha />} />
      <Route
        path="/mural"
        element={
          <ProtectedRoute>
            <MuralAvisos />
          </ProtectedRoute>
        }
      />
      <Route
        path="/secretaria"
        element={
          <ProtectedRoute papeis={['secretaria', 'direcao']}>
            <PainelSecretaria />
          </ProtectedRoute>
        }
      />
      <Route
        path="/secretaria/usuarios/:id"
        element={
          <ProtectedRoute papeis={['secretaria', 'direcao']}>
            <PerfilUsuario />
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}

export default App
