import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import ExportPage from './pages/ExportPage'
import ReviewPage from './pages/ReviewPage'
import TemplatePage from './pages/TemplatePage'
import UploadPage from './pages/UploadPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<UploadPage />} />
        <Route path="review/:videoId" element={<ReviewPage />} />
        <Route path="template/:videoId" element={<TemplatePage />} />
        <Route path="export/:videoId" element={<ExportPage />} />
      </Route>
    </Routes>
  )
}

export default App
