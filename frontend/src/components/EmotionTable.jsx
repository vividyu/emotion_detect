import React, { useState } from 'react';
import './EmotionTable.css';

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

function EmotionTable({ data }) {
  const [sortBy, setSortBy] = useState('index');
  const [sortOrder, setSortOrder] = useState('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;

  // 排序数据
  const sortedData = [...data].sort((a, b) => {
    let aValue, bValue;

    switch (sortBy) {
      case 'valence':
        aValue = a.valence;
        bValue = b.valence;
        break;
      case 'arousal':
        aValue = a.arousal;
        bValue = b.arousal;
        break;
      case 'emotion':
        aValue = a.emotionName;
        bValue = b.emotionName;
        break;
      case 'image':
        aValue = a.image;
        bValue = b.image;
        break;
      default:
        return 0;
    }

    if (sortOrder === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });

  // 分页
  const totalPages = Math.ceil(sortedData.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentData = sortedData.slice(startIndex, endIndex);

  // 排序处理
  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
  };

  // 获取情绪对应的表情符号
  const getEmotionEmoji = (emotion) => {
    const emojiMap = {
      'Happy': '😊',
      'Sad': '😢',
      'Anger': '😠',
      'Fear': '😨',
      'Disgust': '🤢',
      'Surprise': '😲',
      'Neutral': '😐',
      'Contempt': '😏'
    };
    return emojiMap[emotion] || '🎭';
  };

  // 获取效价颜色
  const getValenceColor = (valence) => {
    if (valence > 0.3) return '#4caf50'; // 绿色 - 积极
    if (valence < -0.3) return '#f44336'; // 红色 - 消极
    return '#ff9800'; // 橙色 - 中性
  };

  return (
    <div className="emotion-table-container">
      <div className="table-responsive">
        <table className="emotion-table">
          <thead>
            <tr>
              <th>#</th>
              <th onClick={() => handleSort('image')} className="sortable">
                图像 {sortBy === 'image' && (sortOrder === 'asc' ? '↑' : '↓')}
              </th>
              <th>Face ID</th>
              <th onClick={() => handleSort('emotion')} className="sortable">
                情绪 {sortBy === 'emotion' && (sortOrder === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('valence')} className="sortable">
                Valence {sortBy === 'valence' && (sortOrder === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('arousal')} className="sortable">
                Arousal {sortBy === 'arousal' && (sortOrder === 'asc' ? '↑' : '↓')}
              </th>
              <th>边界框</th>
            </tr>
          </thead>
          <tbody>
            {currentData.map((item, index) => (
              <tr key={startIndex + index}>
                <td>{startIndex + index + 1}</td>
                <td className="image-name" title={item.image}>
                  {item.image.substring(0, 20)}...
                </td>
                <td>{item.faceId}</td>
                <td className="emotion-cell">
                  <span className="emotion-emoji">{getEmotionEmoji(item.emotionName)}</span>
                  {EMOTION_LABELS[item.emotionName] || item.emotionName}
                </td>
                <td 
                  className="valence-cell"
                  style={{ color: getValenceColor(item.valence) }}
                >
                  <strong>{item.valence.toFixed(3)}</strong>
                </td>
                <td className="arousal-cell">
                  {item.arousal.toFixed(3)}
                </td>
                <td className="bbox-cell">
                  [{item.bbox.join(', ')}]
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 分页控件 */}
      {totalPages > 1 && (
        <div className="pagination">
          <button
            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
            className="btn-pagination"
          >
            上一页
          </button>
          <span className="page-info">
            第 {currentPage} / {totalPages} 页
          </span>
          <button
            onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
            disabled={currentPage === totalPages}
            className="btn-pagination"
          >
            下一页
          </button>
        </div>
      )}
    </div>
  );
}

export default EmotionTable;
