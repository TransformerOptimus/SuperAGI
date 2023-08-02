import React, {useEffect, useRef} from "react";
import * as echarts from 'echarts';

export const BarGraph = ({data, type, color}) => {
  const chartRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    const chartInstance = echarts.getInstanceByDom(chartRef.current);
    const chart = chartInstance ? chartInstance : echarts.init(chartRef.current);

    const option = {
      color: color,
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      xAxis: {
        type: 'category',
        data: data.map(item => item.name),
        axisLabel: {
          interval: 0,
          rotate: 45,
          color: '#888'
        }
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: function (value) {
            if (value >= 1000) {
              return `${value / 1000}k`;
            } else {
              return value;
            }
          }
        },
        splitLine: {
          lineStyle: {
            color: 'rgba(255, 255, 255, 0.08)'
          }
        }
      },
      series: [{
        data: data.map(item => type === 'tokens_per_call' ? (item.tokens_consumed / item.calls) : item[type]),
        type: 'bar'
      }],
      responsive: true
    };

    chart.setOption(option);

    const resizeObserver = new ResizeObserver(entries => {
      entries.forEach(entry => {
        chart.resize();
      });
    });

    resizeObserver.observe(containerRef.current);

    return () => resizeObserver.disconnect();
  }, [data, type]);

  return (
    <div ref={containerRef} style={{width: '100%', height: '100%'}}>
      <div ref={chartRef} style={{width: '100%', height: '100%'}}></div>
    </div>
  );
}

export default BarGraph;