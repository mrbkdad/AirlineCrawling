import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from email.header import Header
import logging
from common.log_util import log

## 메일보내기, 멀티 첨부 파일 처리
def email_sender(to, subject, html, attachs=None):
    log(['receiver',to,' ## email -',subject])
    email_user='park363@eastarjet.com'  # 세팅 처리
    email_pwd='bk@813102'
    msg=MIMEMultipart('alternative')
    msg['From']=email_user
    msg['To'] = to
    msg['Subject'] = Header(s=subject, charset="utf-8")
    msg.attach(MIMEText(html, 'html', _charset="utf-8"))

    #첨부파일
    if attachs:
        for attach in attachs:
            part=MIMEBase('application','octet-stream')
            part.set_payload(open(attach, 'rb').read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition','attachment; filename="%s"' % os.path.basename(attach))
            msg.attach(part)

    s = smtplib.SMTP("spam.eastarjet.com", 587)
    s.ehlo()
    #s.starttls()
    #s.ehlo()
    #s.login(email_user, email_pwd)
    s.sendmail(email_user, to, msg.as_string())
    s.close()

def email_multi_sender(to_list,subject,html,attachs=None):
    log('start multi email sender')
    for to in to_list:
        email_sender(to, subject, html, attachs=attachs)
    log('end multi email sender')
## 발송용 html처리
def make_newletter_html(template_dict):
    # html 메시지 생성
    with open('template/newletter.html',encoding='utf-8') as fp:
        template = fp.read()
    ## 수정 및 추가 사항 처리
    template= template.replace('{msg_title1}',template_dict['title1']).replace('{msg_title2}',template_dict['title2'])
    template = template.replace('{msg_date}',template_dict['date']).replace('{msg_auth}',template_dict['auth'])
    template = template.replace('{msg_contents}',template_dict['contents']).replace('\n','')
    return template