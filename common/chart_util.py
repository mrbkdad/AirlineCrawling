import matplotlib.pyplot as plt
import mpld3
from mpld3 import plugins

''' DataFrame 데이터를 입력 받아 라인차트용 D3 스크립트 작성
- DataFrame 데이터 구조
    * X 축 인덱스
    * Y 축은 각 컬럼의 값  - 반드시 수치 사용
    * legend : 각 컬럼명
        인덱스 컬럼1 컬럼2 ...
        201701 1000  2000 ...
        ...
'''
def plot_by_mpld3(dataframe,figsize=(12,6),marker='o',grid=True,
                           alpha_ax=0.3,alpha_plot=0.4,alpha_unsel=0.3,alpha_over=1.5,
                           title=None,xlabel=None,ylabel=None,mode="display",file=None):
    ## DataFrame 데이터를 이용하여 웹용 D3 chart 스크립트 생성
    # plot line + confidence interval
    fig, ax = plt.subplots(figsize=figsize)
    ax.grid(grid, alpha=alpha_ax)

    for key, val in dataframe.iteritems():
        l, = ax.plot(val.index, val.values, label=key, marker=marker)
        ax.plot(val.index,val.values, color=l.get_color(), alpha=alpha_plot)
    # define interactive legend
    handles, labels = ax.get_legend_handles_labels() # return lines and labels
    interactive_legend = plugins.InteractiveLegendPlugin(handles,labels,
                                                         alpha_unsel=alpha_unsel,
                                                         alpha_over=alpha_over, 
                                                         start_visible=True)
    plugins.connect(fig, interactive_legend)

    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, size=len(title)+5)

    ## mode
    if mode == 'html': # return html script
        return mpld3.fig_to_html(fig)
    elif mode == 'save' and file: # save file
        mpld3.save_html(fig,file)
    else: # display chart
        #mpld3.enable_notebook()
        return mpld3.display()