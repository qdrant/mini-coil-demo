import PropTypes from 'prop-types';
import Chart from 'chart.js/auto';
import { useEffect, useRef } from 'react';

const Visualization = ({ sentence }) => {
  const canvasRef = useRef(null);
  console.log(sentence);

  const xyValues = [
    {x:50, y:7},
    {x:60, y:8},
    {x:70, y:8},
    {x:80, y:9},
    {x:90, y:9},
    {x:100, y:9},
    {x:110, y:10},
    {x:120, y:11},
    {x:130, y:14},
    {x:140, y:14},
    {x:150, y:15}
  ];

  // let chart;

  useEffect(() => {
    if (!canvasRef.current) {
      return;
    }
    let chart = null;
    const ctx = canvasRef?.current?.getContext("2d");
    if (ctx) {
      chart = new Chart(ctx, {
        type: "scatter",
        data: {
          datasets: [{
            pointRadius: 4,
            pointBackgroundColor: "#b99aff",
            pointBorderColor: "#8547ff",
            data: xyValues
          }]
        },
        options:{
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              grid: {
                display: false,
              },
              display: false,
            },
            y: {
              display: false,
            },
          },
        }
      });
    }
    return () => {
      chart?.destroy();
    };
  }, []);

  return (
      <canvas ref={canvasRef}></canvas>
  )
}

Visualization.propTypes = {
  sentence: PropTypes.string.isRequired,
};

export default Visualization;