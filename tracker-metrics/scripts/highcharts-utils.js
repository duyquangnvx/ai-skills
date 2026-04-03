// Highcharts Data Extraction Utilities
// Run via Chrome DevTools evaluate_script tool
// Returns structured JSON of all charts on the current page

(() => {
  function isHighchartsAvailable() {
    return typeof window !== 'undefined' && !!window.Highcharts;
  }

  function collectAllCharts() {
    const charts = [];
    if (window.Highcharts?.charts) {
      for (const chart of window.Highcharts.charts) {
        if (chart) charts.push(chart);
      }
    }
    return charts;
  }

  function serializeChart(chart) {
    return {
      title: chart.title?.textStr || '',
      subtitle: chart.subtitle?.textStr || '',
      categories: chart.xAxis?.[0]?.categories || [],
      series: chart.series.map(s => ({
        name: s.name,
        data: s.options.data || [],
        type: s.type,
        stack: s.options.stack,
        yAxis: s.yAxis?.options?.title?.text || undefined,
        visible: s.visible,
      })),
    };
  }

  function serializeHighcharts(hcCharts) {
    return hcCharts.map(c => serializeChart(c)).filter(Boolean);
  }

  function getHighchartsDataSummary(charts) {
    return {
      totalCharts: charts.length,
      chartTitles: charts.map(c => c.title).filter(Boolean),
      seriesCount: charts.reduce((sum, c) => sum + c.series.length, 0),
      totalDataPoints: charts.reduce((cs, c) =>
        cs + c.series.reduce((ss, s) =>
          ss + (Array.isArray(s.data) ? s.data.length : 0), 0), 0),
    };
  }

  function getAllHighchartsFromWindow() {
    if (!isHighchartsAvailable()) {
      return { error: 'Highcharts not available on this page' };
    }
    const charts = serializeHighcharts(collectAllCharts());
    const summary = getHighchartsDataSummary(charts);
    return { summary, charts };
  }

  return getAllHighchartsFromWindow();
})()
