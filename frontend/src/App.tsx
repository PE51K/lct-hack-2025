import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import CalculatorChat from './components/CalculatorChat';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/chat/calculator" replace />} />
        <Route path="/chat/calculator" element={<CalculatorChat />} />
      </Routes>
    </Router>
  );
}

export default App;
