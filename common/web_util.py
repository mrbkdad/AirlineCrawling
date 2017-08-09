## Grid tr html 작성
## Grid의 데이터 부분
def make_grid_td(data_list):
    tr_html = '<tr>{}</tr>'
    td_html = '<td>{}</td>'
    return ''.join([tr_html.format(''.join([td_html.format(d) for d in td])) for td in data_list])
## Grid의 헤더 부분
def make_grid_th(column_list):
    tr_html = '<tr>{}</tr>'
    th_html = '<th>{}</th>'
    return tr_html.format(''.join([th_html.format(th) for th in column_list]))
