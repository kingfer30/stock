
# 创建2x2的子图布局（4个独立折线图）
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=("情绪温度趋势", "涨停家数趋势", "连板高度趋势", "亏钱效应趋势"),
    vertical_spacing=0.15,
    horizontal_spacing=0.1
)
# 1. 情绪温度折线图（左上）
fig.add_trace(
    go.Scatter(
        x=filtered_df['Day'],
        y=filtered_df['strong'],
        name='情绪温度',
        mode='lines+markers',
        line=dict(color='#636EFA', width=2),
        marker=dict(size=6)
    ),
    row=1, col=1
)
# 添加警戒线
fig.add_hline(y=75, line_dash="dot", line_color="red", row=1, col=1,
              annotation_text="过热警戒线", annotation_position="top right")
fig.add_hline(y=25, line_dash="dot", line_color="green", row=1, col=1,
              annotation_text="过冷警戒线", annotation_position="bottom right")
fig.update_yaxes(title_text="情绪指数(0-100)", range=[0, 100], row=1, col=1)
# 2. 涨停家数折线图（右上）
fig.add_trace(
    go.Scatter(
        x=filtered_df['Day'],
        y=filtered_df['ztjs'],
        name='涨停家数',
        mode='lines+markers',
        line=dict(color='#00C853', width=2),
        marker=dict(size=6, symbol='diamond')
    ),
    row=1, col=2
)
# 添加活跃警戒线
fig.add_hline(y=50, line_dash="dot", line_color="orange", row=1, col=2,
              annotation_text="情绪活跃线", annotation_position="top right")
fig.update_yaxes(title_text="涨停数量", row=1, col=2)
# 3. 连板高度折线图（左下）
fig.add_trace(
    go.Scatter(
        x=filtered_df['Day'],
        y=filtered_df['lbgd'],
        name='连板高度',
        mode='lines+markers',
        line=dict(color='#FF6D00', width=2, dash='dot'),
        marker=dict(size=7, symbol='triangle-up')
    ),
    row=2, col=1
)
# 添加龙头股识别线
fig.add_hline(y=5, line_dash="dot", line_color="purple", row=2, col=1,
              annotation_text="龙头股阈值", annotation_position="top right")
fig.update_yaxes(title_text="连板天数", row=2, col=1)
# 4. 亏钱效应折线图（右下）
fig.add_trace(
    go.Scatter(
        x=filtered_df['Day'],
        y=filtered_df['df_num'],
        name='亏钱效应',
        mode='lines+markers',
        line=dict(color='#D50000', width=2),
        marker=dict(size=6, symbol='x')
    ),
    row=2, col=2
)
# 添加风险警戒线
fig.add_hline(y=30, line_dash="dot", line_color="brown", row=2, col=2,
              annotation_text="风险警戒线", annotation_position="top right")
fig.update_yaxes(title_text="跌停数量", row=2, col=2)
# 统一设置布局
fig.update_layout(
    height=700,
    showlegend=False,  # 每个图表独立展示，无需图例
    template='plotly_white',
    margin=dict(t=50, b=50),
    hovermode='x unified'
)
fig.update_xaxes(title_text="日期", row=2, col=1)
fig.update_xaxes(title_text="日期", row=2, col=2)
st.plotly_chart(fig, use_container_width=True)