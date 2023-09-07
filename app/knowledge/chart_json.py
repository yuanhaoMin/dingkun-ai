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
    "dataPres": [
      {
        "minQty": 1,
        "maxQty": 1,
        "fieldConditions": ["Time", "Ordinal"]
      },
      {
        "minQty": 0,
        "maxQty": 1,
        "fieldConditions": ["Nominal"]
      },
      {
        "minQty": 1,
        "maxQty": 1,
        "fieldConditions": ["Interval"]
      }
    ],
    "channel": ["Position", "Direction"],
    "recRate": "Recommended"
  },
  "Column": {
    "name": "Column",
    "alias": ["Columns"],
    "def": "A column chart uses series of columns to display the value of the dimension. The horizontal axis shows the classification dimension and the vertical axis shows the corresponding value.",
    "purpose": ["Comparison", "Distribution", "Rank"],
    "coord": ["Cartesian2D"],
    "category": ["Statistic"],
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
    "recRate": "Recommended"
  },
  "Bar": {
    "name": "Bar",
    "alias": ["Bars"],
    "def": "A bar chart uses series of bars to display the value of the dimension. The vertical axis shows the classification dimension and the horizontal axis shows the corresponding value.",
    "purpose": ["Comparison", "Distribution", "Rank"],
    "coord": ["Cartesian2D"],
    "category": ["Statistic"],
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
    "recRate": "Recommended"
  },
  "Pie": {
    "name": "Pie",
    "alias": ["Circle Chart", "Pie"],
    "def": "A pie chart is a chart that the classification and proportion of data are represented by the color and arc length (angle, area) of the sector.",
    "purpose": ["Comparison", "Composition", "Proportion"],
    "coord": ["Polar"],
    "category": ["Statistic"],
    "shape": ["Round"],
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
    "coord": ["Cartesian2D"],
    "category": ["Statistic"],
    "shape": ["Area"],
    "dataPres": [
      {
        "minQty": 1,
        "maxQty": 1,
        "fieldConditions": ["Time", "Ordinal"]
      },
      {
        "minQty": 1,
        "maxQty": 1,
        "fieldConditions": ["Interval"]
      },
      {
        "minQty": 0,
        "maxQty": 1,
        "fieldConditions": ["Nominal"]
      }
    ],
    "channel": ["Color", "Position"],
    "recRate": "Recommended"
  },
  "Scatter": {
    "name": "Scatter",
    "alias": ["Scatter Chart", "Scatterplot"],
    "def": "A scatter plot is a type of plot or mathematical diagram using Cartesian coordinates to display values for typically two variables for series of data.",
    "purpose": ["Comparison", "Distribution", "Anomaly"],
    "coord": ["Cartesian2D"],
    "category": ["Statistic"],
    "shape": ["Scatter"],
    "dataPres": [
      {
        "minQty": 2,
        "maxQty": 2,
        "fieldConditions": ["Interval"]
      },
      {
        "minQty": 0,
        "maxQty": 1,
        "fieldConditions": ["Nominal"]
      }
    ],
    "channel": ["Color", "Position"],
    "recRate": "Recommended"
  }
}'''