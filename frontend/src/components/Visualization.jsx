import PropTypes from 'prop-types';
import Chart from 'chart.js/auto';
import { useEffect, useRef } from 'react';

const Visualization = ({ selectedWords, word }) => {
  const canvasRef = useRef(null);

  const xyValues = selectedWords.map((wordObj) => {
    return {
      x: wordObj.embedding[0],
      y: wordObj.embedding[1],
      sentence: wordObj.sentence,
    };
  });

  const zwValues = selectedWords.map((wordObj) => {
    return {
      x: wordObj.embedding[2],
      y: wordObj.embedding[3],
      sentence: wordObj.sentence,
    };
  });

  // let chart;

  useEffect(() => {
    if (!canvasRef.current) {
      return;
    }
    let chart = null;
    const ctx = canvasRef?.current?.getContext("2d");
    if (ctx) {
      let datasets = xyValues.length > 0 ? [{
        pointRadius: 4,
        pointBackgroundColor: "#b99aff",
        pointBorderColor: "#8547ff",
        label: word + ":[0,1]",
        data: xyValues
      },
      {
        pointRadius: 4,
        pointBackgroundColor: "#ff8a8a",
        pointBorderColor: "#ff5a5a",
        label: word + ":[2,3]",
        data: zwValues
      }
    ] : [];

      chart = new Chart(ctx, {
        type: "scatter",
        data: {
          datasets
        },
        options: {
          plugins: {
            tooltip: {
              callbacks: {
                label: (context) => {
                  const sentence = context.dataset.data[context.dataIndex].sentence;
                  return sentence;
                }
              }
            }
          },
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              min: -1.2,
              max: 1.2,
              display: true,
              position: 'center',
              grid: {
                display: false
              },
              ticks: {
                display: false
              },
              border: {
                display: true,
                color: '#444444aa',
                drawTicks: false
              },
            },
            y: {
              min: -1.2,
              max: 1.2,
              display: true,
              position: 'center',
              grid: {
                display: false
              },
              ticks: {
                display: false
              },
              border: {
                display: true,
                color: '#444444aa',
                drawTicks: false
              },
            },
          },
        }
      });
    }
    return () => {
      chart?.destroy();
    };
  }, [word, selectedWords]);

  return (
    <canvas ref={canvasRef}></canvas>
  )
}

Visualization.propTypes = {
  selectedWords: PropTypes.array.isRequired,
  word: PropTypes.string,
};

export default Visualization;