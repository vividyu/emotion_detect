import React from 'react';
import './EmotionStats.css';

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

function EmotionStats({ stats }) {
  // 获取情绪分布的百分比
  const getEmotionPercentages = () => {
    const total = stats.totalRecords;
    return Object.entries(stats.emotionDistribution).map(([emotion, count]) => ({
      emotion,
      emotionLabel: EMOTION_LABELS[emotion] || emotion,
      count,
      percentage: ((count / total) * 100).toFixed(1)
    }));
  };

  const emotionPercentages = getEmotionPercentages();

  // 情绪颜色映射
  const emotionColors = {
    'Happy': '#4caf50',
    'Sad': '#2196f3',
    'Anger': '#f44336',
    'Fear': '#9c27b0',
    'Disgust': '#795548',
    'Surprise': '#ff9800',
    'Neutral': '#9e9e9e',
    'Contempt': '#607d8b'
  };

  return (
    <div className="emotion-stats">
      <h2>📊 统计信息</h2>
      
      <div className="stats-grid">
        {/* 总记录数 */}
        <div className="stat-card">
          <div className="stat-label">总记录数</div>
          <div className="stat-value">{stats.totalRecords}</div>
        </div>

        {/* 平均效价 */}
        <div className="stat-card">
          <div className="stat-label">平均 Valence</div>
          <div className="stat-value" style={{ 
            color: stats.averageValence > 0 ? '#4caf50' : '#f44336' 
          }}>
            {stats.averageValence.toFixed(3)}
          </div>
          <div className="stat-desc">
            {stats.averageValence > 0 ? '偏积极 ↑' : '偏消极 ↓'}
          </div>
        </div>

        {/* 平均唤醒度 */}
        <div className="stat-card">
          <div className="stat-label">平均 Arousal</div>
          <div className="stat-value">
            {stats.averageArousal.toFixed(3)}
          </div>
          <div className="stat-desc">
            {stats.averageArousal > 0 ? '偏激活 ⚡' : '偏平静 💤'}
          </div>
        </div>
      </div>

      {/* 情绪分布 */}
      <div className="emotion-distribution">
        <h3>情绪分布</h3>
        <div className="distribution-bars">
          {emotionPercentages
            .sort((a, b) => b.count - a.count)
            .map(({ emotion, emotionLabel, count, percentage }) => (
              <div key={emotion} className="distribution-item">
                <div className="distribution-label">
                  <span className="emotion-name">{emotionLabel}</span>
                  <span className="emotion-count">{count} ({percentage}%)</span>
                </div>
                <div className="distribution-bar-container">
                  <div 
                    className="distribution-bar"
                    style={{ 
                      width: `${percentage}%`,
                      backgroundColor: emotionColors[emotion] || '#9e9e9e'
                    }}
                  />
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}

export default EmotionStats;
