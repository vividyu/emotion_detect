import React, { useState, useEffect } from 'react';
import EmotionChart from './components/EmotionChart';
import EmotionTable from './components/EmotionTable';
import EmotionStats from './components/EmotionStats';
import axios from 'axios';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001';

// 情绪英中文映射
const EMOTION_LABELS = {
  'Neutral': '中性',
  'Happy': '快乐',
  'Sad': '悲伤',
  'Surprise': '惊讶',
  'Fear': '恐惧',
  'Disgust': '厌恶',
  'Anger': '愤怒',
  'Contempt': '轻蔑'
};

function App() {
  const [emotions, setEmotions] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedEmotion, setSelectedEmotion] = useState('all');

  // 加载数据
  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      // 获取所有情绪数据
      const emotionsResponse = await axios.get(`${API_BASE_URL}/api/emotions`);
      setEmotions(emotionsResponse.data.data);

      // 获取统计数据
      const statsResponse = await axios.get(`${API_BASE_URL}/api/emotions/stats`);
      setStats(statsResponse.data.data);

      console.log('Data loaded successfully:', {
        emotions: emotionsResponse.data.data.length,
        stats: statsResponse.data.data
      });
    } catch (err) {
      console.error('Error loading data:', err);
      setError(err.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  // 自动加载数据
  useEffect(() => {
    loadData();
  }, []);

  // 过滤数据
  const filteredEmotions = selectedEmotion === 'all' 
    ? emotions 
    : emotions.filter(e => e.emotionName === selectedEmotion);

  // 获取唯一的情绪类别
  const uniqueEmotions = [...new Set(emotions.map(e => e.emotionName))];

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎭 情绪检测可视化系统</h1>
        <p>Emotion Detection Visualization Dashboard</p>
      </header>

      <main className="App-main">
        {/* 控制面板 */}
        <div className="control-panel">
          <button 
            onClick={loadData} 
            disabled={loading}
            className="btn btn-primary"
          >
            {loading ? '加载中...' : '🔄 重新加载数据'}
          </button>

          <div className="filter-group">
            <label htmlFor="emotion-filter">筛选情绪：</label>
            <select 
              id="emotion-filter"
              value={selectedEmotion}
              onChange={(e) => setSelectedEmotion(e.target.value)}
              className="emotion-select"
            >
              <option value="all">全部</option>
              {uniqueEmotions.map(emotion => (
                <option key={emotion} value={emotion}>
                  {EMOTION_LABELS[emotion] || emotion}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="error-message">
            ⚠️ 错误：{error}
            <button onClick={loadData} className="btn-link">重试</button>
          </div>
        )}

        {/* 统计信息 */}
        {stats && <EmotionStats stats={stats} />}

        {/* 图表显示 */}
        {filteredEmotions.length > 0 && (
          <div className="chart-container">
            <h2>Valence & Arousal 时间序列</h2>
            <EmotionChart data={filteredEmotions} />
          </div>
        )}

        {/* 数据表格 */}
        {filteredEmotions.length > 0 && (
          <div className="table-container">
            <h2>详细数据</h2>
            <EmotionTable data={filteredEmotions} />
          </div>
        )}

        {/* 空数据提示 */}
        {!loading && emotions.length === 0 && (
          <div className="empty-state">
            <p>📭 暂无数据</p>
            <p className="hint">
              请确保后端服务器正在运行，并且 results 目录中有 JSON 文件。
            </p>
          </div>
        )}
      </main>

      <footer className="App-footer">
        <p>
          数据来源：情绪检测系统 | 
          记录数：{filteredEmotions.length} / {emotions.length}
        </p>
      </footer>
    </div>
  );
}

export default App;
