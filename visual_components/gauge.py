from random import random

import streamlit as st
import plotly.graph_objects as go

class BaseGauge:

    def __init__(self):
        pass


class Gauge:
    def __init__(self,):
        pass


class GaugeGraph:
    def __init__(self,in_title = None, in_value = None):
        self.title = in_title
        self.value = in_value

    def in_title(self, in_title):
        self.title = in_title
        return self

    def in_value(self, in_value):
        self.value = in_value
        return self

    def create_gauge(self):
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=self.value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': self.title},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "red" if self.value < 50 else ("yellow" if 50 < self.value < 90 else "green")},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 90], 'color': "gray"},
                    {'range': [90, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 2},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))

        fig.update_layout(
            margin=dict(l=20, r=20, t=50, b=0),
            height=250,
        )

        st.plotly_chart(fig, width='content', key=f"{self.title}_{self.value}_{random()}")

class GaugeGraphLinked(GaugeGraph):

    def __init__(self,in_title = None, in_value = None, page_path = None, label=None):
        super().__init__(in_title, in_value)
        self.page_path = page_path
        self.label = label

    def create_gauge(self):
        page_name = self.page_path.replace("pages/", "").replace(".py", "")

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=self.value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': self.label, 'font': {'size': 14}},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "red" if self.value < 50 else ("yellow" if 50 < self.value < 90 else "green")},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 90], 'color': "gray"},
                    {'range': [90, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 2},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))

        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=0),
            height=250,
        )
        #st.page_link(self.page_path, label="להצגת ישוב")
        st.plotly_chart(fig, width='content', key=f"{self.title}_{self.value}_{random()}")



class GaugePane():
    def __init__(self,in_title = None, in_value = None, page_path = None):
        super().__init__()
        self.title = in_title
        self.value = in_value
        self.page_path = page_path

