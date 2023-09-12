chart_json='''
{
  "Line": {
    "name": "Line",
    "alias": ["Lines"],
    "def": "A line chart uses lines with segments to show changes in data in a ordinal dimension.",
    "purpose": ["Comparison", "Trend", "Anomaly"],
    "coord": ["Cartesian2D"],
    "category": ["Statistic"],
    "shape": ["Lines"],
    "channel": ["Position", "Direction"],
  },
  "Column": {
    "name": "Column",
    "alias": ["Columns"],
    "def": "A column chart uses series of columns to display the value of the dimension. The horizontal axis shows the classification dimension and the vertical axis shows the corresponding value.",
    "purpose": ["Comparison", "Distribution", "Rank"],
    "coord": ["Cartesian2D"],
    "category": ["Statistic"],
    "shape": ["Bars"],
    "channel": ["Position", "Color"],
  },
  "Bar": {
    "name": "Bar",
    "alias": ["Bars"],
    "def": "A bar chart uses series of bars to display the value of the dimension. The vertical axis shows the classification dimension and the horizontal axis shows the corresponding value.",
    "purpose": ["Comparison", "Distribution", "Rank"],
    "shape": ["Bars"],
    "dataPres": [
      {
        "minQty": 1,
        "maxQty": 2,
        "fieldConditions": ["Nominal", "Ordinal"]
      },
      {
        "minQty": 1,
        "maxQty": 1,
        "fieldConditions": ["Interval"]
      }
    ],
    "channel": ["Position", "Color"],
  },
  "Pie": {
    "name": "Pie",
    "alias": ["Circle Chart", "Pie"],
    "def": "A pie chart is a chart that the classification and proportion of data are represented by the color and arc length (angle, area) of the sector.",
    "purpose": ["Comparison", "Composition", "Proportion"],
    "coord": ["Polar"],
    "dataPres": [
      {
        "minQty": 1,
        "maxQty": 1,
        "fieldConditions": ["Nominal", "Ordinal"]
      },
      {
        "minQty": 1,
        "maxQty": 1,
        "fieldConditions": ["Interval"]
      }
    ],
    "channel": ["Angle", "Area", "Color"],
    "recRate": "Use with Caution"
  },
  "Area": {
    "name": "Area",
    "alias": [],
    "def": "An area chart uses series of line segments with overlapped areas to show the change in data in a ordinal dimension.",
    "purpose": ["Comparison", "Trend", "Anomaly"],
    "shape": ["Area"],
    "channel": ["Color", "Position"],
  },
  "Scatter": {
    "name": "Scatter",
    "alias": ["Scatter Chart", "Scatterplot"],
    "def": "A scatter plot is a type of plot or mathematical diagram using Cartesian coordinates to display values for typically two variables for series of data.",
    "purpose": ["Comparison", "Distribution", "Anomaly"],
    "shape": ["Scatter"],
    "channel": ["Color", "Position"],
  },
  "Bullet": {
    "name": "Bullet",
    "alias": ["Bullet Chart", "Performance Chart"],
    "def": "A bullet chart is a variation of a bar graph developed to replace dashboard gauges and meters. It is used primarily to compare a single measure to some pre-defined thresholds or to another measure.",
    "purpose": ["Comparison", "Benchmark", "Performance"],
    "coord": ["Cartesian2D"],
    "category": ["Statistic"],
    "shape": ["Bar", "Tick"],
    "channel": ["Position", "Length", "Color"],
  }
}'''