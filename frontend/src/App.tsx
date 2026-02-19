import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import Footer from './components/Footer'
import Home from './pages/Home'
import Files from './pages/Files'

function App() {
  return (
    <Router>
      <div className="flex flex-col h-screen overflow-hidden">
        <Header />
        <main className="flex-grow overflow-auto">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/files" element={<Files />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  )
}

export default App
