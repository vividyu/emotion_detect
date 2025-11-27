import React, { useRef, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

// 注册 Chart.js 组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

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

function EmotionChart({ data }) {
  const chartRef = useRef(null);

  // 准备图表数据
  const labels = data.map((item, index) => {
    // 使用图像名称作为标签（简化显示）
    return item.image.substring(0, 15);
  });

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Valence (效价)',
        data: data.map(item => item.valence),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        tension: 0.3,
        pointRadius: 4,
        pointHoverRadius: 6,
      },
      {
        label: 'Arousal (唤醒度)',
        data: data.map(item => item.arousal),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        tension: 0.3,
        pointRadius: 4,
        pointHoverRadius: 6,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Valence & Arousal 时间序列变化',
        font: {
          size: 16,
        },
      },
      tooltip: {
        callbacks: {
          title: function(context) {
            const index = context[0].dataIndex;
            return `${data[index].image} (人脸 ${data[index].faceId})`;
          },
          label: function(context) {
            const index = context.dataIndex;
            const emotion = data[index].emotionName;
            const emotionLabel = EMOTION_LABELS[emotion] || emotion;
            return [
              `${context.dataset.label}: ${context.parsed.y.toFixed(3)}`,
              `情绪: ${emotionLabel}`
            ];
          }
        }
      }
    },
    scales: {
      y: {
        min: -1,
        max: 1,
        title: {
          display: true,
          text: '值 (Value)',
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
      },
      x: {
        title: {
          display: true,
          text: '样本索引 (Sample Index)',
        },
        ticks: {
          maxTicksLimit: 20,
          maxRotation: 45,
          minRotation: 45,
        },
      },
    },
  };

  return (
    <div style={{ height: '400px', width: '100%' }}>
      <Line ref={chartRef} data={chartData} options={options} />
    </div>
  );
}

export default EmotionChart;
